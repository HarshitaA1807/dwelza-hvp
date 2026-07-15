
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="Dwelza Advanced Valuation Platform", 
    page_icon="🏠", 
    layout="wide"
)

EXCEL_FILE = "source data.xlsx"

# --- SYSTEM INITIALIZATION ENGINE ---
def initialize_database():
    active_now = datetime.now().strftime("%Y-%m-%d")
    stale_past = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    future_exp = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    
    default_listings = {
        "listing_id": [1001, 1002, 1003, 1004, 1005],
        "title": ["Premium 3 BHK Apartment", "Cozy 1 BHK for Bachelors", "Luxury Smart Villa", "Modern Flat near IT Corridor", "Stale Unverified Listing Example"],
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon", "OMR Sholinganallur, Chennai", "Kakkanad, Kochi"],
        "price_inr": [18500000, 4500000, 52000000, 8500000, 3200000],
        "size_sqft": [1800, 650, 4200, 1450, 1600],
        "lat": [12.97189, 19.11967, 28.4908, 12.9010, 10.0159],
        "lon": [77.64115, 72.84642, 77.0894, 80.2279, 76.3419],
        "rera_number": ["PRM/KA/RERA/1251/310/PR/180516/001", "", "HRERA/2022/89", "TN/29/Building/0122/2024", ""],
        "is_verified": [True, False, True, True, False],
        "veg_only": [False, True, False, False, False],
        "bachelors_allowed": [True, True, False, True, True],
        "near_metro": [True, True, False, False, True],
        "owner_name": ["Rajesh Kumar", "Amit Sharma", "Vikram Malhotra", "Suresh Kumar", "Unknown Broker Hub"],
        "owner_phone": ["9876543210", "9123456789", "9988776655", "9444012345", "9846056789"],
        "reports_count": [0, 0, 0, 0, 4],
        "created_date": [active_now, active_now, active_now, active_now, stale_past],
        "expiry_date": [future_exp, future_exp, future_exp, future_exp, active_now],
        "status": ["Active", "Active", "Active", "Active", "Stale"]
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

# --- CONTEXT PERSISTENCE STRUCTS ---
if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

def calculate_dwelzestimate(size_sqft, locality, near_metro, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty: 
            base_rate = match['avg_price_per_sqft'].values[0]
    if base_rate is None:
        if "mumbai" in locality_lower: base_rate = 18000
        elif "bangalore" in locality_lower: base_rate = 9500
        else: base_rate = 6500
        
    base_value = size_sqft * base_rate
    mult = 1.05 + (0.10 if near_metro else 0.0)
    final_val = int(base_value * mult)
    return int(final_val * 0.93), int(final_val * 1.07)

def format_indian_currency(num):
    if num >= 10000000: return f"₹{num / 10000000:.2f} Crore"
    elif num >= 100000: return f"₹{num / 100000:.2f} Lakh"
    return f"₹{num:,}"

# --- IDENTITY ACCESS INTERFACE ---
st.sidebar.title("🛂 Identity Verification Desk")

with st.sidebar.container(border=True):
    if st.session_state["user_role"] == "Guest":
        st.info("👤 Session Track: Guest Profile Mode")
        u_input = st.text_input("Profile User Name", value="Investor_Alpha")
        r_input = st.selectbox("Authorization Track", ["Verified Buyer", "Verified Builder / Owner"])
        if st.button("Complete Verification", use_container_width=True):
            if u_input:
                st.session_state["username"] = u_input
                st.session_state["user_role"] = r_input
                st.rerun()
    else:
        st.success(f"🔒 Account Logged: {st.session_state['username']}")
        st.caption(f"Clearance: {st.session_state['user_role']}")
        if st.button("Logout Session", use_container_width=True):
            st.session_state["user_role"] = "Guest"
            st.session_state["username"] = ""
            st.rerun()

st.sidebar.markdown("---")
menu_selection = st.sidebar.radio(
    "Application Interfaces", 
    ["🔍 Property Marketplace", "💡 AI Value Predictor Engine", "📊 Market Trends Index", "🏗️ Owner Management Dashboard"]
)

# --- MODULE 1: ECOSYSTEM FEED ---
if menu_selection == "🔍 Property Marketplace":
    st.title("🏢 Dwelza Asset Feeds")
    st.markdown("---")
    
    if not df_listings.empty:
        active_items = df_listings[df_listings['status'] == 'Active']
        
        for idx, row in active_items.iterrows():
            with st.container(border=True):
                col_info, col_price = st.columns([3, 1])
                with col_info:
                    st.subheader(row['title'])
                    st.write(f"📍 Location Axis: **{row['locality']}** | 📐 Space Matrix: **{row['size_sqft']} Sq.Ft.**")
                    if row['is_verified']:
                        st.success(f"✓ RERA Bound Sequence Approved: {row['rera_number']}")
                with col_price:
                    st.metric(label="Asking Market Value", value=format_indian_currency(row['price_inr']))
                
                c_pred, c_btn = st.columns([2, 1])
                with c_pred:
                    low_v, high_v = calculate_dwelzestimate(row['size_sqft'], row['locality'], row.get('near_metro', False), df_historical)
                    st.info(f"💡 **AI Predictive Fair Boundary Baseline:** {format_indian_currency(low_v)} - {format_indian_currency(high_v)}")
                with c_btn:
                    if st.session_state["user_role"] == "Guest":
                        st.warning("🔒 Verification required to unlock contact channels.")
                    else:
                        st.write(f"👤 Representative: **{row['owner_name']}**")
                        text_msg = f"Hello {row['owner_name']}, looking to inspect '{row['title']}'."
                        st.markdown(f'[💬 Connect on WhatsApp](https://wa.me/91{row["owner_phone"]}?text={urllib.parse.quote(text_msg)})')

# --- MODULE 2: INNOVATIVE VALUE PREDICTOR ---
elif menu_selection == "💡 AI Value Predictor Engine":
    st.title("💡 Advanced Algorithmic Valuation Desk")
    st.write("Determine highly optimized real estate target pricing vectors via localized historical telemetry indexing filters.")
    st.markdown("---")
    
    col_in_1, col_in_2 = st.columns(2)
    with col_in_1:
        selected_loc = st.selectbox("Target Regional Node", df_historical['locality'].unique() if not df_historical.empty else ["Indiranagar, Bangalore"])
        layout_size = st.number_input("Total Unit Matrix Footprint (Sq.Ft.)", min_value=100, max_value=20000, value=1200, step=50)
    with col_in_2:
        infra_metro = st.toggle("Strategic Proximity Infrastructure Node (Metro Proximity < 1KM)", value=True)
        structural_quality = st.select_slider("Construct Structural Tier Standard", options=["Economy", "Standard", "Premium Smart Spec"])

    # Math Calculation Boundary Pipeline
    low_bound, high_bound = calculate_dwelzestimate(layout_size, selected_loc, infra_metro, df_historical)
    
    tier_multiplier = 1.0
    if structural_quality == "Economy": tier_multiplier = 0.90
    elif structural_quality == "Premium Smart Spec": tier_multiplier = 1.15
    
    final_low = int(low_bound * tier_multiplier)
    final_high = int(high_bound * tier_multiplier)
    median_avg = int((final_low + final_high) / 2)
    
    st.markdown("### Valuation Breakdown Matrix")
    
    # Innovative Metric Scorecard Block
    with st.container(border=True):
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Conservative Floor Estimate", format_indian_currency(final_low))
        m_col2.metric("Target Median Valuation Value", format_indian_currency(median_avg), delta=f"{int((tier_multiplier-1)*100)}% Quality Premium Applied")
        m_col3.metric("Aggressive Ceiling Limit", format_indian_currency(final_high))
        
    # Innovative Predictive Variance Gauge Graphic Layout
    st.markdown("### Valuation Spread Vector Visualization")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = median_avg,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Predicted Target Valuation for {selected_loc}", 'font': {'size': 20}},
        delta = {'reference': low_bound, 'increasing': {'color': "LightSeaGreen"}},
        gauge = {
            'axis': {'range': [None, final_high * 1.2], 'tickformat': ',r'},
            'bar': {'color': "#38bdf8"},
            'bgcolor': "rgba(0,0,0,0)",
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': final_high
            },
            'steps': [
                {'range': [0, final_low], 'color': 'rgba(255, 255, 255, 0.1)'},
                {'range': [final_low, final_high], 'color': 'rgba(56, 189, 248, 0.2)'}
            ]
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff" if st.get_option("theme.base") == "dark" else "#000000"})
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- MODULE 3: MARKET TRENDS ---
elif menu_selection == "📊 Market Trends Index":
    st.title("📊 Macro-Analysis Metrics Dashboard")
    st.markdown("---")
    if not df_historical.empty:
        fig_bar = px.bar(
            df_historical, 
            x="locality", 
            y="avg_price_per_sqft", 
            color="avg_price_per_sqft",
            title="Localized Average Operational Index Values (Per Sq.Ft.)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# --- MODULE 4: OPERATIONS CONSOLE ---
elif menu_selection == "🏗️ Owner Management Dashboard":
    st.title("🏗️ Portfolio Control Desk")
    st.markdown("---")
    if st.session_state["user_role"] != "Verified Builder / Owner":
        st.error("🚨 Track Access Prohibited. Shift your active profile track settings to 'Verified Builder / Owner' inside the sidebar verification desk widget to open this deployment window.")
    else:
        with st.form("new_listing_asset"):
            st.subheader("Broadcast New Verified Asset Inventory Record")
            t_title = st.text_input("Asset Title")
            t_loc = st.selectbox("Location Target Axis", df_historical['locality'].unique() if not df_historical.empty else ["Indiranagar, Bangalore"])
            t_price = st.number_input("Absolute Demanded Asking Value Target (INR)", min_value=100000)
            t_size = st.number_input("Net Usable Footprint Area Layout (Sq.Ft.)", min_value=150)
            t_phone = st.text_input("Primary Direct Contact Routing Sequence (10 Digits)")
            
            if st.form_submit_button("Verify and Append Asset to Active Ledger"):
                if t_title and t_phone:
                    nxt_id = int(df_listings['listing_id'].max() + 1 if not df_listings.empty else 1001)
                    new_item = {
                        "listing_id": nxt_id, "title": t_title, "locality": t_loc, "price_inr": t_price, "size_sqft": t_size,
                        "lat": 12.97, "lon": 77.59, "rera_number": "PENDING-APPROVAL-LEDGER", "is_verified": False,
                        "veg_only": False, "bachelors_allowed": True, "near_metro": False,
                        "owner_name": st.session_state["username"], "owner_phone": t_phone,
                        "reports_count": 0, "created_date": datetime.now().strftime("%Y-%m-%d"),
                        "expiry_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "status": "Active"
                    }
                    df_listings = pd.concat([df_listings, pd.DataFrame([new_item])], ignore_index=True)
                    save_data(df_listings, "Listings")
                    st.success("Asset appended successfully!")
                    st.rerun()
