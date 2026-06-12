import streamlit as st
import pandas as pd
import folium
import requests
import time
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import google.generativeai as genai
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ----------------------------
# INIT DB
# ----------------------------
def init_db():
    conn = sqlite3.connect("bookings.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pickup TEXT,
        dropoff TEXT,
        distance REAL,
        time REAL,
        fare REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------------------------
# SAVE BOOKING
# ----------------------------
def save_booking(pickup, dropoff, distance, time_taken, fare):
    conn = sqlite3.connect("bookings.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO bookings (pickup, dropoff, distance, time, fare, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (pickup, dropoff, distance, time_taken, fare))

    conn.commit()
    conn.close()

# ----------------------------
# PDF GENERATOR
# ----------------------------
def generate_pdf(booking_id, pickup, dropoff, distance, time_taken, fare):
    file_name = f"booking_{booking_id}.pdf"

    c = canvas.Canvas(file_name, pagesize=letter)
    c.drawString(100, 750, "SMART FARE CONTRACT")
    c.drawString(100, 720, f"Booking ID: {booking_id}")
    c.drawString(100, 700, f"Pickup: {pickup}")
    c.drawString(100, 680, f"Drop: {dropoff}")
    c.drawString(100, 660, f"Distance: {distance:.2f} KM")
    c.drawString(100, 640, f"Time: {time_taken:.0f} min")
    c.drawString(100, 620, f"Fare: ₹{fare}")
    c.drawString(100, 600, "Status: LOCKED")

    c.save()
    return file_name

# ----------------------------
# GEMINI SETUP
# ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Smart Fare Contract", page_icon="🚕", layout="wide")
st.markdown("""
<style>

.stApp{
    background:#0f172a;
    color:white;
}

.block-container{
    max-width:1600px;
}

h1,h2,h3,h4{
    color:#00f5d4 !important;
}

.card{
    background:#03045e;
    padding:20px;
    border-radius:20px;
    border:1px solid rgba(0,245,212,0.2);
    box-shadow:0 0 25px rgba(0,245,212,0.08);
}

.glow-card{
    background:#03045e;
    padding:20px;
    border-radius:20px;
    border:1px solid #00f5d4;
    box-shadow:0 0 30px rgba(0,245,212,0.25);
}

.stButton > button{
    background:linear-gradient(
        90deg,
        #00b4d8,
        #00f5d4
    );
    color:black;
    font-weight:bold;
    border:none;
    border-radius:12px;
}

[data-testid="stMetric"]{
    background:#03045e;
    padding:20px;
    border-radius:16px;
    border:1px solid rgba(0,245,212,.2);
}

.stTextInput input{
    background:#03045e !important;
    color:white !important;
}

.stSelectbox div[data-baseweb="select"]{
    background:#03045e;
}

button[data-baseweb="tab"][aria-selected="true"]{
    color:#00f5d4 !important;
}

</style>
""", unsafe_allow_html=True)
# ----------------------------
# LOCATION
# ----------------------------
def get_coordinates(place):
    locations = {
        "ukkadam": (10.9916, 76.9610),
        "gandhipuram": (11.0183, 76.9675),
        "rs puram": (11.0089, 76.9446),
        "airport": (11.0300, 77.0434),
        "peelamedu": (11.0280, 77.0170),
        "saravanampatti": (11.0820, 77.0010),
        "kgisl": (11.0905, 77.0015),
        "codissia": (11.0402, 77.0408)
    }
    return locations.get(place.strip().lower())

# ----------------------------
# ROUTE API
# ----------------------------
def get_route(start, end):
    url = f"https://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    return requests.get(url).json()

# ----------------------------
# SESSION STATE
# ----------------------------
if "generated" not in st.session_state:
    st.session_state.generated = False

if "route_data" not in st.session_state:
    st.session_state.route_data = None

if "fare_data" not in st.session_state:
    st.session_state.fare_data = None

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None
# ----------------------------
# LOGIN SESSION
# ----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

# ----------------------------
# LOGIN PAGE
# ----------------------------

if not st.session_state.logged_in:

    st.markdown("""
<h1 style='font-size:54px;
color:#00f5d4'>
🚕 Smart Fare AI
</h1>

<p style='color:#94a3b8'>
AI Powered Ride Monitoring
</p>

<p style='color:gray;font-size:18px'>
Green Mobility • Transparent Pricing
</p>
""", unsafe_allow_html=True)

    users = {
    "customer": {
        "password": "1234",
        "role": "Customer"
    },
    "driver": {
        "password": "1234",
        "role": "Driver"
    }
}

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):
    
     if username.lower() in users:

        if users[username.lower()]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.role = users[username.lower()]["role"]

            st.rerun()

    st.error("Invalid Credentials")

    st.stop() 
col1,col2 = st.columns([8,1])

with col1:
    st.title(
        f"🚕 Smart Fare AI Console ({st.session_state.role})"
    )

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()
# ----------------------------
# TABS
# ----------------------------

if st.session_state.role == "Customer":

    tab1, tab2, tab3 = st.tabs([
        "🚗 Booking",
        "📊 Analytics",
        "📜 History"
    ])

    # ======================================
    # BOOKING TAB
    # ======================================
    with tab1:

        st.markdown("## 🚗 Book Your Ride")

        col1, col2 = st.columns(2)

        with col1:
            pickup = st.selectbox(
                "Pickup",
                ["ukkadam","gandhipuram","rs puram","airport",
                 "peelamedu","saravanampatti","kgisl","codissia"]
            )

        with col2:
            dropoff = st.selectbox(
                "Drop",
                ["ukkadam","gandhipuram","rs puram","airport",
                 "peelamedu","saravanampatti","kgisl","codissia"]
            )

        if pickup == dropoff:
            st.warning("Pickup and Drop cannot be same!")
        else:

            start = get_coordinates(pickup)
            end = get_coordinates(dropoff)

            st.markdown("### 🚗 Select Ride Type")

            ride_type = st.radio(
                "",
                ["Bike", "Mini", "Sedan", "SUV"],
                horizontal=True
            )

            rates = {
                "Bike": 8,
                "Mini": 10,
                "Sedan": 12,
                "SUV": 15
            }

            generate = st.button("🔒 Generate Fare Contract")

            if generate:

                route_data = get_route(start, end)

                distance = route_data["routes"][0]["distance"] / 1000
                duration = route_data["routes"][0]["duration"] / 60

                fare = round(
                    40 +
                    distance * rates[ride_type] +
                    duration * 1.2
                )

                save_booking(
                    pickup,
                    dropoff,
                    distance,
                    duration,
                    fare
                )

                booking_id = int(time.time()) % 10000

                pdf_file = generate_pdf(
                    booking_id,
                    pickup,
                    dropoff,
                    distance,
                    duration,
                    fare
                )

                st.session_state.route_data = route_data

                st.session_state.fare_data = {
                    "distance": distance,
                    "time": duration,
                    "fare": fare
                }

                st.session_state.pdf_file = pdf_file
                st.session_state.generated = True

                prompt = f"""
                Pickup: {pickup}
                Drop: {dropoff}
                Distance: {distance:.2f}
                Time: {duration:.0f}
                Fare: ₹{fare}

                Explain fairness of pricing.
                """

                try:
                    res = model.generate_content(prompt)
                    st.session_state.explanation = res.text
                except:
                    st.session_state.explanation = "Transparent pricing applied"

            # ---------------- MAP ----------------

            if (
                st.session_state.generated
                and
                st.session_state.route_data
            ):

                route_data = st.session_state.route_data

                coords = route_data["routes"][0]["geometry"]["coordinates"]

                route_points = [
                    [c[1], c[0]]
                    for c in coords
                ]

                m = folium.Map(
    location=start,
    zoom_start=12,
    tiles="CartoDB dark_matter"
)

                folium.Marker(start).add_to(m)
                folium.Marker(end).add_to(m)

                folium.PolyLine(
                    route_points,
                    color="green",
                    weight=5
                ).add_to(m)

                st_folium(
                    m,
                    use_container_width=True,
                    height=450
                )

                data = st.session_state.fare_data

                st.markdown(f"""
                <div class="card">

                <h2>🚗 Trip Summary</h2>

                <p>📏 Distance :
                {data['distance']:.2f} KM</p>

                <p>⏱ ETA :
                {data['time']:.0f} min</p>

                <p>💰 Fare :
                ₹{data['fare']}</p>

                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="glow-card">

                <h3>👨 Driver Assigned</h3>

                <p><b>Name:</b> Jerome Bell</p>

                <p><b>Rating:</b> ⭐ 4.9</p>

                <p><b>Vehicle:</b> {ride_type}</p>

                <p style='color:#2e7d32'>
                Arriving in 4 mins
                </p>

                </div>
                """, unsafe_allow_html=True)

                st.info(
                    st.session_state.explanation
                )

                if st.session_state.pdf_file:

                    with open(
                        st.session_state.pdf_file,
                        "rb"
                    ) as f:

                        st.download_button(
                            "⬇ Download Fare Contract PDF",
                            f,
                            file_name=st.session_state.pdf_file,
                            mime="application/pdf"
                        )

    # ======================================
    # ANALYTICS TAB
    # ======================================

    with tab2:

        st.markdown("## 📊 Analytics")
        st.markdown("""
<div class="glow-card">

<h3>🧠 AI ANALYTICAL STREAM</h3>

<pre style="color:#00f5d4">

[AI] Surge prediction updated

[ML] Driver anomaly detected

[DATA] Route processed

[SYSTEM] All systems operational

</pre>

</div>
""", unsafe_allow_html=True)

        c1, c2, c3,c4 = st.columns(4)
        c1.metric(
        "TOTAL RIDES",
         "28,547"
           ) 

        c2.metric(
        "ACTIVE DRIVERS",
        "13,892"
         )

        c3.metric(
        "SURGE EVENTS",
         "156"
         )

        c4.metric(
         "REVENUE",
         "₹1.28L"
         )

         
        df = pd.DataFrame({
            "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
            "Contracts": [10,20,35,50,65,80]
        })

        st.line_chart(
            df.set_index("Month")
        )

    # ======================================
    # HISTORY TAB
    # ======================================

    with tab3:

        st.markdown("## 📜 Booking History")

        conn = sqlite3.connect(
            "bookings.db"
        )

        df = pd.read_sql_query(
            """
            SELECT *
            FROM bookings
            ORDER BY id DESC
            """,
            conn
        )

        conn.close()

        st.dataframe(
            df,
            use_container_width=True
        )

# ==========================================
# DRIVER DASHBOARD
# ==========================================

else:

    tab1, tab2 = st.tabs([
        "🚖 Driver Dashboard",
        "💰 Earnings"
    ])

    with tab1:

        st.markdown(
            "## 🚖 Driver Dashboard"
        )

        st.success("🟢 Online")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Trips Completed",
            "18"
        )

        c2.metric(
            "Today's Earnings",
            "₹2450"
        )

        c3.metric(
            "Rating",
            "⭐ 4.9"
        )

        st.markdown("""
        ### Current Ride

        Pickup : Ukkadam

        Drop : Airport

        Fare : ₹180
        """)

    with tab2:

        earnings = pd.DataFrame({
            "Day":[
                "Mon","Tue","Wed",
                "Thu","Fri"
            ],
            "Revenue":[
                1200,1800,2200,
                2000,2450
            ]
        })

        st.line_chart(
            earnings.set_index("Day")
        )