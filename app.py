import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Levelup Training - Smart Calc", page_icon="🏗️", layout="centered")

st.title("🏗️ Profi-Lastenrechner")
st.write("### Levelup Training: Sicherheit durch Präzision")

# --- NEU: WINKEL-MESS-TOOL (JavaScript Integration) ---
st.subheader("1. Neigungswinkel bestimmen")

# Ein kleiner JavaScript-Baustein, der auf die Handy-Sensoren zugreift
angle_sensor_html = """
<div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center;">
    <p>Handy flach an den Strang halten:</p>
    <h1 id="angle-display">0°</h1>
    <button onclick="requestPermission()" style="padding: 10px; border-radius: 5px; border: none; background: #ff4b4b; color: white;">Sensor aktivieren</button>
</div>

<script>
let angle = 0;
function requestPermission() {
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
        DeviceOrientationEvent.requestPermission()
            .then(permissionState => {
                if (permissionState === 'granted') {
                    window.addEventListener('deviceorientation', handleOrientation);
                }
            })
            .catch(console.error);
    } else {
        window.addEventListener('deviceorientation', handleOrientation);
    }
}

function handleOrientation(event) {
    // beta ist die Neigung nach vorne/hinten
    angle = Math.abs(Math.round(event.beta));
    document.getElementById('angle-display').innerText = angle + "°";
    // Wert an Streamlit zurückgeben (optional für Automatisierung)
}
</script>
"""

with st.expander("📷 Kamera/Sensor-Winkelmesser öffnen"):
    components.html(angle_sensor_html, height=200)
    st.caption("Hinweis: Halte dein Handy parallel zum Anschlagmittel. Der Winkel β wird zur Vertikalen gemessen.")



# --- EINGABEMASKE ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    material = st.selectbox("Material", ["Kette (GK 8)", "Drahtseil", "Hebeband"])
    anzahl = st.radio("Anzahl Stränge", [1, 2, 3, 4], horizontal=True)

with col2:
    wll_basis = st.number_input("WLL gerader Zug (kg)", value=1000)
    # Hier wählt der User basierend auf der Messung oben
    winkel_bereich = st.selectbox("Gemessener Winkelbereich (β)", 
                                 ["0° (Vertikal)", "0° - 45°", "45° - 60°", "> 60° (Verboten!)"])

symmetrie = st.toggle("Symmetrische Belastung", value=True)

# --- LOGIK ---
def berechne_wll(anzahl, bereich, basis_wll, symmetrisch):
    if bereich == "> 60° (Verboten!)":
        return 0
    
    # Faktoren nach DGUV 209-021
    faktoren = {
        1: {"0° (Vertikal)": 1.0, "0° - 45°": 1.0, "45° - 60°": 1.0},
        2: {"0° (Vertikal)": 2.0, "0° - 45°": 1.4, "45° - 60°": 1.0},
        3: {"0° (Vertikal)": 3.0, "0° - 45°": 2.1, "45° - 60°": 1.5},
        4: {"0° (Vertikal)": 4.0, "0° - 45°": 2.1, "45° - 60°": 1.5}
    }
    
    m = faktoren[anzahl][bereich]
    
    # Unsymmetrie-Regel
    if not symmetrisch:
        m = 1.0 if anzahl <= 2 else 1.0 # DGUV: Nur 1 Strang tragend
        
    return basis_wll * m

ergebnis = berechne_wll(anzahl, winkel_bereich, wll_basis, symmetrie)

# --- AUSGABE ---
st.divider()
if ergebnis == 0:
    st.error("### ❌ ACHTUNG: Winkel über 60° ist unzulässig!")
else:
    st.success(f"### Zulässige Tragfähigkeit: {int(ergebnis)} kg")
    st.balloons() if ergebnis > 5000 else None

st.info(f"**Levelup Training Tipp:** Bei einem Winkel von {winkel_bereich} beträgt der Lastfaktor M = {ergebnis/wll_basis if wll_basis > 0 else 0}.")
