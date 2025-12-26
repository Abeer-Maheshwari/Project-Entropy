import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import math
import time
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# --- CONFIG ---
st.set_page_config(page_title="ENTROPY: INTELLIGENT", layout="wide")

# --- HARDCODED FALLBACKS FOR DEMO STABILITY ---
# --- HARDCODED FALLBACKS FOR DEMO STABILITY ---
FALLBACK_CITIES = {
    # NORTH AMERICA
    "new york": (40.7128, -74.0060), "nyc": (40.7128, -74.0060),
    "san francisco": (37.7749, -122.4194), "sf": (37.7749, -122.4194),
    "austin": (30.2672, -97.7431),
    "seattle": (47.6062, -122.3321),
    "chicago": (41.8781, -87.6298),
    "los angeles": (34.0522, -118.2437), "la": (34.0522, -118.2437),
    "toronto": (43.6532, -79.3832),
    "montreal": (45.5017, -73.5673),
    "vancouver": (49.2827, -123.1207),
    "mexico city": (19.4326, -99.1332),

    # SOUTH AMERICA
    "sao paulo": (-23.5505, -46.6333),
    "rio": (-22.9068, -43.1729),
    "buenos aires": (-34.6037, -58.3816),
    "santiago": (-33.4489, -70.6693),
    "bogota": (4.7110, -74.0721),

    # EUROPE
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "berlin": (52.5200, 13.4050),
    "frankfurt": (50.1109, 8.6821),
    "amsterdam": (52.3676, 4.9041),
    "dublin": (53.3498, -6.2603),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "zurich": (47.3769, 8.5417),
    "stockholm": (59.3293, 18.0686),
    "oslo": (59.9139, 10.7522),
    "helsinki": (60.1699, 24.9384),
    "warsaw": (52.2297, 21.0122),
    "kyiv": (50.4501, 30.5234),
    "moscow": (55.7558, 37.6173),

    # ASIA
    "tokyo": (35.6762, 139.6503),
    "singapore": (1.3521, 103.8198),
    "hong kong": (22.3193, 114.1694), "hk": (22.3193, 114.1694),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "seoul": (37.5665, 126.9780),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "delhi": (28.7041, 77.1025),
    "jakarta": (-6.2088, 106.8456),
    "bangkok": (13.7563, 100.5018),
    "taipei": (25.0330, 121.5654),

    # MIDDLE EAST
    "dubai": (25.2048, 55.2708),
    "abu dhabi": (24.4539, 54.3773),
    "tel aviv": (32.0853, 34.7818),
    "riyadh": (24.7136, 46.6753),
    "istanbul": (41.0082, 28.9784),

    # AFRICA
    "cape town": (-33.9249, 18.4241),
    "johannesburg": (-26.2041, 28.0473),
    "lagos": (6.5244, 3.3792),
    "cairo": (30.0444, 31.2357),
    "nairobi": (-1.2921, 36.8219),

    # OCEANIA
    "sydney": (-33.8688, 151.2093),
    "melbourne": (-37.8136, 144.9631),
    "auckland": (-36.8485, 174.7633)
}

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {background-color: #050505;}
    .metric-card {
        background: rgba(20, 20, 20, 0.9); border-left: 4px solid #00CC96;
        padding: 15px; margin-bottom: 10px; border-radius: 5px;
    }
    .big-stat {font-size: 1.8rem; font-weight: bold; color: #fff;}
    .sub-stat {color: #888; font-size: 0.9rem;}
    /* Highlight Input */
    div[data-baseweb="input"] {border: 1px solid #555; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- INIT SESSION STATE ---
if 'user_loc' not in st.session_state:
    st.session_state['user_loc'] = {"name": "New York City", "lat": 40.7128, "lon": -74.0060}

# --- HYPERSCALE DATASET (120+ Locations) ---
# Format: ID, Name, Lat, Lon, Base Cost ($/kWh), Carbon Intensity (gCO2/kWh)
RAW_NODES = [
    # === NORTH AMERICA (USA) ===
    ("US-VA", "Ashburn (AWS East)", 39.0438, -77.4874, 0.12, 380),
    ("US-OH", "Columbus (AWS Ohio)", 40.4173, -82.9071, 0.11, 450),
    ("US-CA-N", "San Jose (Silicon Valley)", 37.3382, -121.8863, 0.16, 220),
    ("US-CA-S", "Los Angeles", 34.0522, -118.2437, 0.18, 260),
    ("US-OR", "The Dalles (Google)", 45.5946, -121.1787, 0.06, 50),
    ("US-WA", "Seattle (Azure West)", 47.6062, -122.3321, 0.07, 40), # Hydro
    ("US-TX-A", "Austin (Tesla)", 30.2672, -97.7431, 0.09, 410),
    ("US-TX-D", "Dallas/Fort Worth", 32.7767, -96.7970, 0.10, 420),
    ("US-TX-H", "Houston", 29.7604, -95.3698, 0.11, 440),
    ("US-IL", "Chicago (Lakeside)", 41.8781, -87.6298, 0.13, 390),
    ("US-NY", "New York (NJ Edge)", 40.7128, -74.0060, 0.19, 290),
    ("US-FL", "Miami (LATAM Gateway)", 25.7617, -80.1918, 0.14, 400),
    ("US-GA", "Atlanta", 33.7490, -84.3880, 0.11, 380),
    ("US-AZ", "Phoenix", 33.4484, -112.0740, 0.10, 350),
    ("US-NV", "Las Vegas (Switch)", 36.1699, -115.1398, 0.09, 150), # Solar
    ("US-UT", "Salt Lake City", 40.7608, -111.8910, 0.08, 480),
    ("US-IA", "Des Moines (Facebook)", 41.5868, -93.6250, 0.08, 300),
    ("US-NC", "Raleigh", 35.7796, -78.6382, 0.10, 360),
    ("US-CO", "Denver", 39.7392, -104.9903, 0.12, 550),

    # === NORTH AMERICA (Canada & Mexico) ===
    ("CA-QC", "Montreal (Hydro)", 45.5017, -73.5673, 0.05, 20),
    ("CA-ON", "Toronto", 43.6532, -79.3832, 0.11, 80),
    ("CA-BC", "Vancouver", 49.2827, -123.1207, 0.09, 30),
    ("CA-AB", "Calgary", 51.0447, -114.0719, 0.10, 600), # Coal/Gas
    ("MX-QT", "Queretaro", 20.5888, -100.3899, 0.13, 450),
    ("MX-MC", "Mexico City", 19.4326, -99.1332, 0.14, 480),

    # === SOUTH AMERICA ===
    ("BR-SP", "Sao Paulo", -23.5505, -46.6333, 0.14, 100),
    ("BR-RJ", "Rio de Janeiro", -22.9068, -43.1729, 0.15, 120),
    ("CL-ST", "Santiago", -33.4489, -70.6693, 0.13, 280),
    ("CO-BG", "Bogota", 4.7110, -74.0721, 0.12, 150),
    ("AR-BA", "Buenos Aires", -34.6037, -58.3816, 0.16, 350),
    ("PE-LI", "Lima", -12.0464, -77.0428, 0.15, 200),
    
    # === EUROPE (Western) ===
    ("GB-LD", "London (Slough)", 51.5074, -0.1278, 0.22, 210),
    ("GB-CW", "Cardiff (Wales)", 51.4816, -3.1791, 0.20, 190),
    ("IE-DB", "Dublin (Tech Hub)", 53.3498, -6.2603, 0.19, 350),
    ("NL-AM", "Amsterdam", 52.3676, 4.9041, 0.24, 320),
    ("NL-EM", "Eemshaven (Google)", 53.4333, 6.8333, 0.22, 300),
    ("DE-FR", "Frankfurt", 50.1109, 8.6821, 0.28, 400),
    ("DE-MU", "Munich", 48.1351, 11.5820, 0.26, 380),
    ("DE-BE", "Berlin", 52.5200, 13.4050, 0.29, 450),
    ("FR-PA", "Paris", 48.8566, 2.3522, 0.18, 55), # Nuclear
    ("FR-MA", "Marseille (Subsea Hub)", 43.2965, 5.3698, 0.19, 60),
    ("CH-ZU", "Zurich", 47.3769, 8.5417, 0.15, 30),
    ("BE-BR", "Brussels", 50.8503, 4.3517, 0.22, 180),
    ("AT-VI", "Vienna", 48.2082, 16.3738, 0.21, 150),

    # === EUROPE (Nordics) ===
    ("IS-RE", "Reykjavik", 64.1466, -21.9426, 0.04, 0), # Pure Green
    ("NO-OS", "Oslo", 59.9139, 10.7522, 0.05, 15),
    ("NO-ST", "Stavanger", 58.9690, 5.7331, 0.05, 15),
    ("SE-ST", "Stockholm", 59.3293, 18.0686, 0.07, 25),
    ("SE-LU", "Lulea (Arctic)", 65.5848, 22.1567, 0.04, 10),
    ("FI-HE", "Helsinki", 60.1699, 24.9384, 0.11, 80),
    ("FI-HA", "Hamina", 60.5693, 27.1981, 0.10, 80),
    ("DK-CP", "Copenhagen", 55.6761, 12.5683, 0.30, 120), # Expensive but Green

    # === EUROPE (Southern/Eastern) ===
    ("ES-MA", "Madrid", 40.4168, -3.7038, 0.21, 190),
    ("ES-BA", "Barcelona", 41.3851, 2.1734, 0.22, 200),
    ("PT-LI", "Lisbon", 38.7223, -9.1393, 0.19, 160),
    ("IT-MI", "Milan", 45.4642, 9.1900, 0.23, 300),
    ("IT-RO", "Rome", 41.9028, 12.4964, 0.24, 320),
    ("PL-WA", "Warsaw", 52.2297, 21.0122, 0.17, 750), # Coal
    ("CZ-PR", "Prague", 50.0755, 14.4378, 0.18, 500),
    ("HU-BU", "Budapest", 47.4979, 19.0402, 0.16, 350),
    ("RO-BU", "Bucharest", 44.4268, 26.1025, 0.15, 400),
    ("GR-AT", "Athens", 37.9838, 23.7275, 0.20, 550),

    # === ASIA (East) ===
    ("JP-TK", "Tokyo", 35.6762, 139.6503, 0.20, 480),
    ("JP-OS", "Osaka", 34.6937, 135.5023, 0.19, 470),
    ("KR-SE", "Seoul", 37.5665, 126.9780, 0.12, 520),
    ("KR-BU", "Busan", 35.1796, 129.0756, 0.11, 510),
    ("CN-BJ", "Beijing", 39.9042, 116.4074, 0.13, 800),
    ("CN-SH", "Shanghai", 31.2304, 121.4737, 0.14, 650),
    ("CN-HK", "Hong Kong", 22.3193, 114.1694, 0.18, 550),
    ("TW-TP", "Taipei", 25.0330, 121.5654, 0.13, 500),

    # === ASIA (South/Southeast) ===
    ("SG-SG", "Singapore", 1.3521, 103.8198, 0.25, 490),
    ("IN-MU", "Mumbai", 19.0760, 72.8777, 0.10, 700),
    ("IN-HY", "Hyderabad", 17.3850, 78.4867, 0.09, 710),
    ("IN-BA", "Bangalore", 12.9716, 77.5946, 0.10, 680),
    ("IN-DE", "New Delhi", 28.6139, 77.2090, 0.11, 750),
    ("ID-JK", "Jakarta", -6.2088, 106.8456, 0.11, 600),
    ("MY-KL", "Kuala Lumpur", 3.1390, 101.6869, 0.10, 550),
    ("TH-BK", "Bangkok", 13.7563, 100.5018, 0.12, 500),
    ("VN-HC", "Ho Chi Minh City", 10.8231, 106.6297, 0.11, 580),
    ("VN-HA", "Hanoi", 21.0285, 105.8542, 0.10, 600),
    ("PH-MA", "Manila", 14.5995, 120.9842, 0.15, 450),

    # === MIDDLE EAST ===
    ("AE-DU", "Dubai", 25.2048, 55.2708, 0.08, 600),
    ("AE-AB", "Abu Dhabi", 24.4539, 54.3773, 0.08, 600),
    ("SA-RI", "Riyadh", 24.7136, 46.6753, 0.06, 650),
    ("QA-DO", "Doha", 25.2854, 51.5310, 0.07, 680),
    ("BH-MA", "Manama", 26.0667, 50.5577, 0.07, 620),
    ("IL-TA", "Tel Aviv", 32.0853, 34.7818, 0.16, 400),
    ("TR-IS", "Istanbul", 41.0082, 28.9784, 0.14, 450),

    # === AFRICA ===
    ("ZA-CT", "Cape Town", -33.9249, 18.4241, 0.15, 800),
    ("ZA-JO", "Johannesburg", -26.2041, 28.0473, 0.14, 850),
    ("NG-LA", "Lagos", 6.5244, 3.3792, 0.18, 550),
    ("KE-NA", "Nairobi", -1.2921, 36.8219, 0.14, 200),
    ("EG-CA", "Cairo", 30.0444, 31.2357, 0.11, 500),
    ("MA-CA", "Casablanca", 33.5731, -7.5898, 0.13, 450),

    # === OCEANIA ===
    ("AU-SY", "Sydney", -33.8688, 151.2093, 0.21, 680),
    ("AU-ME", "Melbourne", -37.8136, 144.9631, 0.20, 700),
    ("AU-PE", "Perth", -31.9505, 115.8605, 0.19, 600),
    ("AU-BR", "Brisbane", -27.4698, 153.0251, 0.20, 650),
    ("NZ-AK", "Auckland", -36.8485, 174.7633, 0.12, 100)
]

# --- LOGIC ---

def update_user_location():
    """Bulletproof Geocoding: Local Cache -> API Retry"""
    user_input = st.session_state.loc_input
    if not user_input: return
    
    clean_input = user_input.lower().strip()

    # STRATEGY 1: CHECK LOCAL CACHE (Instant & Offline-Safe)
    if clean_input in FALLBACK_CITIES:
        lat, lon = FALLBACK_CITIES[clean_input]
        st.session_state['user_loc'] = {
            "name": user_input.title(), 
            "lat": lat,
            "lon": lon
        }
        return # Success! Skip the API.

    # STRATEGY 2: API WITH RETRY
    # Use a specific user agent to avoid blocking
    geolocator = Nominatim(user_agent="entropy_hackathon_demo_v1")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Add a slight delay to be polite to the API
            time.sleep(1) 
            location = geolocator.geocode(user_input, timeout=10)
            
            if location:
                st.session_state['user_loc'] = {
                    "name": location.address.split(",")[0], 
                    "lat": location.latitude,
                    "lon": location.longitude
                }
                return # Success
            else:
                st.error(f"City not found. Try 'London' or 'Tokyo'.")
                return
                
        except (GeocoderTimedOut, GeocoderServiceError):
            if attempt == max_retries - 1:
                st.error("Geocoding API is down. Please use a major city (London, Paris, SF).")
            continue # Try again

@st.cache_data(ttl=600)
def fetch_global_weather():
    results = []
    for idx, (nid, name, lat, lon, cost, carbon) in enumerate(RAW_NODES):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            r = requests.get(url, timeout=1).json()
            temp = r['current_weather']['temperature']
        except: temp = 20
        results.append({"id": nid, "name": name, "lat": lat, "lon": lon, "base_cost": cost, "carbon": carbon, "live_temp": temp})
    return results

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_scores(data, job_type, u_lat, u_lon):
    scored = []
    for node in data:
        # Physics
        excess_heat = max(0, node['live_temp'] - 15)
        pue = 1.0 + (excess_heat * 0.015)
        real_cost = node['base_cost'] * pue
        
        # Latency
        dist = calculate_haversine(u_lat, u_lon, node['lat'], node['lon'])
        latency = dist * 0.02
        
        # Score
        if job_type == "TRAINING":
            score = (real_cost * 1000) + (node['carbon'] / 2)
            color_scale = [0, 255, 100]
        else: # INFERENCE
            lat_penalty = max(0, latency - 50) * 2
            score = (real_cost * 500) + lat_penalty
            color_scale = [0, 150, 255]

        if score < 150: color = [*color_scale, 200]
        elif score < 300: color = [255, 200, 0, 200]
        else: color = [255, 50, 50, 200]

        scored.append({**node, "real_cost": round(real_cost,4), "latency": int(latency), "score": round(score,1), "color": color, "radius": 200000 if score < 150 else 60000})
    return pd.DataFrame(scored)

# --- UI ---

st.title("ENTROPY: INTELLIGENT ROUTER")

# 1. CONTROLS
c_job, c_user, c_input = st.columns([1, 1.5, 1.5])

with c_job:
    st.markdown("### Workload")
    job_type = st.radio("Type:", ["TRAINING (Batch)", "INFERENCE (Real-Time)"])
    mode_key = "TRAINING" if "TRAINING" in job_type else "INFERENCE"

with c_user:
    st.markdown("### Origin")
    st.info(f"**{st.session_state['user_loc']['name']}**")

with c_input:
    st.markdown("### Change Location")
    # Trigger update on Enter
    st.text_input("Enter City", key="loc_input", on_change=update_user_location)

# 2. PROCESS
raw_data = fetch_global_weather()
u_lat = st.session_state['user_loc']['lat']
u_lon = st.session_state['user_loc']['lon']

df = calculate_scores(raw_data, mode_key, u_lat, u_lon)
winner = df.loc[df['score'].idxmin()]

# 3. MAP (FIXED: Dynamic Camera)
# Use user's lat/lon to center the map
view_state = pdk.ViewState(
    latitude=u_lat, 
    longitude=u_lon, 
    zoom=2, 
    pitch=30
)

layer_nodes = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius="radius",
    pickable=True,
    opacity=0.8,
    radius_min_pixels=5,
    radius_max_pixels=40
)

# Active Route
arc_data = pd.DataFrame([{"source": [u_lon, u_lat], "target": [winner['lon'], winner['lat']]}])
layer_arc = pdk.Layer(
    "ArcLayer",
    arc_data,
    get_source_position="source",
    get_target_position="target",
    get_source_color=[255, 255, 255, 150],
    get_target_color=winner['color'],
    get_width=6,
    get_tilt=15
)

st.pydeck_chart(pdk.Deck(
    layers=[layer_nodes, layer_arc],
    initial_view_state=view_state,
    map_style=pdk.map_styles.CARTO_DARK,
    tooltip={"text": "{name}\nTemp: {live_temp}°C\nLatency: {latency}ms\nCost: ${real_cost}"}
))

# 4. STATS
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="sub-stat">OPTIMAL NODE</div>
        <div class="big-stat" style="color:#00FF99">{winner['name']}</div>
        <div class="sub-stat">Score: {winner['score']}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    lat_color = "#FF4B4B" if winner['latency'] > 100 else "#00CC96"
    st.markdown(f"""
    <div class="metric-card">
        <div class="sub-stat">NETWORK LATENCY</div>
        <div class="big-stat" style="color:{lat_color}">{winner['latency']} ms</div>
        <div class="sub-stat">From {st.session_state['user_loc']['name']}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="sub-stat">REAL COST</div>
        <div class="big-stat">${winner['real_cost']}</div>
        <div class="sub-stat">per kWh (Inc. Cooling)</div>
    </div>
    """, unsafe_allow_html=True)