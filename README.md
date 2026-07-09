# SurgeShield-AI (Smart Fare AI)

An AI-assisted ride-hailing fare estimation and booking dashboard built with Streamlit. The app calculates transparent, distance-and-time-based fares, generates a downloadable fare contract, and uses the Gemini API to produce a plain-language fairness explanation for each fare — aimed at making dynamic/surge pricing more interpretable to riders.

## Overview

Dynamic pricing in ride-hailing platforms is often a black box to end users. SurgeShield-AI is a prototype exploring how an LLM can generate a transparent, human-readable justification alongside an algorithmic fare, so riders understand *why* a price is what it is rather than just seeing a number.

## Features

- **Route & fare calculation** — live routing via the OSRM API (distance + ETA) combined with a rate-card fare formula (base fare + distance rate + time rate, varying by vehicle type: Bike/Mini/Sedan/SUV)
- **AI-generated fare explanation** — calls Google's Gemini API to generate a natural-language rationale for the computed fare, aiming to improve pricing transparency
- **Interactive route map** — live pickup/drop visualization using Folium
- **Booking persistence** — bookings stored in a local SQLite database
- **PDF fare contracts** — auto-generated downloadable PDF receipt per booking
- **Dual dashboards** — separate Customer (booking, analytics, history) and Driver (trip status, earnings) views

## Tech Stack

- **Frontend/App**: Streamlit
- **Routing**: OSRM (Open Source Routing Machine) API
- **Mapping**: Folium + streamlit-folium
- **AI**: Google Gemini API (`gemini-2.5-flash`) for fare-fairness explanations
- **Database**: SQLite
- **PDF Generation**: ReportLab
- **Data handling**: Pandas

## Setup

```bash
git clone https://github.com/Vanitha-1111-ART/SurgeShield-AI.git
cd SurgeShield-AI
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:
GEMINI_API_KEY=your_api_key_here
Run the app:
```bash
streamlit run app.py
```

## Demo Login

This is a prototype with placeholder authentication for demonstration purposes (not production-secure):
- Customer: `customer` / `1234`
- Driver: `driver` / `1234`

## Notes & Limitations

- Locations are currently limited to a fixed set of Coimbatore-area coordinates for demo purposes
- Analytics dashboard figures (total rides, active drivers, revenue) are illustrative placeholder data, not live metrics
- Authentication is a simple demo login and not intended for production use
- Built as a prototype to explore AI-assisted pricing transparency, not a production-ready ride-hailing platform

## Future Improvements

- Replace fixed location list with live geocoding
- Real authentication (hashed passwords, session tokens)
- Connect analytics dashboard to actual booking data from the SQLite store
- Expand fairness-explanation prompting to flag potentially unfair or discriminatory pricing patterns

<img width="1440" height="920" alt="image" src="https://github.com/user-attachments/assets/c2b72806-d1d2-4ff2-bc25-ac697c2a9909" />
