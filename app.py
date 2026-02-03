import streamlit as st
import math

# --- KONFIGURATION & BRANDING ---
st.set_page_config(page_title="Levelup Training - Profi Rechner", page_icon="🏗️")

st.title("🏗️ Levelup Anschlag-Profi")
st.markdown("Interaktiver Rechner nach **DGUV Information 209-021**")

# --- ERWEITERTE DATENBANKEN ---
# Hier sind die Tragfähigkeiten (WLL) und die dazugehörigen Bezeichnungen/Dicken hinterlegt
datenbanken = {
    "Rundschlingen (Chemiefaser)": {
        1000: "1000 kg (Violett)", 
        2000: "2000 kg (Grün)", 
        3000: "3000 kg (Gelb)", 
        4000: "4000 kg (Grau)", 
        5000: "5000 kg (Rot)", 
        8000: "8000 kg (Blau)"
    },
    "Rundstahlkette Güteklasse 8": {
        1120: "6 mm (1.12 t)", 
        1500: "7 mm (1.5 t)", 
        2000: "8 mm (2.0 t)", 
        3150: "10 mm (3.15 t)", 
        5300: "13 mm (5.3 t)", 
        8000: "16 mm (8.0 t)"
    },
    "Litzenseile": {
        700: "8 mm", 
        1100: "10 mm", 
        1600: "12 mm", 
        2200: "14 mm", 
        2900: "16 mm", 
        3700: "18 mm", 
        4500: "20 mm", 
        5500: "22 mm"
    },
    "Kabelschlagseil-Grummets": {
        2500: "21 mm", 
        3400: "24 mm", 
        4400: "27 mm", 
        5500: "30 mm", 
        7900: "36 mm", 
        10800: "42 mm"
    }
}

material_liste = [
    "Rundschlingen (Chemiefaser)",
    "Rundstahlkette Güteklasse 8",
    "Rundstahlkette Güteklasse 10",
    "Rundstahlkette Güteklasse 4",
    "Rundstahlkette Güteklasse 2",
    "Litzenseile",
    "Kabelschlagseil-Grummets",
    "Naturfaserseile",
    "Endlose Chemiefaserhebebänder"
]

# --- HILFSFUNKTION FÜR DEN GEOMETRIEFAKTOR (M) ---
def get_geometry_factor(eff_straenge, winkel_str, symmetrisch):
    if winkel_str == "> 60° (Verboten!)": 
        return 0
    
    # DGUV-Regel bei Unsymmetrie: Nur 1 Strang (bei 2) oder 2 Stränge (bei 3/4) tragen die Last
    if not symmetrisch:
        if eff_straenge <= 2: 
            return 1.0 
        else:
            # Rechnet wie 2 Stränge im ungünstigsten Winkel
            faktoren_unsym = {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0}
            return faktoren_unsym[winkel_str]
    
    # Standard-Tabelle für symmetrische Last
    faktoren = {
        1: {"0° (Vertikal)": 1.0, "0° - 45°": 1.0, "45° - 60°": 1.0},
        2: {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0},
        3: {"0° (Vertikal)": 3.0, "0° - 45°": 2.1, "45° - 60°": 1.5},
        4: {"0° (Vertikal)": 4.0, "0° - 45°": 2.1, "45° - 60°": 1.5}
    }
    # Da rechnerisch im Hängegang mehr als 4 Stränge entstehen können, deckeln wir auf Faktor für 4
    safe_count = min(eff_straenge, 4)
    return faktoren[safe_count][winkel_str]

# --- HAUPT-NAVIGATION ---
tab1, tab2 = st.tabs(["📦 Was darf ich heben?", "🔗 Was brauche ich zum Heben?"])

# ==========================================
# MODUS 1: VORHANDENES MATERIAL PRÜFEN
# ==========================================
with tab1:
    st.header("Tragfähigkeits-Check")
    st.write("Berechne, wie schwer deine Last maximal sein darf.")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        t1_mat = st.selectbox("Anschlagmittel", material_liste, key="t1_m")
        t1_wll_label = st.number_input("WLL laut Etikett (kg)", value=1000, step=100)
        t1_anz_mittel = st.number_input("Anzahl eingesetzte Mittel", min_value=1, value=1, key="t1_n")
    
    with col_a2:
        t1_punkte = st.radio("Punkte pro Mittel", [1, 2, 3, 4], index=0, key="t1_p")
        t1_art = st.selectbox("Anschlagart", ["Direkter Zug", "Geschnürt", "Hängegang"], key="t1_a")
        t1_winkel = st.selectbox("Neigungswinkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t1_w")
        t1_sym = st.toggle("Symmetrisch?", value=True, key="t1_s")

    # Logik für Modus 1
    eff_pro_m = t1_punkte * 2 if t1_art == "Hängegang" else t1_punkte
    art_f = 0.8 if t1_art == "Geschnürt" else 1.0
    geom_f = get_geometry_factor(eff_pro_m, t1_winkel, t1_sym)
    
    st.divider()
    if geom_f == 0:
        st.error("⛔ UNZULÄSSIG: Neigungswinkel über 60°!")
    else:
        # Gesamtlast = (WLL * Art * Geo) * Anzahl der Mittel
        max_last_gesamt = (t1_wll_label * art_f * geom_f) * t1_anz_mittel
        st.success(f"### Zulässige Gesamtlast: {int(max_last_gesamt)} kg")
        st.info(f"Ein einzelnes Mittel trägt in dieser Konfiguration: {int(t1_wll_label * art_f * geom_f)} kg")

# ==========================================
# MODUS 2: PASSENDES MATERIAL FINDEN
# ==========================================
with tab2:
    st.header("Material-Konfigurator")
    st.write("Berechne, welche Dimension dein Anschlagmittel haben muss.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        t2_last = st.number_input("Gewicht der Last (kg)", value=5000, step=500)
        t2_anz_mittel = st.number_input("Anzahl der Mittel (z.B. 2 Gehänge)", min_value=1, value=1, key="t2_n")
        t2_punkte = st.radio("Punkte pro Mittel", [1, 2, 3, 4], index=1, key="t2_p")
        
    with col_b2:
        t2_mat = st.selectbox("Gewünschtes Material", material_liste, key="t2_m")
        t2_art = st.selectbox("Geplante Anschlagart", ["Direkter Zug", "Geschnürt", "Hängegang"], key="t2_a")
        t2_winkel = st.selectbox("Geplanter Winkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t2_w")
        t2_sym = st.toggle("Symmetrisch?", value=True, key="t2_s")

    # Logik für Modus 2
    eff_pro_m_req = t2_punkte * 2 if t2_art == "Hängegang" else t2_punkte
    art_f_req = 0.8 if t2_art == "Geschnürt" else 1.0
    geom_f_req = get_geometry_factor(eff_pro_m_req, t2_winkel, t2_sym)
    
    st.divider()
    if geom_f_req == 0:
        st.error("⛔ UNZULÄSSIG: Winkel über 60°!")
    else:
        # Erforderliche WLL pro Einzelstrang
        last_pro_mittel = t2_last / t2_anz_mittel
        erf_wll_strang = last_pro_mittel / (art_f_req * geom_f_req)
        
        # Suche in den Datenbanken
        empfehlung = None
        identifiziert = False
        if t2_mat in datenbanken:
            for wll_grenze, info in datenbanken[t2_mat].items():
                if wll_grenze >= erf_wll_strang:
                    empfehlung = info
                    identifiziert = True
                    break
        
        # Ergebnistext zusammenbauen
        st.subheader("Ergebnis:")
        ergebnis_text = f"Du benötigst **{t2_anz_mittel}x {t2_mat}** "
        
        if identifiziert:
            if "Litzenseile" in t2_mat or "Grummets" in t2_mat:
                ergebnis_text += f"mit mindestens **{empfehlung} Nenndicke**."
            else:
                ergebnis_text += f"der Größe **{empfehlung}**."
        else:
            ergebnis_text += f"mit einer Tragfähigkeit (WLL) von je mindestens **{int(erf_wll_strang)} kg** pro Strang."
            
        st.success(ergebnis_text)
        st.caption(f"Rechnerischer Bedarf pro Strang: {int(erf_wll_strang)} kg WLL.")

# --- FOOTER ---
st.divider()
st.markdown(f"© {2026} **Levelup Training** | Fachbereich Anschlagtechnik")
st.caption("Hinweis: Diese App ist eine Rechenhilfe. Vor jedem Hebevorgang ist eine Sichtprüfung der Anschlagmittel und eine Gefährdungsbeurteilung durchzuführen.")
