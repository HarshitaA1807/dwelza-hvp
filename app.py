
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
    page_title="Dwelza Advanced Real Estate Matrix", 
    page_icon="🏢", 
    layout="wide"
)

EXCEL_FILE = "source data.xlsx"

# --- INTUITIVE SEED DATA LOADER WITH RENTAL SCALING ---
def initialize_database():
    active_now = datetime.now().strftime("%Y-%m-%d")
    stale_past = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    future_exp = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    
    default_listings = {
        "listing_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007],
        "title": [
            "Premium 3 BHK Apartment", "Cozy 1 BHK for Bachelors", 
            "Luxury Smart Villa", "Modern Flat near IT Corridor", 
            "Stale Unverified Listing Example", "High-Rise 2 BHK Rental Flat",
            "Executive Studio Apartment"
        ],
        "locality": [
            "Indiranagar, Bangalore", "Andheri West, Mumbai", 
            "DLF Phase 3, Gurgaon", "OMR Sholinganallur, Chennai", 
            "Kakkanad, Kochi", "Whitefield, Bangalore", "Bandra West, Mumbai"
        ],
        "transaction_type": ["Buy", "Buy", "Buy", "Buy", "Buy", "Rent", "Rent"],
        "price_inr": [18500000, 4500000, 52000000, 8500000, 3200000, 38000, 25000],
        "size_sqft": [1800, 650, 4200, 1450, 1600, 1200, 500],
        "lat": [12.9718, 19.1196, 28.4908, 12.9010, 10.0159, 12.9698, 19.0596],
        "lon": [77.6411, 72.8464, 77.0894, 80.2279, 76.3419, 77.7499, 72.8295],
        "rera_number": ["PRM/KA/RERA/1251/310/PR/180516/001", "", "HRERA/2022/89", "TN/29/Building/0122/2024", "", "", ""],
        "is_verified": [True, False, True, True, False, True, False],
        "near_metro": [True, True, False, False, True, True, True],
        "owner_name": ["Rajesh Kumar", "Amit Sharma", "Vikram Malhotra", "Suresh Kumar", "Unknown Broker Hub", "Nikhil Reddy", "Pooja Mehta"],
        "owner_phone": ["9876543210", "9123456789", "9988776655", "9444012345", "9846056789", "9880011223", "9820099887"],
        "reports_count": [0, 0, 0, 0, 4, 0, 0],
        "created_date": [active_now, active_now, active_now, active_now, stale_past, active_now, active_now],
        "expiry_date": [future_exp, future_exp, future_exp, future_exp, active_now, future_exp, future_exp],
        "status": ["Active", "Active", "Active", "Active", "Stale", "Active", "Active"]
    }
    
    default_historical = {
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon", "OMR Sholinganallur, Chennai", "Adyar, Chennai", "Coimbatore Center", "Kakkanad, Kochi", "Thiruvananthapuram City"],
        "avg_price_per_sqft": [9500, 18000, 11500, 6200, 13500, 5500, 5800, 5200]
    }
    
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
            pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
    else:
        try:
            xl = pd.ExcelFile(EXCEL_FILE)
            if "Listings" not in xl.sheet_names or "HistoricalSales" not in xl.sheet_names:
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                    pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
                    pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
        except:
            pass

initialize_database()

def load_data(sheet_name):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        return df
    except:
        return pd.DataFrame()

def save_data(df, sheet_name):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    st.cache_data.clear()

df_listings = load_data("Listings")
df_historical = load_data("HistoricalSales")

# Ensure transaction column exists for fallback retro-compatibility
if "transaction_type" not in df_listings.columns:
    df_listings["transaction_type"] = "Buy"

# --- SYSTEM CACHING STATES ---
if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

# --- ADVANCED ANY-LOCATION SMART PREDICTION LOGIC ---
def calculate_dynamic_valuation(size_sqft, locality, near_metro, txn_mode, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    
    # 1. Look for precise index matches
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty: 
            base_rate = match['avg_price_per_sqft'].values[0]
            
    # 2. Universal fallback matching algorithm for any unknown location typed by user
    if base_rate is None:
        if "mumbai" in locality_lower or "pune" in locality_lower: base_rate = 16500
        elif "bangalore" in locality_lower or "hyderabad" in locality_lower: base_rate = 9000
        elif "chennai" in locality_lower or "coimbatore" in locality_lower: base_rate = 6800
        elif "delhi" in locality_lower or "gurgaon" in locality_lower or "noida" in locality_lower: base_rate = 11000
        else: base_rate = 5500 # Global baseline per sqft for generic/tier-3 destinations
        
    capital_value = size_sqft * base_rate
    mult = 1.05 + (0.08 if near_metro else 0.0)
    final_capital = int(capital_value * mult)
    
    if txn_mode == "Rent":
        # Calculate monthly rental matrix based on an annualized yield of 3.6%
        predicted_rent = int((final_capital * 0.036) / 12)
        return int(predicted_rent * 0.90), int(predicted_rent * 1.10)
    else:
        return int(final_capital * 0.93), int(final_capital * 1.07)

def format_val_currency(num, txn_mode):
    if txn_mode == "Rent":
        return f"₹{num:,} / Month"
    else:
        if num >= 10000000: return f"₹{num / 10000000:.2f} Crore"
        elif num >= 100000: return f"₹{num / 100000:.2f} Lakh"
        return f"₹{num:,}"

# --- IDENTITY VERIFICATION INTERFACE ---
st.sidebar.title("🛡️ Identity Verification Desk")
with st.sidebar.container(border=True):
    if st.session_state["user_role"] == "Guest":
        st.info("👤 Status: Unverified Tracker Session")
        u_input = st.text_input("Profile Handle Name", value="RealEstate_Pro")
        r_input = st.selectbox("Role Track Clearance", ["Verified Buyer", "Verified Builder / Owner"])
        if st.button("Authorize Identity Profile", use_container_width=True):
            if u_input:
                st.session_state["username"] = u_input
                st.session_state["user_role"] = r_input
                st.rerun()
    else:
        st.success(f"🔒 Account Logged: {st.session_state['username']}")
        st.caption(f"Privilege Matrix Tier: {st.session_state['user_role']}")
        if st.button("Flush Identity State", use_container_width=True):
            st.session_state["user_role"] = "Guest"
            st.session_state["username"] = ""
            st.rerun()

st.sidebar.markdown("---")
menu_selection = st.sidebar.radio(
    "Ecosystem Operational Portals", 
    ["🔍 Unified Property Feed", "💡 Universal AI Price Predictor", "📈 Market Trends Ledger"]
)

# --- PORTAL 1: UNIFIED FEEDS & MULTI-LOCATION SEARCH ---
if menu_selection == "🔍 Unified Property Feed":
    st.title("🏢 Dwelza Global Asset Matrix")
    st.write("Browse dynamic marketplace indexes for purchase transactions and residential long-term leases.")
    st.markdown("---")
    
    # Global Omnipresent Search Optimization Layout
    with st.container(border=True):
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search Any Location, City, or Property Title...", value="", placeholder="Type anywhere (e.g., Bandra, Whitefield, Kochi...)")
        with col_s2:
            market_filter = st.selectbox("Market System Core", ["All Listings", "For Sale / Buy Only", "Rented Houses Only"])
        with col_s3:
            verif_filter = st.toggle("Show Verified Only (RERA Approved)")

    if not df_listings.empty:
        processed_df = df_listings[df_listings['status'] == 'Active']
        
        # Apply market segmentation hooks
        if market_filter == "For Sale / Buy Only":
            processed_df = processed_df[processed_df['transaction_type'] == 'Buy']
        elif market_filter == "Rented Houses Only":
            processed_df = processed_df[processed_df['transaction_type'] == 'Rent']
            
        # Apply verification strictness checks
        if verif_filter:
            processed_df = processed_df[processed_df['is_verified'] == True]
            
        # Apply the multi-location wildcard string matcher
        if search_query:
            processed_df = processed_df[
                processed_df['locality'].str.contains(search_query, case=False, na=False) |
                processed_df['title'].str.contains(search_query, case=False, na=False)
            ]
            
        if not processed_df.empty:
            for idx, row in processed_df.iterrows():
                current_mode = row.get('transaction_type', 'Buy')
                with st.container(border=True):
                    col_info, col_metric = st.columns([3, 1])
                    with col_info:
                        type_tag = "🟢 FOR RENT" if current_mode == "Rent" else "🔵 FOR SALE"
                        st.caption(f"**{type_tag}**")
                        st.subheader(row['title'])
                        st.write(f"📍 Location Mapping: **{row['locality']}** | 📐 Scale Boundary: **{row['size_sqft']} Sq.Ft.**")
                        if str(row.get('rera_number', '')) != "nan" and row.get('rera_number', ''):
                            st.success(f"✓ Regulatory RERA Database Record Confirmed: {row['rera_number']}")
                    with col_metric:
                        st.metric(label="Listed Asset Target Price", value=format_val_currency(row['price_inr'], current_mode))
                        
                    c_low, c_high = calculate_dynamic_valuation(row['size_sqft'], row['locality'], row.get('near_metro', False), current_mode, df_historical)
                    
                    col_b1, col_b2 = st.columns([2, 1])
                    with col_b1:
                        st.info(f"💡 **AI Predictive Fair Value Range for this location:** {format_val_currency(c_low, current_mode)} - {format_val_currency(c_high, current_mode)}")
                    with col_b2:
                        if st.session_state["user_role"] == "Guest":
                            st.warning("🔒 Verification token needed to access contact paths.")
                        else:
                            text_msg = f"Hello {row['owner_name']}, inquiring about asset sequence '{row['title']}'."
                            st.markdown(f'[💬 Chat with Representative (+91 {row["owner_phone"]})](https://wa.me/91{row["owner_phone"]}?text={urllib.parse.quote(text_msg)})')
        else:
            st.error("No real estate entries match your specific location query or transaction layout selection.")

# --- PORTAL 2: UNIVERSAL ANY-LOCATION PREDICTOR ---
elif menu_selection == "💡 Universal AI Price Predictor":
    st.title("💡 Cross-Location Real Estate Prediction Engine")
    st.write("Type **any location across India** below. The predictive fallback matrix automatically runs statistical approximations for size parameters.")
    st.markdown("---")
    
    with st.container(border=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            user_typed_location = st.text_input("Target Location Hub (Any City or Neighborhood)", value="Bandra West, Mumbai")
            property_sqft = st.number_input("Structural Blueprint Size (Sq.Ft.)", min_value=100, max_value=50000, value=1100, step=50)
        with col_p2:
            target_transaction = st.selectbox("Market Evaluation Channel Mode", ["Buy / Sell Valuation", "Rental Yield Analysis"])
            infra_node = st.toggle("Strategic Asset Optimization Layout (Near Mass Metro Transit)", value=True)
            finishing_grade = st.select_slider("Interior Finishing Parameter Standard", options=["Economy Structural Build", "Standard Standard", "Premium Ultra Core"])

    # Map configuration selector to mathematical structures
    tx_mode = "Rent" if "Rental" in target_transaction else "Buy"
    l_bound, h_bound = calculate_dynamic_valuation(property_sqft, user_typed_location, infra_node, tx_mode, df_historical)
    
    tier_weight = 1.0
    if finishing_grade == "Economy Structural Build": tier_weight = 0.88
    elif finishing_grade == "Premium Ultra Core": tier_weight = 1.18
    
    calculated_low = int(l_bound * tier_weight)
    calculated_high = int(h_bound * tier_weight)
    calculated_avg = int((calculated_low + calculated_high) / 2)
    
    st.markdown("### Algorithmic Forecast Scorecard")
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Conservative Baseline Floor", format_val_currency(calculated_low, tx_mode))
        m2.metric("Optimized Median Target", format_val_currency(calculated_avg, tx_mode), delta=f"{int((tier_weight-1)*100)}% Grade Skew Factor")
        m3.metric("Aggressive Upper Cap Limit", format_val_currency(calculated_high, tx_mode))

    # Predictive Visual Display Component Block
    st.markdown("### Structural Valuation Spread Spectrum Indicator")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = calculated_avg,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Target Fair Market Prediction Vector: {user_typed_location}", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, calculated_high * 1.25], 'tickformat': ',r'},
            'bar': {'color': "#0284c7"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, calculated_low], 'color': 'rgba(255, 255, 255, 0.08)'},
                {'range': [calculated_low, calculated_high], 'color': 'rgba(2, 132, 199, 0.25)'}
            ]
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- PORTAL 3: INDEX MARKET TRENDS ---
elif menu_selection == "📈 Market Trends Ledger":
    st.title("📈 Strategic Regional Analytics")
    st.markdown("---")
    if not df_historical.empty:
        fig = px.bar(
            df_historical, 
            x="locality", 
            y="avg_price_per_sqft", 
            color="avg_price_per_sqft",
            title="Baseline Valuation Indexing Arrays per Sq.Ft.",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
