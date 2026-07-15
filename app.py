
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
from datetime import datetime, timedelta

# --- INITIAL SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Dwelza Pro Hub", page_icon="🏢", layout="wide")

# Force readable CSS text rules (Universal high-contrast parameters)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Premium High Contrast Card Outlines */
    .market-card {
        padding: 24px;
        border-radius: 12px;
        background-color: #1e293b !important;
        border: 2px solid #475569 !important;
        margin-bottom: 25px;
    }
    
    /* Force text colors inside custom blocks to remain readable */
    .market-card h3, .market-card p, .market-card span, .market-card div {
        color: #ffffff !important;
    }
    
    .price-tag {
        font-size: 26px;
        font-weight: 800;
        color: #38bdf8 !important;
    }
    
    /* Security Alert Callouts */
    .escrow-alert {
        background-color: #7f1d1d !important;
        border: 1px solid #f87171 !important;
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        color: #fef2f2 !important;
    }
    
    .dwelz-box {
        background-color: #0f172a !important;
        border: 1px solid #3b82f6 !important;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        color: #e2e8f0 !important;
    }
    
    /* WhatsApp Styling */
    .wa-link-btn {
        background-color: #22c55e !important;
        color: white !important;
        padding: 10px 16px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        text-align: center;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

EXCEL_FILE = "source data.xlsx"

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
        if sheet_name == "Listings":
            if "status" not in df.columns: df["status"] = "Active"
            if "reports_count" not in df.columns: df["reports_count"] = 0
            if "expiry_date" not in df.columns: df["expiry_date"] = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        return df
    except:
        return pd.DataFrame()

def save_data(df, sheet_name):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    st.cache_data.clear()

df_listings = load_data("Listings")
df_historical = load_data("HistoricalSales")

# --- INITIALIZE RUNTIME SESSION STATES ---
if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

def calculate_dwelzestimate(size_sqft, locality, near_metro, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty: base_rate = match['avg_price_per_sqft'].values[0]
    if base_rate is None:
        if "mumbai" in locality_lower: base_rate = 18000
        elif "bangalore" in locality_lower: base_rate = 9500
        else: base_rate = 6500
    base_value = size_sqft * base_rate
    mult = 1.06 + (0.12 if near_metro else 0.0)
    final_val = int(base_value * mult)
    return int(final_val * 0.95), int(final_val * 1.05)

def format_indian_currency(num):
    if num >= 10000000: return f"₹{num / 10000000:.2f} Crore"
    elif num >= 100000: return f"₹{num / 100000:.2f} Lakh"
    return f"₹{num:,}"

# --- SIDEBAR INTERFACE (IDENTITY VERIFICATION ALWAYS VISIBLE) ---
st.sidebar.title("🛡️ Identity Verification Desk")

if st.session_state["user_role"] == "Guest":
    st.sidebar.info("🔒 Status: Unverified Guest Mode")
    with st.sidebar.form("identity_gate_form"):
        name_input = st.text_input("Enter Profile Name", value="Premium_Buyer")
        role_select = st.selectbox("Select Access Track", ["Verified Buyer", "Verified Builder / Owner"])
        btn_verify = st.form_submit_button("Authenticate Verification Profile")
        if btn_verify and name_input:
            st.session_state["username"] = name_input
            st.session_state["user_role"] = role_select
            st.sidebar.success("Verification Profile Loaded!")
            st.rerun()
else:
    st.sidebar.success(f"✅ Verified As: {st.session_state['username']}")
    st.sidebar.write(f"Track level: **{st.session_state['user_role']}**")
    if st.sidebar.button("Reset Identity Status"):
        st.session_state["user_role"] = "Guest"
        st.session_state["username"] = ""
        st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Navigation Panel", ["🔍 Marketplace Feed", "📊 Pricing Index Analytics", "🏗️ Property Management Panel"])

# --- HEADER REGION ---
st.title("🏢 DWELZA ENTERPRISE PRO")
st.markdown("##### Fraud-Free, High-Contrast Verified Real Estate Ecosystem")

# --- MAIN CONTROLLER ROUTER ---
if menu == "🔍 Marketplace Feed":
    st.subheader("Live Property Inventory")
    
    if not df_listings.empty:
        # Strict state validation filters
        active_listings = df_listings[df_listings['status'] == 'Active']
        
        for idx, row in active_listings.iterrows():
            st.markdown(f"""
            <div class='market-card'>
                <table style='width:100%; border:none; border-collapse:collapse;'>
                    <tr>
                        <td style='vertical-align:top; text-align:left;'>
                            <h3 style='margin:0;'>{row['title']}</h3>
                            <p style='margin:4px 0;'>📍 Locality Area: <strong>{row['locality']}</strong> | 📐 Size: <strong>{row['size_sqft']} Sq.Ft.</strong></p>
                        </td>
                        <td style='vertical-align:top; text-align:right; width:30%;'>
                            <div class='price-tag'>{format_indian_currency(row['price_inr'])}</div>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Interactive Streamlit operations columns below html framework structure safely
            c1, c2 = st.columns([2, 1])
            with c1:
                low_est, high_est = calculate_dwelzestimate(row['size_sqft'], row['locality'], row.get('near_metro', False), df_historical)
                st.markdown(f"""
                <div class='dwelz-box'>
                    <span style='color:#38bdf8; font-weight:bold;'>💡 Dwelzestimate Local Index Floor Bounds:</span><br>
                    <strong>{format_indian_currency(low_est)} - {format_indian_currency(high_est)}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                if row['price_inr'] < low_est * 0.85:
                    st.markdown("""
                    <div class='escrow-alert'>
                        ⚠️ <strong>CRITICAL VALUE ALERT:</strong> Listed price drops abnormally below baseline index averages. Verify structural ownership papers before giving offline tokens!
                    </div>
                    """, unsafe_allow_html=True)
            
            with c2:
                if st.session_state["user_role"] == "Guest":
                    st.warning("🔒 Authenticate via sidebar form to display contact stream parameters.")
                else:
                    st.write(f"👤 **Representative:** {row['owner_name']}")
                    st.code(f"+91 {row['owner_phone']}", language="text")
                    
                    text_msg = f"Hello {row['owner_name']}, I want to view '{row['title']}' via Dwelza Pro."
                    st.markdown(f'<a href="https://wa.me/91{row["owner_phone"]}?text={urllib.parse.quote(text_msg)}" target="_blank" class="wa-link-btn">💬 Open Direct WhatsApp Chat</a>', unsafe_allow_html=True)
            
            st.markdown("<hr style='border:1px solid #334155;'>", unsafe_allow_html=True)

elif menu == "📊 Pricing Index Analytics":
    st.subheader("Regional Price Tracking Metrics")
    if not df_historical.empty:
        st.plotly_chart(px.bar(df_historical, x="locality", y="avg_price_per_sqft", color="avg_price_per_sqft", title="Average Pricing Index per Locality"), use_container_width=True)

elif menu == "🏗️ Property Management Panel":
    st.subheader("Publish Asset Listing Records")
    if st.session_state["user_role"] != "Verified Builder / Owner":
        st.error("🚨 Access Restricted: Use the Identity Form on the left sidebar profile track to elevate status to 'Verified Builder / Owner'.")
    else:
        with st.form("new_listing_form"):
            t = st.text_input("Property Heading Title")
            l = st.text_input("Locality Target Node")
            p = st.number_input("Demanded Absolute Price (INR)", min_value=100000)
            s = st.number_input("Usable Area Blueprint Size (Sq.Ft.)", min_value=100)
            ph = st.text_input("Direct Phone Endpoint Link Target")
            submit = st.form_submit_button("Post Record")
            
            if submit and t and l and ph:
                new_id = int(df_listings['listing_id'].max() + 1 if not df_listings.empty else 1001)
                new_data = {
                    "listing_id": new_id, "title": t, "locality": l, "price_inr": p, "size_sqft": s,
                    "lat": 12.97, "lon": 77.59, "rera_number": "PENDING-VERIFICATION", "is_verified": False,
                    "veg_only": False, "bachelors_allowed": True, "near_metro": False,
                    "owner_name": st.session_state["username"], "owner_phone": ph,
                    "reports_count": 0, "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "expiry_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "status": "Active"
                }
                df_listings = pd.concat([df_listings, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df_listings, "Listings")
                st.success("Listing published live successfully!")
                st.rerun()
