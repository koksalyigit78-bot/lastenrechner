import streamlit as st

# --- KONFIGURATION ---
st.set_page_config(page_title="Levelup Training - Profi Rechner", page_icon="🏗️")

st.title("🏗️ Levelup Anschlag-Profi")
st.markdown("Berechnung nach **DGUV Information 209-021**")

# --- DATENBANKEN FÜR STANDARD-GRÖSSEN ---
# Hier hinterlegen wir echte Marktstandards, um Empfehlungen zu geben
standard_rundschlingen = {
    1000: "1000 kg (Violett)",
    2000: "2000 kg (Grün)",
    3000: "3000 kg (Gelb)",
    4000: "4000 kg (Grau)",
    5000: "5000 kg (Rot)",
    6000: "6000 kg (Braun)",
    8000: "8000 kg (Blau)",
    10000: "10000 kg (Orange)"
}

standard_kette_gk8 = {
    1120: "6 mm (1.12 t)",
    1500: "7 mm (1.5 t)",
    2000: "8 mm (2.0 t)",
    3150: "10 mm (3.15 t)",
    5300: "13 mm (5.3 t)",
    8000: "16 mm (8.0 t)",
    11200: "18 mm (11.2 t)",
    15000: "20 mm (15.0 t)"
}

material_liste = [
    "Rundschlingen (Chemiefaser)",
    "Rundstahlkette Güteklasse 8",
    "Rundstahlkette Güteklasse 10",
    "Rundstahlkette Güteklasse 4",
    "Rundstahlkette Güteklasse 2",
    "Endlose Chemiefaserhebebänder",
    "Litzenseile",
    "Naturfaserseile",
    "Kabelschlagseil-Grummets"
]

# --- HILFSFUNKTIONEN ---

def get_geometry_factor(effektive_straenge, winkel_str, symmetrisch):
    if winkel_str == "> 60° (Verboten!)": return 0
    
    # Unsymmetrie-Regel
    if not symmetrisch:
        if effektive_straenge <= 2: return 1.0 
        # Bei 3/4 Strängen unsymmetrisch -> Rechnet wie 2 Stränge
        basis_faktoren_2strang = {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0}
        return basis_faktoren_2strang[winkel_str]

    # Symmetrisch
    faktoren_tabelle = {
        1: {"0° (Vertikal)": 1.0, "0° - 45°": 1.0, "45° - 60°": 1.0},
        2: {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0},
        3: {"0° (Vertikal)": 3.0, "0° - 45°": 2.1, "45° - 60°": 1.5},
        4: {"0° (Vertikal)": 4.0, "0° - 45°": 2.1, "45° - 60°": 1.5}
    }
    # Sicherung für > 4 Stränge (Hängegang)
    safe_count = min(effektive_straenge, 4)
    return faktoren_tabelle[safe_count][winkel_str]

def finde_naechste_groesse(benoetigte_wll, material):
    # Diese Funktion sucht die passende Handelsgröße
    vorschlag = None
    
    if "Rundschlingen" in material or "Chemiefaserhebebänder" in material:
        for wll, name in standard_rundschlingen.items():
            if wll >= benoetigte_wll:
                vorschlag = name
                break
                
    elif "Güteklasse 8" in material:
        for wll, name in standard_kette_gk8.items():
            if wll >= benoetigte_wll:
                vorschlag = name
                break
    
    return vorschlag

# --- UI START ---
tab1, tab2 = st.tabs(["📦 Last berechnen (Ich habe Material)", "🔗 Material finden (Ich habe eine Last)"])

# ==========================================
# TAB 1: WAS KANN ICH HEBEN?
# ==========================================
with tab1:
    st.header("Vorhandenes Anschlagmittel prüfen")
    
    # Materialauswahl
    t1_mat = st.selectbox("Welches Anschlagmittel nutzt du?", material_liste, key="t1_mat")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        t1_wll_strang = st.number_input("WLL Einzelstrang (kg)", value=1000, step=100, help="Was steht auf dem Etikett/Anhänger?")
        t1_punkte = st.radio("Anzahl Anschlagpunkte", [1, 2, 3, 4], key="t1_p")
    
    with col_a2:
        t1_art = st.selectbox("Anschlagart", ["Direkter Zug", "Geschnürt (Schnürgang)", "Umgelegt (Hängegang)"], key="t1_art")
        t1_winkel = st.selectbox("Neigungswinkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t1_w")
        t1_sym = st.toggle("Symmetrische Last?", value=True, key="t1_sym")

    # Logik
    effektive_straenge = t1_punkte * 2 if t1_art == "Umgelegt (Hängegang)" else t1_punkte
    art_faktor = 0.8 if t1_art == "Geschnürt (Schnürgang)" else 1.0
    geom_faktor = get_geometry_factor(effektive_straenge, t1_winkel, t1_sym)

    st.divider()

    if geom_faktor == 0:
        st.error("⛔ STOPP: Winkel > 60° ist verboten!")
    else:
        max_last = t1_wll_strang * art_faktor * geom_faktor
        st.write(f"Du nutzt: **{t1_mat}**")
        st.success(f"### Maximale Last: {int(max_last)} kg")
        st.caption(f"Berechnungsfaktoren: Art {art_faktor} x Geometrie {geom_faktor} (M)")


# ==========================================
# TAB 2: WELCHES MITTEL BRAUCHE ICH?
# ==========================================
with tab2:
    st.header("Passendes Anschlagmittel finden")
    
    # 1. Material wählen
    st.info("Schritt 1: Was willst du benutzen?")
    t2_mat = st.selectbox("Material auswählen:", material_liste, key="t2_mat")
    
    # 2. Lastdaten
    st.info("Schritt 2: Wie schwer ist die Last & wie hängst du an?")
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        t2_last = st.number_input("Gewicht der Last (kg)", value=2500, step=100)
        t2_punkte = st.radio("Anzahl Anschlagpunkte", [1, 2, 3, 4], key="t2_p")
        
    with col_b2:
        t2_art = st.selectbox("Geplante Anschlagart", ["Direkter Zug", "Geschnürt (Schnürgang)", "Umgelegt (Hängegang)"], key="t2_art")
        t2_winkel = st.selectbox("Geplanter Winkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t2_w")
        t2_sym = st.toggle("Symmetrische Last?", value=True, key="t2_sym")

    # Logik
    effektive_straenge_req = t2_punkte * 2 if t2_art == "Umgelegt (Hängegang)" else t2_punkte
    art_faktor_req = 0.8 if t2_art == "Geschnürt (Schnürgang)" else 1.0
    geom_faktor_req = get_geometry_factor(effektive_straenge_req, t2_winkel, t2_sym)
    
    st.divider()
    
    if geom_faktor_req == 0:
        st.error("⛔ STOPP: Winkel > 60° ist verboten!")
    else:
        # Rückrechnung
        gesamt_faktor = art_faktor_req * geom_faktor_req
        benoetigte_wll = t2_last / gesamt_faktor
        
        st.subheader("Ergebnis:")
        st.write(f"Gesamt-Lastfaktor (M): **{round(gesamt_faktor, 2)}**")
        
        # Das wichtige Ergebnis: Was muss auf dem Etikett stehen?
        st.warning(f"Jeder einzelne Strang/Gurt muss eine WLL haben von mindestens:")
        st.title(f"{int(benoetigte_wll)} kg")
        
        # Intelligenter Vorschlag (Levelup Training Feature)
        vorschlag = finde_naechste_groesse(benoetigte_wll, t2_mat)
        
        if vorschlag:
            st.success(f"✅ **Levelup Empfehlung:** Nimm {t2_mat} der Größe:\n# {vorschlag}")
        else:
            st.info(f"Bitte prüfe die Traglasttabelle für {t2_mat}, ob eine Größe verfügbar ist, die > {int(benoetigte_wll)} kg trägt.")

# --- FOOTER ---
st.divider()
st.caption("Levelup Training App | Angaben gemäß DGUV Information 209-021 | Alle Werte ohne Gewähr.")
