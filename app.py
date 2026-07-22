import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PLATFORM CONFIGURATION ---
st.set_page_config(
    page_title="Dwelza Premium Visual Property Engine", 
    page_icon="🏡", 
    layout="wide"
)

# Target production dataset file path
CSV_FILE = "hvp_dataset.csv"

# --- AUTOMATED SCHEMA TRANSLATION ENGINE ---
def auto_map_dataframe(df):
    """
    Dynamically maps raw Kaggle datasets using common real-estate aliases
    to prevent application crashes and remove key missing column errors.
    """
    mapping_dict = {
        'locality': ['locality', 'location', 'suburb', 'neighborhood', 'area', 'city', 'address', 'place'],
        'price_inr': ['price_inr', 'price', 'cost', 'amount', 'value', 'sale_price', 'rent_price'],
        'size_sqft': ['size_sqft', 'size', 'sqft', 'square_feet', 'area_sqft', 'builtup_area', 'carpet_area'],
        'transaction_type': ['transaction_type', 'type', 'status_type', 'purpose', 'rent_or_sale'],
        'status': ['status', 'listing_status', 'availability_status', 'state']
    }
    
    renamed_cols = {}
    for standard_key, aliases in mapping_dict.items():
        for col in df.columns:
            if str(col).lower().strip() in aliases:
                renamed_cols[col] = standard_key
                break
                
    df = df.rename(columns=renamed_cols)
    
    # Inject standard fallbacks for missing structural configuration elements
    if 'locality' not in df.columns: df['locality'] = 'Unknown Location Axis'
    if 'size_sqft' not in df.columns: df['size_sqft'] = 1000
    if 'price_inr' not in df.columns: df['price_inr'] = 5000000
    if 'transaction_type' not in df.columns: df['transaction_type'] = 'Buy'
    if 'status' not in df.columns: df['status'] = 'Active'
    
    # Programmatic sanitization and typing cleanup
    df['locality'] = df['locality'].astype(str).str.strip()
    df['transaction_type'] = df['transaction_type'].astype(str).str.capitalize()
    df['status'] = df['status'].astype(str).str.capitalize()
    
    # Convert numerical columns to valid integer states safely
    df['price_inr'] = pd.to_numeric(df['price_inr'], errors='coerce').fillna(5000000).astype(int)
    df['size_sqft'] = pd.to_numeric(df['size_sqft'], errors='coerce').fillna(1000).astype(int)
    
    return df

# --- INTUITIVE INITIALIZER ENGINE (WITH UNICODE PATCH) ---
def seed_fallback_database():
    """Generates standard baseline CSV asset data if no deployment file is discovered."""
    if not os.path.exists(CSV_FILE):
        default_listings = {
            "title": [
                "Premium 3 BHK Smart Apartment", 
                "Cozy 1 BHK for Bachelors", 
                "Modern Coimbatore Center Flat", 
                "Luxury Coimbatore Suburban Villa"
            ],
            "locality": [
                "Whitefield, Bangalore", 
                "Andheri West, Mumbai", 
                "Ramanathapuram, Coimbatore", 
                "Saravanampatti, Coimbatore"
            ],
            "transaction_type": ["Buy", "Rent", "Rent", "Buy"],
            "price_inr": [12000000, 35000, 22000, 8500000],
            "size_sqft": [1400, 1100, 1250, 2400],
            "image_url": [
                "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=500&auto=format&fit=crop", 
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500&auto=format&fit=crop", 
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=500&auto=format&fit=crop", 
                "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=500&auto=format&fit=crop"
            ],
            "rera_number": ["PRM/KA/RERA/1251", "", "", "TN/29/Building/0122/2026"],
            "is_verified": [True, False, False, True],
            "near_metro": [True, True, False, False],
            "owner_name": ["Rajesh Kumar", "Amit Sharma", "Karthik Raja", "Suresh Kumar"],
            "owner_phone": ["9999999999", "8888888888", "9444012345", "9846056789"],
            "status": ["Active", "Active", "Active", "Active"]
        }
        pd.DataFrame(default_listings).to_csv(CSV_FILE, index=False, encoding="utf-8")

seed_fallback_database()

@st.cache_data
def load_live_dataset():
    """
    Reads the active dataset safely. Explicitly targets 'latin-1' encoding 
    profiles to bypass and completely eradicate UnicodeDecodeErrors.
    """
    try:
        df = pd.read_csv(CSV_FILE, encoding="latin-1")
        return auto_map_dataframe(df)
    except Exception as e:
        st.error(f"Critical Ingestion Pipeline Error: {e}")
        return pd.DataFrame()

df_listings = load_live_dataset()

# --- CONTEXT SYSTEM CACHING STATES ---
if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

# --- ADVANCED VALUATION PROCESSING ENGINE ---
def calculate_dynamic_valuation(size_sqft, locality, near_metro, txn_mode):
    locality_lower = str(locality).lower()
    
    # Adaptive regional baseline evaluation parameters
    if "mumbai" in locality_lower: base_rate = 18000
    elif "bangalore" in locality_lower: base_rate = 9500
    elif "coimbatore" in locality_lower: base_rate = 5500
    elif "delhi" in locality_lower or "gurgaon" in locality_lower: base_rate = 11000
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

# --- USER IDENTITY Clearances PANEL ---
st.sidebar.title("🛡️ Identity Control Desk")
with st.sidebar.container(border=True):
    if st.session_state["user_role"] == "Guest":
        st.info("👤 Status: Unverified Tracker Session")
        u_input = st.text_input("Profile Username Handle", value="RealEstate_Pro")
        r_input = st.selectbox("Role Track Clearance", ["Verified Buyer", "Verified Builder / Owner"])
        if st.button("Authorize Identity Profile", use_container_width=True):
            if u_input:
                st.session_state["username"] = u_input
                st.session_state["user_role"] = r_input
                st.rerun()
    else:
        st.success(f"🔒 Account Logged: {st.session_state['username']}")
        st.caption(f"Privilege Matrix Tier: {st.session_state['user_role']}")
        if st.button("Flush Identity State Tracker", use_container_width=True):
            st.session_state["user_role"] = "Guest"
            st.session_state["username"] = ""
            st.rerun()

st.sidebar.markdown("---")
menu_selection = st.sidebar.radio(
    "Ecosystem Portals", 
    ["🔍 Unified Property Feed", "💡 Universal AI Price Predictor"]
)

# --- PORTAL 1: SEARCH FEED CARD MATRIX ---
if menu_selection == "🔍 Unified Property Feed":
    st.title("🏢 Dwelza Global Visual Property Matrix")
    st.write("Browse dynamic marketplace indexes for purchase transactions and residential long-term leases.")
    st.markdown("---")
    
    # Global Omnipresent Navigation Filter Box
    with st.container(border=True):
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search Any Location, City, or Property Title...", value="", placeholder="Type anywhere (e.g., Coimbatore, Bangalore, Mumbai...)")
        with col_s2:
            market_filter = st.selectbox("Market System Core Type", ["All Listings", "For Sale / Buy Only", "Rented Houses Only"])
        with col_s3:
            verif_filter = st.toggle("Show Verified Only (RERA Approved)")

    if not df_listings.empty:
        processed_df = df_listings[df_listings['status'] == 'Active'].copy()
        
        # Apply strict data subset filters safely
        if market_filter == "For Sale / Buy Only":
            processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('b')]
        elif market_filter == "Rented Houses Only":
            processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('r')]
            
        if verif_filter and 'is_verified' in processed_df.columns:
            processed_df = processed_df[processed_df['is_verified'] == True]
            
        if search_query:
            processed_df = processed_df[
                processed_df['locality'].str.contains(search_query, case=False, na=False) |
                processed_df.get('title', pd.Series(dtype=str)).str.contains(search_query, case=False, na=False)
            ]
            
        if not processed_df.empty:
            for idx, row in processed_df.iterrows():
                current_mode = "Rent" if str(row['transaction_type']).lower().startswith('r') else "Buy"
                
                # Fetch visual media anchors or fallback to clean real estate photography
                img_url = row.get('image_url', "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500&auto=format&fit=crop")
                if pd.isna(img_url) or not str(img_url).strip():
                    img_url = "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500&auto=format&fit=crop"
                
                with st.container(border=True):
                    col_img, col_det = st.columns([1.2, 2.5])
                    
                    with col_img:
                        st.image(img_url, use_container_width=True)
                        
                    with col_det:
                        c_tag, c_rera = st.columns([1, 2])
                        with c_tag:
                            st.markdown("🟢 **FOR RENT**" if current_mode == "Rent" else "🔵 **FOR SALE**")
                        with c_rera:
                            if row.get('is_verified', False) or (row.get('rera_number', '') and str(row.get('rera_number','')) != 'nan'):
                                st.markdown("🔒 **RERA VERIFIED PRO**")
                                
                        st.subheader(row.get('title', 'Premium Architectural Listing Asset'))
                        st.markdown(f"📍 **Location Mapping Axis:** {row['locality']}")
                        
                        # Quantitative visual indicator rows
                        m_p1, m_p2, m_p3 = st.columns(3)
                        m_p1.metric("Listed Valuation Price", format_currency(int(row['price_inr']), current_mode))
                        m_p2.metric("Total Usable Area Layout", f"{int(row['size_sqft']):,} Sq.Ft.")
                        
                        c_low, c_high = calculate_dynamic_valuation(int(row['size_sqft']), row['locality'], row.get('near_metro', False), current_mode)
                        m_p3.metric("AI Market Reference", format_currency(c_low, current_mode))
                        
                        with st.expander("📊 Run Deep Statistical Valuation Spread Matrix"):
                            st.info(f"💡 **AI Predictive Fair Boundary Baseline:** {format_currency(c_low, current_mode)} to {format_currency(c_high, current_mode)}")
                            
                            # Render comparative analytics layout chart gauges
                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = int(row['price_inr']),
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': "Market Assessment Delta Vector", 'font': {'size': 12}},
                                gauge = {
                                    'axis': {'range': [None, c_high * 1.35], 'tickformat': ',r'},
                                    'bar': {'color': "#38bdf8"},
                                    'steps': [
                                        {'range': [0, c_low], 'color': "rgba(255,255,255,0.06)"},
                                        {'range': [c_low, c_high], 'color': "rgba(56,189,248,0.22)"}
                                    ]
                                }
                            ))
                            fig.update_layout(height=130, margin=dict(l=10,r=10,t=35,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
                            st.plotly_chart(fig, use_container_width=True, key=f"gauge_widget_{idx}")
                            
                            if st.session_state["user_role"] != "Guest":
                                text_msg = f"Hello {row.get('owner_name', 'Agent')}, looking to inspect this property asset."
                                st.markdown(f'[💬 Directly Message Representative via WhatsApp (+91 {row.get("owner_phone", "9000000000")})](https://wa.me/91{row.get("owner_phone", "9000000000")}?text={urllib.parse.quote(text_msg)})')
        else:
            st.error("No active property listing elements match your structural location or filter query configurations.")
    else:
        st.warning("Database configuration ledger empty. Drop a valid raw CSV dataset in the root deployment container.")

# --- PORTAL 2: UNIVERSAL PRICE PREDICTOR ENGINE ---
elif menu_selection == "💡 Universal AI Price Predictor":
    st.title("💡 Cross-Location Real Estate Prediction Engine")
    st.write("Type **any location across India** below. The predictive fallback matrix automatically calculates localized pricing metrics.")
    st.markdown("---")
    
    with st.container(border=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            user_typed_location = st.text_input("Target Location Hub (Any City or Neighborhood)", value="Coimbatore Center")
            property_sqft = st.number_input("Structural Blueprint Size (Sq.Ft.)", min_value=100, max_value=50000, value=1200, step=50)
        with col_p2:
            target_transaction = st.selectbox("Market Evaluation Channel Mode", ["Buy / Sell Valuation", "Rental Yield Analysis"])
            infra_node = st.toggle("Strategic Asset Optimization Layout (Near Mass Metro Transit)", value=False)

    tx_mode = "Rent" if "Rental" in target_transaction else "Buy"
    l_bound, h_bound = calculate_dynamic_valuation(property_sqft, user_typed_location, infra_node, tx_mode)
    calculated_avg = int((l_bound + h_bound) / 2)
    
    st.markdown("### Algorithmic Forecast Scorecard")
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Conservative Baseline Floor", format_currency(l_bound, tx_mode))
        m2.metric("Optimized Median Target", format_currency(calculated_avg, tx_mode))
        m3.metric("Aggressive Upper Cap Limit", format_currency(h_bound, tx_mode))

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = calculated_avg,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Target Fair Market Prediction Vector: {user_typed_location}", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, h_bound * 1.25], 'tickformat': ',r'},
            'bar': {'color': "#0284c7"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, l_bound], 'color': 'rgba(255, 255, 255, 0.08)'},
                {'range': [l_bound, h_bound], 'color': 'rgba(2, 132, 199, 0.25)'}
            ]
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
    st.plotly_chart(fig_gauge, use_container_width=True)
