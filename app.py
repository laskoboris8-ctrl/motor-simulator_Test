import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PM vs Indukčný Motor", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#FF000F;'>
⚙️ Porovnanie: PM Motor vs Indukčný Motor – PI Regulácia
</h1>
<p style='text-align:center; color:gray; font-size:16px;'>
4 motory na spoločnom hriadeli
</p>
""", unsafe_allow_html=True)

# ─── KONŠTANTY ──────────────────────────────────────────────────────────────
dt       = 0.02
N_MOT    = 4
rpm2rads = lambda r: r * 2 * np.pi / 60
rads2rpm = lambda w: w * 60 / (2 * np.pi)

# ─── ZADÁVANIE PARAMETROV ───────────────────────────────────────────────────
st.markdown("## ⚙️ PARAMETRE SIMULÁCIE")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔧 Spoločné parametre")
    sp_rpm = st.number_input("📊 Žiadaná rýchlosť [RPM]",  min_value=0,   max_value=1300, value=600,  step=50)
    t_load = st.number_input("🔧 Záťaž [N·m]",             min_value=0.0, max_value=20.0, value=2.0,  step=0.5)
    J_load = st.number_input("J záťaže [kg·m²]",           min_value=0.01,max_value=1.0,  value=0.05, step=0.01)
    t_sim  = st.number_input("⏱️ Doba simulácie [s]",       min_value=2.0, max_value=30.0, value=10.0, step=1.0)

with col2:
    st.markdown("### 🔴 PM Motor")
    st.markdown("**PI regulátor**")
    kp_pm  = st.number_input("Kp (PM)",       min_value=0.1,  max_value=20.0, value=3.0,  step=0.1,  key="kp_pm")
    ti_pm  = st.number_input("Ti [s] (PM)",   min_value=0.05, max_value=5.0,  value=0.8,  step=0.05, key="ti_pm")
    st.markdown("**Parametre motora**")
    Km     = st.number_input("Km [N·m/A]",    min_value=0.1,  max_value=5.0,  value=0.8,  step=0.1)
    J_pm   = st.number_input("J motora PM [kg·m²]",  min_value=0.001,max_value=0.5,value=0.02,step=0.001,format="%.3f")
    B_pm   = st.number_input("B trenie PM [N·m·s/rad]",min_value=0.001,max_value=0.5,value=0.02,step=0.001,format="%.3f")

with col3:
    st.markdown("### 🔵 Indukčný Motor")
    st.markdown("**PI regulátor**")
    kp_ind = st.number_input("Kp (IND)",      min_value=0.1,  max_value=20.0, value=2.0,  step=0.1,  key="kp_ind")
    ti_ind = st.number_input("Ti [s] (IND)",  min_value=0.05, max_value=5.0,  value=1.2,  step=0.05, key="ti_ind")
    st.markdown("**Parametre motora**")
    V_ph   = st.number_input("V fázové [V]",  min_value=10.0, max_value=400.0,value=63.0, step=1.0)
    R1     = st.number_input("R1 [Ω]",        min_value=0.01, max_value=10.0, value=0.5,  step=0.05, format="%.2f")
    R2     = st.number_input("R2 [Ω]",        min_value=0.01, max_value=10.0, value=0.4,  step=0.05, format="%.2f")
    X_tot  = st.number_input("X1+X2 [Ω]",    min_value=0.1,  max_value=20.0, value=1.8,  step=0.1)
    p_pair = st.number_input("Páry pólov (p)",min_value=1,    max_value=6,    value=2,    step=1)
    J_ind  = st.number_input("J motora IND [kg·m²]",min_value=0.001,max_value=0.5,value=0.02,step=0.001,format="%.3f")
    B_ind  = st.number_input("B trenie IND [N·m·s/rad]",min_value=0.001,max_value=0.5,value=0.02,step=0.001,format="%.3f")

# ─── TLAČIDLO SPUŠTENIA ──────────────────────────────────────────────────────
st.markdown("---")
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    run_btn = st.button("▶️   SPUSTIŤ VÝPOČET", use_container_width=True, type="primary")

# ─── SIMULAČNÉ FUNKCIE ───────────────────────────────────────────────────────
def sim_pm(sp, kp, ti, tl, km, j_mot, b, j_ld, dur):
    J = N_MOT * j_mot + j_ld
    omega, intg = 0.0, 0.0
    t_a, sp_a, pv_a, tq_a = [], [], [], []
    for i in range(int(dur / dt)):
        e    = rpm2rads(sp) - omega
        intg += e * dt
        u    = kp * e + (kp / max(ti, 1e-6)) * intg
        Tm   = np.clip(km * u / N_MOT, -0.5, 15.0)
        domega = (N_MOT * Tm - tl - b * omega) / J
        omega  = max(0.0, min(omega + domega * dt, rpm2rads(1350)))
        t_a.append(i * dt);  sp_a.append(sp)
        pv_a.append(rads2rpm(omega)); tq_a.append(Tm)
    return np.array(t_a), np.array(sp_a), np.array(pv_a), np.array(tq_a)


def sim_ind(sp, kp, ti, tl, V, r1, r2, x, j_mot, b, j_ld, pp, dur):
    J            = N_MOT * j_mot + j_ld
    omega_s_max  = 2 * np.pi * 50.0 / pp
    omega, intg  = 0.0, 0.0
    t_a, sp_a, pv_a, tq_a = [], [], [], []
    for i in range(int(dur / dt)):
        e    = rpm2rads(sp) - omega
        intg += e * dt
        u    = kp * e + (kp / max(ti, 1e-6)) * intg
        omega_s = np.clip(u, 0.0, omega_s_max * 1.05)
        V_act = V * min(omega_s / max(omega_s_max, 1e-6), 1.1)
        if omega_s > 0.5:
            slip  = np.clip((omega_s - omega) / omega_s, -0.99, 0.99)
            R2s   = r2 / slip if abs(slip) > 1e-6 else r2 / 1e-6
            Tm    = np.clip((3.0 * V_act**2 * R2s) / (omega_s * ((r1 + R2s)**2 + x**2)), -15.0, 15.0)
        else:
            Tm = 0.0
        domega = (N_MOT * Tm - tl - b * omega) / J
        omega  = max(0.0, min(omega + domega * dt, rpm2rads(1350)))
        t_a.append(i * dt);  sp_a.append(sp)
        pv_a.append(rads2rpm(omega)); tq_a.append(Tm)
    return np.array(t_a), np.array(sp_a), np.array(pv_a), np.array(tq_a)

# ─── SPUSTENIE ───────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner("🔄 Prebieha výpočet ..."):
        r_pm = sim_pm(sp_rpm, kp_pm, ti_pm, t_load, Km, J_pm, B_pm, J_load, t_sim)
        r_id = sim_ind(sp_rpm, kp_ind, ti_ind, t_load, V_ph, R1, R2, X_tot, J_ind, B_ind, J_load, p_pair, t_sim)

    st.session_state.update({
        "t_pm": r_pm[0], "sp_pm": r_pm[1], "pv_pm": r_pm[2], "tq_pm": r_pm[3],
        "t_id": r_id[0], "sp_id": r_id[1], "pv_id": r_id[2], "tq_id": r_id[3],
        "t_sim": t_sim, "sp_rpm": sp_rpm, "t_load": t_load, "ready": True
    })
    st.success("✅ Výpočet hotový! Pozri výsledky nižšie.")

# ─── VÝSLEDKY ────────────────────────────────────────────────────────────────
if st.session_state.get("ready", False):
    t_pm  = st.session_state["t_pm"];  pv_pm = st.session_state["pv_pm"]
    sp_pm = st.session_state["sp_pm"]; tq_pm = st.session_state["tq_pm"]
    t_id  = st.session_state["t_id"];  pv_id = st.session_state["pv_id"]
    sp_id = st.session_state["sp_id"]; tq_id = st.session_state["tq_id"]
    _tsim = st.session_state["t_sim"]
    _sp   = st.session_state["sp_rpm"]
    _tl   = st.session_state["t_load"]

    st.markdown("---")
    st.markdown("## ⏱️ NASTAVENIE ČASOVEJ OSI GRAFOV")
    tc1, tc2 = st.columns(2)
    with tc1:
        t_start = st.slider("▶ Začiatok [s]", 0.0, float(_tsim) - 1.0, 0.0, 1.0)
    with tc2:
        t_end   = st.slider("⏹ Koniec [s]",  1.0, float(_tsim),       float(_tsim), 1.0)
    if t_start >= t_end:
        t_start = 0.0

    m_pm = (t_pm >= t_start) & (t_pm <= t_end)
    m_id = (t_id >= t_start) & (t_id <= t_end)

    st.markdown("---")
    st.markdown("## 📊 VÝSLEDKY")
    mc1,mc2,mc3,mc4,mc5,mc6 = st.columns(6)
    mc1.metric("🎯 Setpoint",         f"{_sp} RPM")
    mc2.metric("🔴 PM – finálna",     f"{pv_pm[-1]:.0f} RPM", delta=f"{pv_pm[-1]-_sp:.0f}")
    mc3.metric("🔵 IND – finálna",    f"{pv_id[-1]:.0f} RPM", delta=f"{pv_id[-1]-_sp:.0f}")
    mc4.metric("🔴 PM – max Tm",      f"{np.max(tq_pm):.2f} N·m")
    mc5.metric("🔵 IND – max Tm",     f"{np.max(tq_id):.2f} N·m")
    mc6.metric("🔧 Záťaž",            f"{_tl:.1f} N·m")

    st.markdown("---")
    st.markdown("## 📈 GRAFY")

    C_SP  = "#FFA500"
    C_PM  = "#FF000F"
    C_IND = "#6764f6"

    fig, axes = plt.subplots(5, 1, figsize=(14, 26))
    plt.subplots_adjust(hspace=0.5)

    def style(ax, title, ylabel, c):
        ax.set_title(title, fontsize=13, fontweight="bold", color=c, pad=8)
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
        ax.set_xlabel("Čas [s]", fontsize=11, fontweight="bold")
        ax.set_xlim(t_start, t_end)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc="best")

    axes[0].plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP,  lw=2,   label="SP – Žiadaná")
    axes[0].plot(t_pm[m_pm], pv_pm[m_pm], "-",  color=C_PM,  lw=2.5, label="PV – Skutočná")
    axes[0].set_ylim(bottom=-10)
    style(axes[0], "🔴 PM MOTOR – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "#CC0000")

    axes[1].plot(t_pm[m_pm], tq_pm[m_pm], "-",  color=C_PM,  lw=2.5, label="Moment / motor")
    axes[1].axhline(15, color="red", lw=1.5, ls="--", alpha=0.6, label="Limit 15 N·m")
    style(axes[1], "🔴 PM MOTOR – MOMENT NA MOTORE", "Moment [N·m]", "#CC0000")

    axes[2].plot(t_id[m_id], sp_id[m_id], "--", color=C_SP,  lw=2,   label="SP – Žiadaná")
    axes[2].plot(t_id[m_id], pv_id[m_id], "-",  color=C_IND, lw=2.5, label="PV – Skutočná")
    axes[2].set_ylim(bottom=-10)
    style(axes[2], "🔵 INDUKČNÝ MOTOR – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "#4444cc")

    axes[3].plot(t_id[m_id], tq_id[m_id], "-",  color=C_IND, lw=2.5, label="Moment / motor")
    axes[3].axhline(15, color="red", lw=1.5, ls="--", alpha=0.6, label="Limit 15 N·m")
    style(axes[3], "🔵 INDUKČNÝ MOTOR – MOMENT NA MOTORE", "Moment [N·m]", "#4444cc")

    axes[4].plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP,  lw=2,   label="SP – Žiadaná")
    axes[4].plot(t_pm[m_pm], pv_pm[m_pm], "-",  color=C_PM,  lw=2.5, label="🔴 PM Motor")
    axes[4].plot(t_id[m_id], pv_id[m_id], "-",  color=C_IND, lw=2.5, label="🔵 Indukčný Motor")
    axes[4].set_ylim(bottom=-10)
    style(axes[4], "⚡ POROVNANIE: PM vs INDUKČNÝ – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "black")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## 📋 TABUĽKA VÝSLEDKOV")

    n  = 50
    ts = np.linspace(t_start, t_end, n)
    df = pd.DataFrame({
        "Čas [s]":       np.round(ts, 2),
        "SP [RPM]":      np.full(n, _sp),
        "PM PV [RPM]":   np.round(np.interp(ts, t_pm, pv_pm), 0),
        "PM Tm [N·m]":   np.round(np.interp(ts, t_pm, tq_pm), 2),
        "IND PV [RPM]":  np.round(np.interp(ts, t_id, pv_id), 0),
        "IND Tm [N·m]":  np.round(np.interp(ts, t_id, tq_id), 2),
    })
    st.dataframe(df, use_container_width=True)

    st.info("💡 Zmeň parametre hore a klikni znova ▶️ SPUSTIŤ VÝPOČET")
