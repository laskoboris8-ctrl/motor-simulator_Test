import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Motor PI", layout="wide")

# ─── NÁZOV ──────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align: center; color: #FF000F;'>
⚙️ 4-MOTOR PI SIMULATOR
</h1>
""", unsafe_allow_html=True)

# ─── PARAMETRE ──────────────────────────────────────────────────
J_motor = 0.02
J_load = 0.05
J_total = 4 * J_motor + J_load
B = 0.02
Km = 0.8
N_MOT = 4
dt = 0.02

rpm2rads = lambda r: r * 2 * np.pi / 60
rads2rpm = lambda w: w * 60 / (2 * np.pi)

# ─── OVLÁDANIE (VĽAVO) ──────────────────────────────────────────
st.sidebar.markdown("## 🎛️ NASTAVENIE")
st.sidebar.markdown("---")

sp_rpm = st.sidebar.slider("📊 Žiadaná rýchlosť [RPM]", 0, 1300, 600, 50)
kp = st.sidebar.slider("📈 Kp (Zosilnenie)", 0.1, 20.0, 3.0, 0.1)
ti = st.sidebar.slider("⏱️ Ti (Časová konštanta) [s]", 0.05, 5.0, 0.8, 0.05)
t_load = st.sidebar.slider("🔧 Záťaž [N·m]", 0.0, 20.0, 2.0, 0.5)

# ─── SIMULÁCIA ──────────────────────────────────────────────────
def run_simulation(sp_val, kp_val, ti_val, tl_val, duration=10):
    omega = 0.0
    integral_e = 0.0
    
    t_arr = []
    sp_arr = []
    pv_arr = []
    tq_arr = []
    err_arr = []
    
    steps = int(duration / dt)
    
    for step in range(steps):
        SP = rpm2rads(sp_val)
        Ti = max(ti_val, 1e-6)
        
        error = SP - omega
        integral_e += error * dt
        u = kp_val * error + (kp_val / Ti) * integral_e
        
        Tm_each = np.clip(Km * u / N_MOT, -0.5, 15.0)
        T_motor = N_MOT * Tm_each
        
        domega = (T_motor - tl_val - B * omega) / J_total
        omega += domega * dt
        omega = max(0.0, min(omega, rpm2rads(1350)))
        
        t_arr.append(step * dt)
        sp_arr.append(sp_val)
        pv_arr.append(rads2rpm(omega))
        tq_arr.append(Tm_each)
        err_arr.append(rads2rpm(error))
    
    return np.array(t_arr), np.array(sp_arr), np.array(pv_arr), np.array(tq_arr), np.array(err_arr)

# Spusti simuláciu
t, sp, pv, tq, err = run_simulation(sp_rpm, kp, ti, t_load, duration=10)

# ─── METRIKY (ČÍSELNÉ HODNOTY) ──────────────────────────────────
st.markdown("## 📊 VÝSLEDKY")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🎯 Žiadaná rýchlosť", f"{sp_rpm} RPM")

with col2:
    final_speed = pv[-1] if len(pv) > 0 else 0
    st.metric("✅ Finálna rýchlosť", f"{final_speed:.0f} RPM", delta=f"{final_speed - sp_rpm:.0f}")

with col3:
    steady_error = abs(err[-1]) if len(err) > 0 else 0
    st.metric("📊 Chyba", f"{steady_error:.1f} RPM")

with col4:
    max_torque = np.max(tq) if len(tq) > 0 else 0
    st.metric("⚡ Max. moment", f"{max_torque:.2f} N·m")

with col5:
    st.metric("🔧 Záťaž", f"{t_load:.1f} N·m")

# ─── GRAFY ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📈 GRAFY")

try:
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
    
    # Rýchlosť
    ax1.plot(t, sp, 'o-', color='orange', lw=2, label='Žiadaná (SP)', markersize=2)
    ax1.plot(t, pv, 's-', color='blue', lw=2, label='Skutočná (PV)', markersize=2)
    ax1.axhline(1300, color='red', lw=1, linestyle='--', alpha=0.5)
    ax1.set_xlabel('Čas [s]', fontweight='bold')
    ax1.set_ylabel('Rýchlosť [RPM]', fontweight='bold')
    ax1.set_title('RÝCHLOSŤ HRIADELE', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Moment
    ax2.plot(t, tq, 'o-', color='green', lw=2, label='Moment/motor', markersize=2)
    ax2.axhline(15, color='red', lw=1, linestyle='--', alpha=0.5)
    ax2.set_xlabel('Čas [s]', fontweight='bold')
    ax2.set_ylabel('Moment [N·m]', fontweight='bold')
    ax2.set_title('MOMENT NA MOTORE', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    st.pyplot(fig)
except:
    st.warning("⚠️ Graf sa nedá vykresliť")

# ─── TABUĽKA ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📋 TABUĽKA")

data = pd.DataFrame({
    "Čas [s]": np.round(t[::10], 2),
    "SP [RPM]": np.round(sp[::10], 0),
    "PV [RPM]": np.round(pv[::10], 0),
    "Odchýlka [RPM]": np.round(err[::10], 1),
    "Moment [N·m]": np.round(tq[::10], 2)
})

st.dataframe(data, use_container_width=True)

st.success("✅ Aplikácia je pripravená!")
