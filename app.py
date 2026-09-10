import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder
import folium
from streamlit_folium import folium_static

# --- SYSTEM PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dwelza AI Hybrid Property Engine", 
    page_icon="🏡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_FILE = "hvp_dataset.csv"

# --- SYSTEM DB INITIALIZER & SEED GENERATION ---
def seed_fallback_database():
    """Generates standard baseline CSV asset data if no deployment file is discovered."""
    default_listings = {
        "title": [
            "Premium 3 BHK Smart Apartment", 
            "Cozy 1 BHK for Bachelors", 
            "Modern Coimbatore Center Flat", 
            "Luxury Coimbatore Suburban Villa",
            "Elite Skycrest Penthouse",
            "Serene Meadows Duplex"
        ],
        "city": ["Bangalore", "Mumbai", "Coimbatore", "Coimbatore", "Delhi", "Chennai"],
        "locality": [
            "Whitefield", "Andheri West", "Ramanathapuram", 
            "Saravanampatti", "Saket", "Anna Nagar"
        ],
        "transaction_type": ["Buy", "Rent", "Rent", "Buy", "Buy", "Rent"],
        "price_inr": [12000000, 35000, 22000, 8500000, 45000000, 45000],
        "size_sqft": [1400, 1100, 1250, 2400, 4200, 1800],
        "bhk": [3, 1, 2, 4, 5, 3],
        "age_years": [2, 5, 1, 0, 4, 3],
        "furnishing": ["Furnished", "Unfurnished", "Semi-Furnished", "Furnished", "Furnished", "Semi-Furnished"],
        "image_url": [
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=500&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=500&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=500&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=500&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=500&auto=format&fit=crop"
        ],
        "rera_number": ["PRM/KA/RERA/1251", "", "", "TN/29/Building/0122/2026", "DLR/44/RERA/2025", ""],
        "is_verified": [True, False, False, True, True, False],
        "near_metro": [True, True, False, False, True, True],
        "dist_to_metro_km": [0.8, 0.5, 4.2, 8.5, 0.3, 1.2],
        "dist_to_school_km": [1.2, 0.8, 1.5, 2.0, 0.5, 1.0],
        "dist_to_hospital_km": [2.1, 1.1, 0.9, 3.4, 1.0, 1.8],
        "num_amenities": [8, 3, 4, 12, 15, 7],
        "parking": [1, 0, 1, 2, 3, 2],
        "latitude": [12.9698, 19.1136, 10.9992, 11.0797, 28.5244, 13.0850],
        "longitude": [77.7500, 72.8697, 76.9934, 77.0011, 77.2065, 80.2101],
        "owner_name": ["Rajesh Kumar", "Amit Sharma", "Karthik Raja", "Suresh Kumar", "Vikram Malhotra", "Nandini Krishnan"],
        "owner_phone": ["9999999999", "8888888888", "9444012345", "9846056789", "9810012345", "9444556677"],
        "status": ["Active", "Active", "Active", "Active", "Active", "Active"]
    }
    pd.DataFrame(default_listings).to_csv(CSV_FILE, index=False, encoding="utf-8")

if not os.path.exists(CSV_FILE):
    seed_fallback_database()

# --- AUTOMATED SCHEMA TRANSLATION LAYER ---
def auto_map_dataframe(df):
    mapping_dict = {
        'locality': ['locality', 'location', 'suburb', 'neighborhood'],
        'city': ['city', 'metro_area', 'district'],
        'price_inr': ['price_inr', 'price', 'cost', 'amount'],
        'size_sqft': ['size_sqft', 'size', 'sqft', 'square_feet', 'area_sqft'],
        'transaction_type': ['transaction_type', 'type', 'purpose'],
        'status': ['status', 'listing_status']
    }
    renamed_cols = {}
    for standard_key, aliases in mapping_dict.items():
        for col in df.columns:
            if str(col).lower().strip() in aliases:
                renamed_cols[col] = standard_key
                break
    df = df.rename(columns=renamed_cols)
    
    # Fill structural fallbacks
    if 'locality' not in df.columns: df['locality'] = 'Central Core Area'
    if 'city' not in df.columns: df['city'] = 'Coimbatore'
    if 'size_sqft' not in df.columns: df['size_sqft'] = 1200
    if 'price_inr' not in df.columns: df['price_inr'] = 5000000
    if 'transaction_type' not in df.columns: df['transaction_type'] = 'Buy'
    if 'status' not in df.columns: df['status'] = 'Active'
    
    return df

@st.cache_data
def load_live_dataset():
    try:
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 10:
            df = pd.read_csv(CSV_FILE, encoding="latin-1", on_bad_lines="skip")
        else:
            seed_fallback_database()
            df = pd.read_csv(CSV_FILE, encoding="latin-1")
        return auto_map_dataframe(df)
    except:
        seed_fallback_database()
        return auto_map_dataframe(pd.read_csv(CSV_FILE, encoding="latin-1"))

df_listings = load_live_dataset()

# --- CACHE MEMORY ML TRAINING PIPELINE (PROJECT 2 CORE) ---
@st.cache_resource
def train_live_fusion_model(df):
    """Dynamically builds and compiles a memory-cached pipeline model for on-the-fly execution."""
    if df.empty:
        return None, None
    
    features = ['city', 'size_sqft', 'bhk', 'age_years', 'furnishing', 'dist_to_metro_km', 'num_amenities', 'parking']
    X = df[features].copy()
    y = df['price_inr'].copy()
    
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    categorical_cols = ['city', 'furnishing']
    X[categorical_cols] = encoder.fit_transform(X[categorical_cols].astype(str))
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model, encoder

ml_model, ml_encoder = train_live_fusion_model(df_listings)

# --- DYNAMIC RULE-BASED VALUATION CORE ---
def calculate_dynamic_valuation(size_sqft, locality, near_metro, txn_mode):
    locality_lower = str(locality).lower()
    if "mumbai" in locality_lower: base_rate = 18000
    elif "bangalore" in locality_lower: base_rate = 9500
    elif "coimbatore" in locality_lower: base_rate = 5500
    elif "delhi" in locality_lower: base_rate = 11000
    else: base_rate = 6000
        
    base_value = size_sqft * base_rate
    mult = 1.05 + (0.10 if near_metro else 0.0)
    final_capital = int(base_value * mult)
    
    if txn_mode in ["Rent", "Rented"]:
        predicted_rent = int((final_capital * 0.035) / 12)
        return int(predicted_rent * 0.90), int(predicted_rent * 1.10)
    else:
        return int(final_capital * 0.93), int(final_capital * 1.07)

def format_currency(num, txn_mode):
    if txn_mode in ["Rent", "Rented"]: return f"₹{num:,} / Month"
    if num >= 10000000: return f"₹{num / 10000000:.2f} Crore"
    elif num >= 100000: return f"₹{num / 100000:.2f} Lakh"
    return f"₹{num:,}"

# --- STATE TRACKING MANAGEMENT ---
if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

# --- SIDEBAR DESK CONTROLS ---
st.sidebar.title("🛡️ Identity Control Desk")
with st.sidebar.container(border=True):
    if st.session_state["user_role"] == "Guest":
        st.info("👤 Status: Unverified Session")
        u_input = st.text_input("Profile Username", value="RealEstate_Pro")
        r_input = st.selectbox("Role Track Clearance", ["Verified Buyer", "Verified Builder / Owner"])
        if st.button("Authorize Identity Profile", use_container_width=True):
            if u_input:
                st.session_state["username"] = u_input
                st.session_state["user_role"] = r_input
                st.rerun()
    else:
        st.success(f"🔒 Logged: {st.session_state['username']}")
        st.caption(f"Privilege Matrix Tier: {st.session_state['user_role']}")
        if st.button("Flush Identity State", use_container_width=True):
            st.session_state["user_role"] = "Guest"
            st.session_state["username"] = ""
            st.rerun()

st.sidebar.markdown("---")
menu_selection = st.sidebar.radio(
    "Ecosystem Portals", 
    ["🏢 Unified Property Feed", "💡 Multi-Source AI Price Predictor", "🗺️ Spatial GIS Map Core"]
)

# --- INJECT PREMIUM FRONTEND HTML HERO BLOCK ---
try:
    with open("static_hero.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=240)
except Exception as e:
    st.warning("HTML visual frame offline. Rendering text fallback mode.")
    st.title("Dwelza AI Hybrid Property Engine")

# --- PORTAL 1: SEARCH FEED MATRIX ---
if menu_selection == "🏢 Unified Property Feed":
    st.markdown("### 🏢 Unified Global Marketplace Index")
    st.write("Browse marketplace entries synced directly across standard data arrays.")
    
    with st.container(border=True):
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search Location, City, or Title...", value="", placeholder="Type here (e.g. Whitefield, Coimbatore...)")
        with col_s2:
            market_filter = st.selectbox("Market Core Filter", ["All Listings", "For Sale / Buy Only", "Rented Houses Only"])
        with col_s3:
            verif_filter = st.toggle("Show Verified (RERA Approved)")

    if not df_listings.empty:
        processed_df = df_listings.copy()
        processed_df = processed_df[processed_df['status'] == 'Active']
        
        if market_filter == "For Sale / Buy Only":
            processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('b')]
        elif market_filter == "Rented Houses Only":
            processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('r')]
            
        if verif_filter and 'is_verified' in processed_df.columns:
            processed_df = processed_df[processed_df['is_verified'] == True]
            
        if search_query:
            processed_df = processed_df[
                processed_df['locality'].str.contains(search_query, case=False, na=False) |
                processed_df['city'].str.contains(search_query, case=False, na=False) |
                processed_df.get('title', pd.Series(dtype=str)).str.contains(search_query, case=False, na=False)
            ]
            
        if not processed_df.empty:
            for idx, row in processed_df.iterrows():
                current_mode = "Rent" if str(row['transaction_type']).lower().startswith('r') else "Buy"
                img_url = row.get('image_url', "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500&auto=format&fit=crop")
                
                with st.container(border=True):
                    col_img, col_det = st.columns([1.2, 2.5])
                    with col_img:
                        st.image(img_url, use_container_width=True)
                    with col_det:
                        t1, t2 = st.columns([1, 2])
                        with t1:
                            st.markdown("🟢 **FOR RENT**" if current_mode == "Rent" else "🔵 **FOR SALE**")
                        with t2:
                            if row.get('is_verified', False):
                                st.markdown("🔒 **RERA VERIFIED PRO**")
                        
                        st.subheader(row.get('title', 'Premium Architectural Asset'))
                        st.markdown(f"📍 **Location Matrix Axis:** {row['locality']}, {row['city']}")
                        
                        m_p1, m_p2, m_p3 = st.columns(3)
                        m_p1.metric("Listed Valuation Price", format_currency(int(row['price_inr']), current_mode))
                        m_p2.metric("Total Usable Area Layout", f"{int(row['size_sqft']):,} Sq.Ft.")
                        
                        c_low, c_high = calculate_dynamic_valuation(int(row['size_sqft']), row['locality'], row.get('near_metro', False), current_mode)
                        m_p3.metric("AI Market Reference", format_currency(c_low, current_mode))
                        
                        with st.expander("📊 Run Deep Analytical Valuation Spread Matrix"):
                            st.info(f"💡 **AI Predictive Fair Boundary Baseline:** {format_currency(c_low, current_mode)} to {format_currency(c_high, current_mode)}")
                            
                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = int(row['price_inr']),
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                gauge = {
                                    'axis': {'range': [None, c_high * 1.35], 'tickformat': ',r'},
                                    'bar': {'color': "#38bdf8"},
                                    'steps': [
                                        {'range': [0, c_low], 'color': "rgba(255,255,255,0.06)"},
                                        {'range': [c_low, c_high], 'color': "rgba(56,189,248,0.22)"}
                                    ]
                                }
                            ))
                            fig.update_layout(height=130, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
                            st.plotly_chart(fig, use_container_width=True, key=f"gauge_feed_{idx}")
                            
                            if st.session_state["user_role"] != "Guest":
                                text_msg = f"Hello {row.get('owner_name', 'Agent')}, requesting data inspection loop for {row.get('title')}."
                                st.markdown(f'[💬 Contact Representative via WhatsApp (+91 {row.get("owner_phone", "9000000000")})](https://wa.me/91{row.get("owner_phone", "9000000000")}?text={urllib.parse.quote(text_msg)})')
        else:
            st.error("No active property listing elements match your structural location or filter query configurations.")
    else:
        st.warning("Database configuration ledger empty.")

# --- PORTAL 2: ADVANCED FUSION ML PREDICTOR ---
elif menu_selection == "💡 Multi-Source AI Price Predictor":
    st.markdown("### 💡 Multi-Source Data Fusion ML Engine")
    st.write("Run deep-learning predictive inferences using combined engineering attributes (BHK, Transit, Amenities, Age).")
    
    with st.container(border=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            city_sel = st.selectbox("Target Core City Hub", ["Delhi", "Mumbai", "Bangalore", "Pune", "Hyderabad", "Chennai", "Coimbatore"])
            locality_txt = st.text_input("Locality Sub-Neighborhood", value="Whitefield Zone")
            area_input = st.number_input("Structural Blueprint Size (Sq.Ft.)", min_value=100, max_value=50000, value=1500, step=50)
            bhk_sel = st.slider("BHK Layout Design", 1, 6, 3)
        with col_p2:
            furnish_sel = st.selectbox("Furnishing State Structural Layer", ["Unfurnished", "Semi-Furnished", "Furnished"])
            prop_age = st.slider("Property Architectural Age (Years)", 0, 50, 2)
            metro_dist = st.number_input("Distance to Mass Transit Link (km)", min_value=0.0, max_value=30.0, value=1.2)
            amenities_count = st.slider("Total Structural Amenities Count", 0, 20, 8)
            parking_spaces = st.selectbox("Designated Parking Units", [0, 1, 2, 3], index=1)

    st.markdown("---")
    
    # Combined calculations
    if st.button("🔍 Run Intelligent Deep Predictor Core", use_container_width=True):
        if ml_model is not None:
            # Structuring sample frame for model matching pipeline
            input_data = pd.DataFrame([{
                'city': city_sel, 'size_sqft': area_input, 'bhk': bhk_sel,
                'age_years': prop_age, 'furnishing': furnish_sel,
                'dist_to_metro_km': metro_dist, 'num_amenities': amenities_count, 'parking': parking_spaces
            }])
            
            # Map categories
            input_data[['city', 'furnishing']] = ml_encoder.transform(input_data[['city', 'furnishing']].astype(str))
            
            # Generate ML execution baseline
            base_pred = ml_model.predict(input_data)[0]
            # Adapt output according to local market trends dynamically
            l_bound, h_bound = int(base_pred * 0.92), int(base_pred * 1.08)
            calculated_avg = int(base_pred)
            
            st.success("### Algorithmic Forecast Scorecard")
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("ML Conservative Floor", format_currency(l_bound, "Buy"))
                m2.metric("ML Weighted Median Target", format_currency(calculated_avg, "Buy"))
                m3.metric("ML Aggressive Ceiling", format_currency(h_bound, "Buy"))
                
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = calculated_avg,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Predictive Vector: {locality_txt}, {city_sel}", 'font': {'size': 16}},
                gauge = {
                    'axis': {'range': [None, h_bound * 1.25], 'tickformat': ',r'},
                    'bar': {'color': "#0284c7"},
                    'steps': [
                        {'range': [0, l_bound], 'color': 'rgba(255, 255, 255, 0.08)'},
                        {'range': [l_bound, h_bound], 'color': 'rgba(2, 132, 199, 0.25)'}
                    ]
                }
            ))
            fig_gauge.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.error("ML Inference Architecture pipeline offline.")

# --- PORTAL 3: GEOSPATIAL GEOGRAPHIC MAP VISUALIZER ---
elif menu_selection == "🗺️ Spatial GIS Map Core":
    st.markdown("### 🗺️ Geographic GIS Resource Mapping Center")
    st.write("Visually audit property listings via standard coordinate vector lookups.")
    
    # Base configuration coordinate center setting (Coimbatore)
    base_lat, base_lon = 11.0168, 76.9558
    
    m = folium.Map(location=[base_lat, base_lon], zoom_start=6, control_scale=True)
    
    for idx, row in df_listings.iterrows():
        lat, lon = row.get('latitude', np.nan), row.get('longitude', np.nan)
        if not pd.isna(lat) and not pd.isna(lon):
            popup_html = f"""
            <div style='font-family: sans-serif; font-size: 12px; color: #333;'>
                <strong>{row['title']}</strong><br/>
                Locality: {row['locality']}<br/>
                Price: {format_currency(int(row['price_inr']), row['transaction_type'])}<br/>
                Area: {row['size_sqft']} Sq.Ft
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color="blue" if str(row['transaction_type']).lower().startswith('b') else "green", icon="home")
            ).add_to(m)
            
    with st.container(border=True):
        folium_static(m, width=1150, height=550)
