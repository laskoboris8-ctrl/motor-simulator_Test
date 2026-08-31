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
Azipod XO 21MW – Steering systém (4 motory na hriadeľ)
</p>
""", unsafe_allow_html=True)

dt       = 0.02
N_MOT    = 4
rpm2rads = lambda r: r * 2 * np.pi / 60
rads2rpm = lambda w: w * 60 / (2 * np.pi)

# ─── ZÁLOŽKY ────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["⚙️ PARAMETRE", "🎮 VÝPOČET", "📊 VÝSLEDKY"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: ZADÁVANIE PARAMETROV
# ═══════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown("## 🔧 VŠETKY PARAMETRE SIMULÁCIE")
    st.markdown("---")
    
    # ─── SPOLOČNÉ PARAMETRE ───────────────────────────────────────────────
    st.markdown("### 🔗 SPOLOČNÉ PARAMETRE")
    
    col_sp1, col_sp2, col_sp3, col_sp4 = st.columns(4)
    
    with col_sp1:
        sp_rpm = st.number_input("📊 Žiadaná rýchlosť [RPM]", 
                                 min_value=0, max_value=2000, value=1480, step=50, key="sp_rpm")
    with col_sp2:
        t_load = st.number_input("🔧 Záťaž [N·m]", 
                                 min_value=0.0, max_value=5000.0, value=500.0, step=50.0, key="t_load")
    with col_sp3:
        J_load = st.number_input("📦 J záťaže [kg·m²]", 
                                 min_value=0.01, max_value=100.0, value=5.0, step=0.5, key="J_load", format="%.2f")
    with col_sp4:
        t_sim = st.number_input("⏱️ Doba simulácie [s]", 
                               min_value=2.0, max_value=60.0, value=10.0, step=1.0, key="t_sim")
    
    st.markdown("---")
    
    # ─── PM MOTOR ─────────────────────────────────────────────────────────
    st.markdown("### 🔴 PERMANENTNÝ MAGNET (PM) MOTOR")
    
    with st.expander("📋 PM Motor – PI regulátor", expanded=True):
        pm_col1, pm_col2 = st.columns(2)
        with pm_col1:
            kp_pm = st.number_input("Kp (PM) – proporcionálne zosilnenie", 
                                    min_value=0.1, max_value=50.0, value=3.0, step=0.1, key="kp_pm")
        with pm_col2:
            ti_pm = st.number_input("Ti [s] (PM) – integračná konštanta", 
                                    min_value=0.05, max_value=10.0, value=0.8, step=0.05, key="ti_pm")
    
    with st.expander("📋 PM Motor – Parametre motora", expanded=True):
        pm_col3, pm_col4, pm_col5, pm_col6 = st.columns(4)
        
        with pm_col3:
            Km = st.number_input("Km [N·m/A] – konštanta momentu", 
                                min_value=0.01, max_value=100.0, value=0.9, step=0.1, key="Km", format="%.3f")
        with pm_col4:
            J_pm = st.number_input("J motora [kg·m²] (PM)", 
                                  min_value=0.001, max_value=50.0, value=1.5, step=0.1, key="J_pm", format="%.3f")
        with pm_col5:
            B_pm = st.number_input("B trenie [N·m·s/rad] (PM)", 
                                  min_value=0.001, max_value=10.0, value=0.04, step=0.01, key="B_pm", format="%.3f")
        with pm_col6:
            eta_pm = st.number_input("Účinnosť η [%] (PM)", 
                                    min_value=50.0, max_value=99.0, value=97.0, step=0.5, key="eta_pm")
    
    st.markdown("---")
    
    # ─── INDUKČNÝ MOTOR ────────────────────────────────────────────────────
    st.markdown("### 🔵 INDUKČNÝ ASYNCHRONNÝ MOTOR")
    
    with st.expander("📋 Indukčný Motor – PI regulátor", expanded=True):
        ind_col1, ind_col2 = st.columns(2)
        with ind_col1:
            kp_ind = st.number_input("Kp (IND) – proporcionálne zosilnenie", 
                                     min_value=0.1, max_value=50.0, value=2.5, step=0.1, key="kp_ind")
        with ind_col2:
            ti_ind = st.number_input("Ti [s] (IND) – integračná konštanta", 
                                     min_value=0.05, max_value=10.0, value=1.0, step=0.05, key="ti_ind")
    
    with st.expander("📋 Indukčný Motor – Elektrické parametre", expanded=True):
        ind_e1, ind_e2, ind_e3, ind_e4 = st.columns(4)
        
        with ind_e1:
            V_ph = st.number_input("V fázové [V]", 
                                  min_value=10.0, max_value=1000.0, value=230.0, step=10.0, key="V_ph")
        with ind_e2:
            f_hz = st.number_input("Frekvencia [Hz]", 
                                  min_value=25.0, max_value=100.0, value=50.0, step=5.0, key="f_hz")
        with ind_e3:
            p_pair = st.number_input("Páry pólov (p)", 
                                    min_value=1, max_value=6, value=2, step=1, key="p_pair")
        with ind_e4:
            eta_ind = st.number_input("Účinnosť η [%] (IND)", 
                                     min_value=50.0, max_value=99.0, value=93.0, step=0.5, key="eta_ind")
    
    with st.expander("📋 Indukčný Motor – Odpory a reaktancie", expanded=True):
        ind_r1, ind_r2, ind_r3, ind_r4 = st.columns(4)
        
        with ind_r1:
            R1 = st.number_input("R1 [Ω] – odpor státora", 
                                min_value=0.001, max_value=50.0, value=0.095, step=0.01, key="R1", format="%.3f")
        with ind_r2:
            R2 = st.number_input("R2 [Ω] – odpor rotora", 
                                min_value=0.001, max_value=50.0, value=0.075, step=0.01, key="R2", format="%.3f")
        with ind_r3:
            X_tot = st.number_input("X1+X2 [Ω] – reaktancia", 
                                   min_value=0.01, max_value=100.0, value=1.2, step=0.1, key="X_tot")
        with ind_r4:
            st.info("Reaktancia = X_státor + X_rotor")
    
    with st.expander("📋 Indukčný Motor – Mechanické parametre", expanded=True):
        ind_m1, ind_m2, ind_m3 = st.columns(3)
        
        with ind_m1:
            J_ind = st.number_input("J motora [kg·m²] (IND)", 
                                   min_value=0.001, max_value=50.0, value=1.8, step=0.1, key="J_ind", format="%.3f")
        with ind_m2:
            B_ind = st.number_input("B trenie [N·m·s/rad] (IND)", 
                                   min_value=0.001, max_value=10.0, value=0.05, step=0.01, key="B_ind", format="%.3f")
        with ind_m3:
            st.info("B = viscózne trenie + trenie ložísk")
    
    st.markdown("---")
    st.info("💾 Všetky parametre sa ukladajú automaticky")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: VÝPOČET
# ═══════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("## 🎮 SPUSTENIE SIMULÁCIE")
    st.markdown("---")
    
    # ─── SIMULAČNÉ FUNKCIE ─────────────────────────────────────────────────
    def sim_pm(sp, kp, ti, tl, km, j_mot, b, j_ld, dur):
        J = N_MOT * j_mot + j_ld
        omega, intg = 0.0, 0.0
        t_a, sp_a, pv_a, tq_a, u_a = [], [], [], [], []
        for i in range(int(dur / dt)):
            e    = rpm2rads(sp) - omega
            intg += e * dt
            u    = kp * e + (kp / max(ti, 1e-6)) * intg
            Tm   = np.clip(km * u / N_MOT, -50.0, 150.0)
            domega = (N_MOT * Tm - tl - b * omega) / J
            omega  = max(0.0, min(omega + domega * dt, rpm2rads(2000)))
            t_a.append(i * dt);  sp_a.append(sp)
            pv_a.append(rads2rpm(omega)); tq_a.append(Tm); u_a.append(u)
        return np.array(t_a), np.array(sp_a), np.array(pv_a), np.array(tq_a), np.array(u_a)

    def sim_ind(sp, kp, ti, tl, V, f, r1, r2, x, j_mot, b, j_ld, pp, dur):
        J            = N_MOT * j_mot + j_ld
        omega_s_max  = 2 * np.pi * f / pp
        omega, intg  = 0.0, 0.0
        t_a, sp_a, pv_a, tq_a, u_a = [], [], [], [], []
        for i in range(int(dur / dt)):
            e    = rpm2rads(sp) - omega
            intg += e * dt
            u    = kp * e + (kp / max(ti, 1e-6)) * intg
            omega_s = np.clip(u, 0.0, omega_s_max * 1.05)
            V_act = V * min(omega_s / max(omega_s_max, 1e-6), 1.1)
            if omega_s > 0.5:
                slip  = np.clip((omega_s - omega) / omega_s, -0.99, 0.99)
                R2s   = r2 / slip if abs(slip) > 1e-6 else r2 / 1e-6
                Tm    = np.clip((3.0 * V_act**2 * R2s) / (omega_s * ((r1 + R2s)**2 + x**2)), -150.0, 150.0)
            else:
                Tm = 0.0
            domega = (N_MOT * Tm - tl - b * omega) / J
            omega  = max(0.0, min(omega + domega * dt, rpm2rads(2000)))
            t_a.append(i * dt);  sp_a.append(sp)
            pv_a.append(rads2rpm(omega)); tq_a.append(Tm); u_a.append(u)
        return np.array(t_a), np.array(sp_a), np.array(pv_a), np.array(tq_a), np.array(u_a)

    # ─── TLAČIDLO SPUŠTENIA ────────────────────────────────────────────────
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        run_btn = st.button("▶️   SPUSTIŤ VÝPOČET", use_container_width=True, type="primary")

    if run_btn:
        with st.spinner("🔄 Prebieha výpočet ..."):
            try:
                r_pm = sim_pm(st.session_state.get("sp_rpm", 1480), 
                            st.session_state.get("kp_pm", 3.0), 
                            st.session_state.get("ti_pm", 0.8), 
                            st.session_state.get("t_load", 500),
                            st.session_state.get("Km", 0.9), 
                            st.session_state.get("J_pm", 1.5), 
                            st.session_state.get("B_pm", 0.04), 
                            st.session_state.get("J_load", 5.0), 
                            st.session_state.get("t_sim", 10.0))
                
                r_id = sim_ind(st.session_state.get("sp_rpm", 1480), 
                             st.session_state.get("kp_ind", 2.5), 
                             st.session_state.get("ti_ind", 1.0), 
                             st.session_state.get("t_load", 500),
                             st.session_state.get("V_ph", 230.0), 
                             st.session_state.get("f_hz", 50.0), 
                             st.session_state.get("R1", 0.095),
                             st.session_state.get("R2", 0.075), 
                             st.session_state.get("X_tot", 1.2), 
                             st.session_state.get("J_ind", 1.8), 
                             st.session_state.get("B_ind", 0.05), 
                             st.session_state.get("J_load", 5.0), 
                             st.session_state.get("p_pair", 2), 
                             st.session_state.get("t_sim", 10.0))

                st.session_state.update({
                    "t_pm": r_pm[0], "sp_pm": r_pm[1], "pv_pm": r_pm[2], "tq_pm": r_pm[3], "u_pm": r_pm[4],
                    "t_id": r_id[0], "sp_id": r_id[1], "pv_id": r_id[2], "tq_id": r_id[3], "u_id": r_id[4],
                    "t_sim": st.session_state.get("t_sim", 10.0),
                    "sp_rpm": st.session_state.get("sp_rpm", 1480),
                    "t_load": st.session_state.get("t_load", 500),
                    "ready": True
                })
                st.success("✅ Výpočet hotový! Prejdi do záložky 📊 VÝSLEDKY")
            except Exception as e:
                st.error(f"❌ Chyba pri výpočte: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: VÝSLEDKY
# ═══════════════════════════════════════════════════════════════════════════

with tab3:
    if st.session_state.get("ready", False):
        t_pm  = st.session_state["t_pm"];  pv_pm = st.session_state["pv_pm"]
        sp_pm = st.session_state["sp_pm"]; tq_pm = st.session_state["tq_pm"]; u_pm = st.session_state["u_pm"]
        t_id  = st.session_state["t_id"];  pv_id = st.session_state["pv_id"]
        sp_id = st.session_state["sp_id"]; tq_id = st.session_state["tq_id"]; u_id = st.session_state["u_id"]
        _tsim = st.session_state["t_sim"]
        _sp   = st.session_state["sp_rpm"]
        _tl   = st.session_state["t_load"]

        # ─── ČASOVÁ OS ──────────────────────────────────────────────────────
        st.markdown("## ⏱️ NASTAVENIE ČASOVEJ OSI")
        tc1, tc2 = st.columns(2)
        with tc1:
            t_start = st.slider("▶ Začiatok [s]", 0.0, float(_tsim) - 1.0, 0.0, 0.5)
        with tc2:
            t_end   = st.slider("⏹ Koniec [s]", 1.0, float(_tsim), float(_tsim), 0.5)
        if t_start >= t_end:
            t_start = 0.0

        m_pm = (t_pm >= t_start) & (t_pm <= t_end)
        m_id = (t_id >= t_start) & (t_id <= t_end)

        # ─── METRIKY ────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 📊 KLÚČOVÉ METRIKY")
        
        mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
        
        with mc1:
            st.metric("🎯 Setpoint", f"{_sp:.0f} RPM")
        with mc2:
            delta_pm = pv_pm[-1] - _sp
            st.metric("🔴 PM – finálna", f"{pv_pm[-1]:.0f} RPM", delta=f"{delta_pm:+.0f}")
        with mc3:
            delta_id = pv_id[-1] - _sp
            st.metric("🔵 IND – finálna", f"{pv_id[-1]:.0f} RPM", delta=f"{delta_id:+.0f}")
        with mc4:
            st.metric("🔴 PM – max Tm", f"{np.max(np.abs(tq_pm)):.2f} N·m")
        with mc5:
            st.metric("🔵 IND – max Tm", f"{np.max(np.abs(tq_id)):.2f} N·m")
        with mc6:
            st.metric("🔧 Záťaž", f"{_tl:.1f} N·m")

        # ─── GRAFY ──────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 📈 GRAFY SIMULÁCIE")

        C_SP  = "#FFA500"
        C_PM  = "#FF000F"
        C_IND = "#6764f6"

        fig, axes = plt.subplots(5, 1, figsize=(15, 28))
        plt.subplots_adjust(hspace=0.5)

        def style(ax, title, ylabel, c):
            ax.set_title(title, fontsize=13, fontweight="bold", color=c, pad=8)
            ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
            ax.set_xlabel("Čas [s]", fontsize=11, fontweight="bold")
            ax.set_xlim(t_start, t_end)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10, loc="best")

        # Graf 1: PM rýchlosť
        axes[0].plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP, lw=2, label="SP – Žiadaná")
        axes[0].plot(t_pm[m_pm], pv_pm[m_pm], "-", color=C_PM, lw=2.5, label="PV – Skutočná")
        axes[0].axhline(_sp, color=C_SP, lw=1, ls=":", alpha=0.5)
        axes[0].set_ylim(bottom=-50)
        style(axes[0], "🔴 PM MOTOR – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "#CC0000")

        # Graf 2: PM moment
        axes[1].plot(t_pm[m_pm], tq_pm[m_pm], "-", color=C_PM, lw=2.5, label="Moment / motor")
        axes[1].axhline(0, color="black", lw=0.5)
        style(axes[1], "🔴 PM MOTOR – MOMENT NA MOTORE", "Moment [N·m]", "#CC0000")

        # Graf 3: IND rýchlosť
        axes[2].plot(t_id[m_id], sp_id[m_id], "--", color=C_SP, lw=2, label="SP – Žiadaná")
        axes[2].plot(t_id[m_id], pv_id[m_id], "-", color=C_IND, lw=2.5, label="PV – Skutočná")
        axes[2].axhline(_sp, color=C_SP, lw=1, ls=":", alpha=0.5)
        axes[2].set_ylim(bottom=-50)
        style(axes[2], "🔵 INDUKČNÝ MOTOR – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "#4444cc")

        # Graf 4: IND moment
        axes[3].plot(t_id[m_id], tq_id[m_id], "-", color=C_IND, lw=2.5, label="Moment / motor")
        axes[3].axhline(0, color="black", lw=0.5)
        style(axes[3], "🔵 INDUKČNÝ MOTOR – MOMENT NA MOTORE", "Moment [N·m]", "#4444cc")

        # Graf 5: Porovnanie
        axes[4].plot(t_pm[m_pm], sp_pm[m_pm], "--", color=C_SP, lw=2, label="SP – Žiadaná")
        axes[4].plot(t_pm[m_pm], pv_pm[m_pm], "-", color=C_PM, lw=2.5, label="🔴 PM Motor")
        axes[4].plot(t_id[m_id], pv_id[m_id], "-", color=C_IND, lw=2.5, label="🔵 Indukčný Motor")
        axes[4].set_ylim(bottom=-50)
        style(axes[4], "⚡ POROVNANIE: PM vs INDUKČNÝ – RÝCHLOSŤ HRIADELE", "Rýchlosť [RPM]", "black")

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        # ─── TABUĽKA ────────────────────────────────────────────────────────
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
        st.dataframe(df, use_container_width=True, height=400)

        # ─── POROVNÁVACIA ANALÝZA ───────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🔍 POROVNÁVACIA ANALÝZA")
        
        anal_col1, anal_col2 = st.columns(2)
        
        with anal_col1:
            st.markdown("**🔴 PM Motor:**")
            st.info(f"""
**Finálna rýchlosť:** {pv_pm[-1]:.0f} RPM

**Chyba:** {abs(pv_pm[-1] - _sp):.1f} RPM

**Max moment:** {np.max(np.abs(tq_pm)):.2f} N·m

**Čas ustálenia:** ~{np.where(np.abs(pv_pm - _sp) < 10)[0][0] * dt if np.any(np.abs(pv_pm - _sp) < 10) else _tsim:.2f} s

**Účinnosť:** 97 %

**Výhody:** Rýchlejšia odozva, vyššia účinnosť
            """)
        
        with anal_col2:
            st.markdown("**🔵 Indukčný Motor:**")
            st.info(f"""
**Finálna rýchlosť:** {pv_id[-1]:.0f} RPM

**Chyba:** {abs(pv_id[-1] - _sp):.1f} RPM

**Max moment:** {np.max(np.abs(tq_id)):.2f} N·m

**Čas ustálenia:** ~{np.where(np.abs(pv_id - _sp) < 10)[0][0] * dt if np.any(np.abs(pv_id - _sp) < 10) else _tsim:.2f} s

**Účinnosť:** 93 %

**Výhody:** Robustnejší, jednoduchší, lacnejší
            """)

        st.success("✅ Analýza hotová!")

    else:
        st.warning("⚠️ Najskôr prejdi do záložky 🎮 VÝPOČET a klikni ▶️ SPUSTIŤ VÝPOČET")

    st.info("💡 Zmeň parametre v ⚙️ PARAMETRE, potom opäť klikni ▶️ SPUSTIŤ VÝPOČET")
