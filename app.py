import streamlit as st

# --- KONFIGURATION ---
st.set_page_config(page_title="Levelup Training - Profi Rechner", page_icon="🏗️")

st.title("🏗️ Levelup Anschlag-Profi")
st.markdown("Berechnung nach **DGUV Information 209-021**")

# --- TAB-STRUKTUR ---
tab1, tab2 = st.tabs(["📦 Was kann ich heben?", "🔗 Welches Mittel brauche ich?"])

# --- HILFSFUNKTION: Lastfaktor (M) ---
def get_geometry_factor(anzahl_effektive_straenge, winkel_str, symmetrisch):
    # 1. Sicherheits-Check: Winkel > 60°
    if winkel_str == "> 60° (Verboten!)":
        return 0
    
    # 2. Asymmetrie-Check (DGUV Regel)
    if not symmetrisch:
        # Bei Unsymmetrie wird die Last rechnerisch nur von weniger Strängen getragen
        if anzahl_effektive_straenge <= 2:
            return 1.0 # Rechnet wie 1 Strang
        else:
            # Bei 3/4 Strängen unsymmetrisch -> Rechnet wie 2 Stränge
            # Wir nehmen den Faktor für 2 Stränge im entsprechenden Winkel
            basis_faktoren_2strang = {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0}
            return basis_faktoren_2strang[winkel_str]

    # 3. Normale Tabelle (Symmetrisch)
    # Hinweis: Falls durch Hängegang mehr als 4 Stränge entstehen,
    # bleibt der Faktor in der Regel bei max 4 tragenden Elementen oder muss gesondert betrachtet werden.
    # Für diese App begrenzen wir die Logik auf die Standard-Faktoren bis 4 Stränge,
    # da darüber hinaus oft Sonderberechnungen (Traversen) nötig sind.
    
    faktoren_tabelle = {
        1: {"0° (Vertikal)": 1.0, "0° - 45°": 1.0, "45° - 60°": 1.0},
        2: {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0},
        3: {"0° (Vertikal)": 3.0, "0° - 45°": 2.1, "45° - 60°": 1.5},
        4: {"0° (Vertikal)": 4.0, "0° - 45°": 2.1, "45° - 60°": 1.5}
    }
    
    # Fallback: Wenn > 4 Stränge (z.B. 4 Punkte im Hängegang = 8 Stränge), 
    # rechnet man sicherheitshalber oft nicht höher als mit Faktor für 4.
    safe_strang_count = min(anzahl_effektive_straenge, 4)
    
    return faktoren_tabelle[safe_strang_count][winkel_str]


# --- MODUS 1: VORHANDENES MITTEL PRÜFEN ---
with tab1:
    st.header("Maximale Last berechnen")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        t1_wll_strang = st.number_input("WLL Einzelstrang (kg)", value=1000, step=100, help="Tragfähigkeit laut Etikett für einen Strang")
        t1_punkte = st.radio("Anzahl Anschlagpunkte an der Last", [1, 2, 3, 4], key="t1_p")
    
    with col_a2:
        t1_art = st.selectbox("Anschlagart", ["Direkter Zug", "Geschnürt (Schnürgang)", "Umgelegt (Hängegang)"], key="t1_art")
        t1_winkel = st.selectbox("Neigungswinkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t1_w")
        t1_sym = st.toggle("Last hängt symmetrisch?", value=True, key="t1_sym")

    # --- LOGIK FÜR ANSCHLAGART ---
    art_faktor = 1.0
    effektive_straenge = t1_punkte

    if t1_art == "Geschnürt (Schnürgang)":
        art_faktor = 0.8  # Reduzierung auf 80%
        st.info("ℹ️ Schnürgang reduziert die Tragfähigkeit auf 80%.")
        
    elif t1_art == "Umgelegt (Hängegang)":
        # Hängegang verdoppelt die Anzahl der Stränge zum Haken
        effektive_straenge = t1_punkte * 2
        st.info(f"ℹ️ Hängegang: Aus {t1_punkte} Anschlagpunkten werden rechnerisch {effektive_straenge} Stränge zum Haken.")

    # Berechnung
    geom_faktor = get_geometry_factor(effektive_straenge, t1_winkel, t1_sym)
    
    st.divider()
    
    if geom_faktor == 0:
        st.error("STOPP! Neigungswinkel über 60° ist verboten.")
    else:
        # Formel: WLL * ArtFaktor * GeometrieFaktor
        max_last = t1_wll_strang * art_faktor * geom_faktor
        
        st.write(f"Geometrie-Faktor (für {effektive_straenge} Stränge): **{geom_faktor}**")
        st.write(f"Faktor Anschlagart: **{art_faktor}**")
        
        st.success(f"### Maximale Last: {int(max_last)} kg")
        
        if t1_art == "Umgelegt (Hängegang)":
            st.warning("⚠️ Wichtig beim Hängegang: Achte darauf, dass die Anschlagmittel am Kranhaken nicht übereinander liegen (Quetschgefahr)!")


# --- MODUS 2: ANSCHLAGMITTEL FINDEN ---
with tab2:
    st.header("Welches Mittel brauche ich?")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        t2_last = st.number_input("Gewicht der Last (kg)", value=2000, step=100)
        t2_punkte = st.radio("Geplante Anschlagpunkte", [1, 2, 3, 4], key="t2_p")
        
    with col_b2:
        t2_art = st.selectbox("Geplante Anschlagart", ["Direkter Zug", "Geschnürt (Schnürgang)", "Umgelegt (Hängegang)"], key="t2_art")
        t2_winkel = st.selectbox("Geplanter Winkel (β)", ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"], key="t2_w")
        t2_sym = st.toggle("Last hängt symmetrisch?", value=True, key="t2_sym")

    # --- LOGIK RÜCKWÄRTS ---
    art_faktor_req = 1.0
    effektive_straenge_req = t2_punkte

    if t2_art == "Geschnürt (Schnürgang)":
        art_faktor_req = 0.8
    elif t2_art == "Umgelegt (Hängegang)":
        effektive_straenge_req = t2_punkte * 2

    geom_faktor_req = get_geometry_factor(effektive_straenge_req, t2_winkel, t2_sym)
    
    st.divider()
    
    if geom_faktor_req == 0:
        st.error("STOPP! Neigungswinkel über 60° ist verboten.")
    else:
        # Rückrechnung: WLL_erforderlich = Last / (ArtFaktor * GeometrieFaktor)
        gesamt_faktor = art_faktor_req * geom_faktor_req
        benoetigte_wll = t2_last / gesamt_faktor
        
        st.write(f"Gesamt-Berechnungsfaktor: **{round(gesamt_faktor, 2)}**")
        st.warning(f"### Du benötigst Stränge mit mind:")
        st.header(f"WLL {int(benoetigte_wll)} kg")
        st.caption("Das ist die WLL, die auf dem Etikett des einzelnen Strangs stehen muss.")
