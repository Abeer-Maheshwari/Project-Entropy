# ENTROPY: The Intelligent Workload Router

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB)](https://www.python.org/)
[![PyDeck](https://img.shields.io/badge/PyDeck-00C7B7)](https://pydeck.gl/)
[![Open-Meteo](https://img.shields.io/badge/Open--Meteo-Orange)](https://open-meteo.com/)
[![Geopy](https://img.shields.io/badge/Geopy-Green)](https://geopy.readthedocs.io/)

Entropy is a Proof-of-Concept for a next-generation load balancer. Instead of routing traffic to the nearest server, Entropy calculates the "Real Cost" of every compute job by analyzing Live Weather Data, Grid Carbon Intensity, and Spot Market Pricing across 120+ global data centers.

## Key Features

* **Global "Digital Twin":** Tracks real-time conditions for 120+ major data center hubs across 6 continents.
* **Intelligent Routing Algorithm:**
    * **Training Mode (Batch):** Ignores latency. Hunts for the absolute lowest cost and carbon footprint.
    * **Inference Mode (Real-Time):** Prioritizes low latency (<50ms) while optimizing for cost within a geofenced radius.
* **Live PUE Calculation:** Uses the Open-Meteo API to fetch live temperatures. It calculates a dynamic "Cooling Penalty" (PUE) for each site. Running servers in a 35°C desert is more expensive than in 5°C Norway.
* **Dynamic Geocoding:** Users can type any city name, and the system instantly recalculates the optimal route from that origin.
* **Interactive Visualization:** Built with PyDeck for 3D mapping.

## Getting Started

### Prerequisites

* Python 3.8+
* No API Keys required! (Uses Open-Meteo for weather and Nominatim for geocoding).

### Installation

1.  **Install dependencies:**
    ```bash
    pip install streamlit pydeck pandas numpy requests geopy
    ```

2.  **Run the application:**
    ```bash
    streamlit run entropy.py
    ```

3.  **Launch:** The app will open in your browser at `http://localhost:8501`.

## How to Use

1.  **Select Workload Type:**
    * Choose **"TRAINING"** to find the cheapest/greenest energy globally.
    * Choose **"INFERENCE"** to find the best node near you.
2.  **Set Origin:** Type your current city into the input box and hit Enter.
3.  **Analyze the Route:**
    * The Green Arc shows the optimal path for your data.
    * Red Dots on the map indicate high cost/carbon regions (avoided).
    * Green Dots indicate efficient regions (targeted).
4.  **View Stats:** Check the bottom metrics for real-time latency, PUE-adjusted cost, and carbon savings.

---
