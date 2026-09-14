import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

st.set_page_config(page_title="PM Motor Control", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#FF000F;'>
⚙️ PM Motor Control – PI Control
</h1>
<p style='text-align:center; color:gray; font-size:16px;'>
Azipod XO 21MW – Steering System (4 motors on common shaft)
</p>
""", unsafe_allow_html=True)

dt       = 0.02
N_MOT    = 4
rpm2rads = lambda r: r * 2 * np.pi / 60
rads2rpm = lambda w: w * 60 / (2 * np.pi)

MOTORS_DB = {
    "Phase Ultrakt3 (M20622S002932)": {
        "type": "PM",
        "Km": 3.34,
        "J_pm": 0.085,
        "B_pm": 0.08,
        "eta_pm": 0.96,
        "kp_pm": 3.5,
        "ti_pm": 0.75,
        "description": "Phase Motion Control Ultrakt3 - High dynamic PM servo motor"
    },
    "Default Azipod XO": {
        "type": "PM",
        "Km": 0.9,
        "J_pm": 1.5,
        "B_pm": 0.04,
        "eta_pm": 0.97,
        "kp_pm": 3.0,
        "ti_pm": 0.8,
        "description": "Generic Azipod XO 21MW steering motor"
    }
}

tab0, tab1, tab2 = st.tabs(["📐 SYSTEM DESIGN", "⚙️ PARAMETERS", "📊 CALCULATION & RESULTS"])

with tab0:
    st.markdown("## 📐 SYSTEM ARCHITECTURE")
    st.markdown("---")
    
    fig, ax = plt.subplots(figsize=(16, 10), facecolor='#f5f5f5')
    ax.set_xlim(-1, 20)
    ax.set_ylim(-1, 14)
    ax.axis('off')
    
    ax.text(10, 13, 'Azipod XO 21MW – Steering System Architecture', 
            fontsize=18, fontweight='bold', ha='center', color='#FF000F')
    ax.text(10, 12.3, '4 Electric Motors on Common Shaft', 
            fontsize=12, ha='center', color='gray')
    
    ctrl_box = FancyBboxPatch((0.5, 10), 3.5, 1.5, boxstyle='round,pad=0.1',
                               edgecolor='#FF000F', facecolor='#FFE5E5', linewidth=2)
    ax.add_patch(ctrl_box)
    ax.text(2.25, 11, 'PI Controller', fontsize=11, fontweight='bold', ha='center', va='center')
    ax.text(2.25, 10.5, 'Kp, Ti', fontsize=9, ha='center', va='center', style='italic')
    
    arrow1 = FancyArrowPatch((4, 10.75), (5.5, 10.75), arrowstyle='->', 
                             mutation_scale=25, color='#FF000F', linewidth=2)
    ax.add_patch(arrow1)
    ax.text(4.75, 11, 'Command', fontsize=9, ha='center', color='#FF000F', fontweight='bold')
    
    shaft_circle = Circle((10, 7), 0.6, color='#888888', ec='black', linewidth=2)
    ax.add_patch(shaft_circle)
    ax.text(10, 7, 'SHAFT', fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    motor_positions = [
        (5.5, 10, 'Motor 1\n(PM)', '#FF000F'),
        (14.5, 10, 'Motor 2\n(PM)', '#FF000F'),
        (5.5, 4, 'Motor 3\n(PM)', '#FF000F'),
        (14.5, 4, 'Motor 4\n(PM)', '#FF000F'),
    ]
    
    for x, y, label, color in motor_positions:
        motor_box = FancyBboxPatch((x-1, y-0.6), 2, 1.2, boxstyle='round,pad=0.05',
                                   edgecolor=color, facecolor=color, alpha=0.3, linewidth=2.5)
        ax.add_patch(motor_box)
        ax.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center')
        
        if x < 10:
            arrow = FancyArrowPatch((x+1, y), (9.4, 7), arrowstyle='->', 
                                   mutation_scale=20, color=color, linewidth=2.5)
        else:
            arrow = FancyArrowPatch((x-1, y), (10.6, 7), arrowstyle='->', 
                                   mutation_scale=20, color=color, linewidth=2.5)
        ax.add_patch(arrow)
    
    load_box = FancyBboxPatch((8.5, 5.2), 3, 1, boxstyle='round,pad=0.1',
                              edgecolor='#228B22', facecolor='#90EE90', linewidth=2)
    ax.add_patch(load_box)
    ax.text(10, 5.7, 'LOAD (Azimuth)', fontsize=10, fontweight='bold', ha='center', va='center')
    
    arrow_load = FancyArrowPatch((10, 6.4), (10, 6.2), arrowstyle='<->', 
                                mutation_scale=20, color='#228B22', linewidth=2.5)
    ax.add_patch(arrow_load)
    
    ax.annotate('', xy=(1.5, 10), xytext=(1.5, 2),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue', linestyle='dashed'))
    ax.text(0.5, 6, 'Speed\nFeedback', fontsize=9, ha='center', color='blue', fontweight='bold')
    
    legend_y = 1.5
    pm_rect = mpatches.Rectangle((1, legend_y), 0.3, 0.3, fc='#FF000F', alpha=0.7)
    ax.add_patch(pm_rect)
    ax.text(1.6, legend_y+0.15, 'PM Motor', fontsize=10, va='center')
    
    specs_text = "SYSTEM: 4 PM Motors | PI Controller | Azimuth Load"
    ax.text(10, 0.3, specs_text, fontsize=9, ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8, pad=0.5),
            family='monospace', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

with tab1:
    st.markdown("## 🔧 MOTOR & LOAD PARAMETERS")
    st.markdown("---")
    
    st.markdown("### 🎯 QUICK MOTOR SELECTION")
    
    motor_cols = st.columns(len(MOTORS_DB))
    
    for idx, (motor_name, motor_params) in enumerate(MOTORS_DB.items()):
        with motor_cols[idx]:
            if st.button(f"🔌 {motor_name}", use_container_width=True, key=f"motor_{idx}"):
                if motor_params["type"] == "PM":
                    st.session_state["Km"] = motor_params["Km"]
                    st.session_state["J_pm"] = motor_params["J_pm"]
                    st.session_state["B_pm"] = motor_params["B_pm"]
                    st.session_state["eta_pm"] = motor_params["eta_pm"] * 100
                    st.success(f"✅ {motor_name} loaded!")
                st.rerun()
    
    with st.expander("📋 Motor Description", expanded=True):
        for motor_name, motor_params in MOTORS_DB.items():
            st.markdown(f"**{motor_name}:** {motor_params['description']}")
    
    st.markdown("---")
    
    st.markdown("### 🔗 COMMON PARAMETERS")
    col_sp1, col_sp2, col_sp3, col_sp4 = st.columns(4)
    
    with col_sp1:
        sp_rpm = st.number_input("📊 Desired Speed [RPM]", min_value=0, max_value=2000, value=1480, step=50, key="sp_rpm")
    with col_sp2:
        t_load = st.number_input("🔧 Load Torque [N·m]", min_value=0.0, max_value=5000.0, value=500.0, step=50.0, key="t_load")
    with col_sp3:
        J_load = st.number_input("📦 Load Inertia J [kg·m²]", min_value=0.01, max_value=100.0, value=5.0, step=0.5, key="J_load")
    with col_sp4:
        t_sim = st.number_input("⏱️ Simulation Time [s]", min_value=2.0, max_value=60.0, value=10.0, step=1.0, key="t_sim")
    
    st.markdown("---")
    st.markdown("### 🔴 PERMANENT MAGNET (PM) MOTOR")
    
    with st.expander("📋 PM Motor – Motor Parameters", expanded=True):
        pm_col3, pm_col4, pm_col5, pm_col6 = st.columns(4)
        with pm_col3:
            Km = st.number_input("Km [N·m/A]", min_value=0.01, max_value=100.0, value=st.session_state.get("Km", 0.9), step=0.1, key="Km", format="%.3f")
        with pm_col4:
            J_pm = st.number_input("J Motor [kg·m²]", min_value=0.001, max_value=50.0, value=st.session_state.get("J_pm", 1.5), step=0.1, key="J_pm", format="%.3f")
        with pm_col5:
            B_pm = st.number_input("B Friction [N·m·s/rad]", min_value=0.001, max_value=10.0, value=st.session_state.get("B_pm", 0.04), step=0.01, key="B_pm", format="%.3f")
        with pm_col6:
            eta_pm = st.number_input("Efficiency η [%]", min_value=50.0, max_value=99.0, value=st.session_state.get("eta_pm", 97.0), step=0.5, key="eta_pm")

with tab2:
    st.markdown("## 📊 CALCULATION & RESULTS")
    st.markdown("---")

    def sim_pm(sp, kp, ti, tl, km, j_mot, b, j_ld, dur):
        J = N_MOT * j_mot + j_ld
        omega, intg = 0.0, 0.0
        t_a, sp_a, pv_a, tq_a = [], [], [], []
        for i in range(int(dur / dt)):
            e = rpm2rads(sp) - omega
            intg += e * dt
            u = kp * e + (kp / max(ti, 1e-6)) * intg
            Tm = np.clip(km * u / N_MOT, -50.0, 150.0)
            domega = (N_MOT * Tm - tl - b * omega) / J
            omega = max(0.0, min(omega + domega * dt, rpm2rads(2000)))
            t_a.append(i * dt)
            sp_a.append(sp)
            pv_a.append(rads2rpm(omega))
            tq_a.append(Tm)
        return np.array(t_a), np.array(sp_a), np.array(pv_a), np.array(tq_a)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        run_btn = st.button("▶️   RUN CALCULATION", use_container_width=True, type="primary")

    if run_btn:
        with st.spinner("🔄 Calculation in progress ..."):
            try:
                r_pm = sim_pm(sp_rpm, st.session_state.get("kp_pm", 3.0), st.session_state.get("ti_pm", 0.8), t_load, Km, J_pm, B_pm, J_load, t_sim)

                st.session_state["t_pm"] = r_pm[0]
                st.session_state["sp_pm"] = r_pm[1]
                st.session_state["pv_pm"] = r_pm[2]
                st.session_state["tq_pm"] = r_pm[3]
                st.session_state["res_tsim"] = t_sim
                st.session_state["res_sp"] = sp_rpm
                st.session_state["res_tload"] = t_load
                st.session_state["ready"] = True

                st.success("✅ Calculation complete! Results below.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.markdown("---")

    if st.session_state.get("ready", False):
        t_pm = st.session_state["t_pm"]
        pv_pm = st.session_state["pv_pm"]
        sp_pm = st.session_state["sp_pm"]
        tq_pm = st.session_state["tq_pm"]
        _tsim = st.session_state["res_tsim"]
        _sp = st.session_state["res_sp"]
        _tl = st.session_state["res_tload"]

        st.markdown("## 🎮 PI CONTROLLER SETTINGS")

        pcol1, pcol2 = st.columns(2)

        with pcol1:
            st.markdown("#### 🔴 PM MOTOR – PI Controller")
            pm_c1, pm_c2 = st.columns(2)
            with pm_c1:
                kp_pm = st.number_input("Kp (PM)", min_value=0.1, max_value=50.0, value=st.session_state.get("kp_pm", 3.0), step=0.1, key="kp_pm_display")
            with pm_c2:
                ti_pm = st.number_input("Ti [s] (PM)", min_value=0.05, max_value=10.0, value=st.session_state.get("ti_pm", 0.8), step=0.05, key="ti_pm_display")

        st.markdown("---")

        st.markdown("## ⏱️ TIME AXIS SETTINGS")
        tc1, tc2 = st.columns(2)
        with tc1:
            t_start = st.slider("▶ Start [s]", 0.0, float(_tsim) - 1.0, 0.0, 0.5)
        with tc2:
            t_end = st.slider("⏹ End [s]", 1.0, float(_tsim), float(_tsim), 0.5)
        if t_start >= t_end:
            t_start = 0.0

        m_pm = (t_pm >= t_start) & (t_pm <= t_end)

        st.markdown("---")
        st.markdown("## 📊 KEY METRICS")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("🎯 Setpoint", f"{_sp:.0f} RPM")
        with mc2:
            st.metric("🔴 PM – Final", f"{pv_pm[-1]:.0f} RPM", delta=f"{pv_pm[-1]-_sp:+.0f}")
        with mc3:
            st.metric("🔴 PM – Max Tm", f"{np.max(np.abs(tq_pm)):.2f} N·m")
        with mc4:
            st.metric("🔧 Load", f"{_tl:.1f} N·m")

        st.markdown("---")
        st.markdown("## 📈 SIMULATION GRAPHS")

        C_SP, C_PM = "#FFA500", "#FF000F"
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        plt.subplots_adjust(hspace=0.4)

        ax1 = axes[0]
        ax1_twin = ax1.twinx()
        ax1.plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP, lw=2, label="SP – Desired", zorder=10)
        ax1.plot(t_pm[m_pm], pv_pm[m_pm], "-", color=C_PM, lw=2.5, label="Speed [RPM]", zorder=10)
        ax1_twin.plot(t_pm[m_pm], tq_pm[m_pm], "-", color="black", lw=2.5, label="Torque [N·m]", zorder=5)
        ax1.set_ylabel("Speed [RPM]", fontsize=11, fontweight="bold", color=C_PM)
        ax1_twin.set_ylabel("Torque [N·m]", fontsize=11, fontweight="bold", color="black")
        ax1.tick_params(axis='y', labelcolor=C_PM)
        ax1_twin.tick_params(axis='y', labelcolor="black")
        ax1.set_xlim(t_start, t_end)
        ax1.set_xlabel("Time [s]", fontsize=11, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.set_title("🔴 PM MOTOR – SPEED + TORQUE", fontsize=13, fontweight="bold", color="#CC0000", pad=8)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc="best")

        axes[1].plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP, lw=2, label="SP")
        axes[1].plot(t_pm[m_pm], pv_pm[m_pm], "-", color=C_PM, lw=2.5, label="🔴 PM Motor")
        axes[1].set_ylim(bottom=-50)
        axes[1].set_title("⚡ SPEED RESPONSE", fontsize=13, fontweight="bold", color="black", pad=8)
        axes[1].set_ylabel("Speed [RPM]", fontsize=11, fontweight="bold")
        axes[1].set_xlabel("Time [s]", fontsize=11, fontweight="bold")
        axes[1].set_xlim(t_start, t_end)
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(fontsize=10, loc="best")

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("## 📋 RESULTS TABLE")
        n = 50
        ts = np.linspace(t_start, t_end, n)
        df = pd.DataFrame({
            "Time [s]": np.round(ts, 2),
            "SP [RPM]": np.full(n, _sp),
            "PM [RPM]": np.round(np.interp(ts, t_pm, pv_pm), 0),
            "PM Tm [N·m]": np.round(np.interp(ts, t_pm, tq_pm), 2),
        })
        st.dataframe(df, use_container_width=True, height=400)

        st.success("✅ Analysis complete!")
    else:
        st.info("⚠️ Click ▶️ RUN CALCULATION above to see results")
