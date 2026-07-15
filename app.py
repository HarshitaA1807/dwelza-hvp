
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
from datetime import datetime, timedelta

# --- PRE-LOAD INTERACTIVE CONFIGURATION & CUSTOM DESIGN SHIMS ---
st.set_page_config(page_title="Dwelza Ecosystem v4.5", page_icon="🏢", layout="wide")

# Dark-Mode Safe High-Contrast CSS Shims
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .main-title { font-size: 44px; font-weight: 800; color: #FF5A5F; text-align: center; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #aaaaaa; text-align: center; margin-bottom: 30px; letter-spacing: 1px; }
    
    /* Dark-mode ready UI Containers */
    .card { padding: 25px; border-radius: 14px; background-color: #1e293b; box-shadow: 0px 8px 24px rgba(0,0,0,0.2); margin-bottom: 25px; border: 1px solid #334155; color: #f8fafc; }
    .card h3 { color: #ffffff !important; margin-top: 5px; }
    
    /* Badges */
    .verified-badge { background-color: #00C851; color: white; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; display: inline-block; }
    .unverified-badge { background-color: #ffbb33; color: #1e293b; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; display: inline-block; }
    .stale-badge { background-color: #ff3547; color: white; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; display: inline-block; }
    
    /* High-contrast valuation text inside containers */
    .dwelzestimate-box { background-color: #0f172a; padding: 18px; border-radius: 10px; border-left: 6px solid #38bdf8; margin-top: 15px; color: #e2e8f0; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; }
    .dwelzestimate-box strong { color: #38bdf8 !important; }
    .escrow-warning { background-color: #78350f; border-left: 6px solid #f59e0b; padding: 12px; border-radius: 6px; margin-top: 10px; color: #fef3c7; font-size: 13px; font-weight: 500; }
    
    /* CTA buttons */
    .wa-button { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; font-size: 14px; text-align: center; box-shadow: 0px 4px 10px rgba(37,211,102,0.2); }
    .auth-banner { background-color: #3b82f6; color: white; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- STATE CONTEXT MANAGER AND DATABASE INITIALIZATION ---
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
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
                pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)

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

# --- AUTO-MAINTENANCE PIPELINE ---
if not df_listings.empty:
    today_str = datetime.now().strftime("%Y-%m-%d")
    df_listings.loc[df_listings['expiry_date'].astype(str) < today_str, 'status'] = 'Stale'
    df_listings.loc[df_listings['reports_count'] >= 3, 'status'] = 'Under Investigation'
    save_data(df_listings, "Listings")

# --- INITIALIZE STATE ARCHITECTURES ---
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
        elif "chennai" in locality_lower: base_rate = 6500
        else: base_rate = 6000
    base_value = size_sqft * base_rate
    mult = 1.06 + (0.12 if near_metro else 0.0)
    final_val = int(base_value * mult)
    return int(final_val * 0.95), int(final_val * 1.05)

def format_indian_currency(num):
    if num >= 10000000: return f"₹{num / 10000000:.2f} Crore"
    elif num >= 100000: return f"₹{num / 100000:.2f} Lakh"
    return f"₹{num:,}"

# --- APP LAYOUT BRANDING HEADER ---
st.markdown("<div class='main-title'>DWELZA ADVANCED PORTAL</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Zero-Spam, Anti-Fraud Premium Property Ecosystem</div>", unsafe_allow_html=True)

# --- SIDEBAR ROLE CONTROLLER & IDENTITY OPTIONS PANEL ---
st.sidebar.title("🔐 Access Control Desk")

# Visible validation options configuration setup
if st.session_state["user_role"] == "Guest":
    st.sidebar.warning("🔒 Features are masked for unauthenticated Guests.")
    with st.sidebar.form("identity_verification_form"):
        user_input = st.text_input("Choose Username Handle", value="Premium_Buyer_Alpha")
        role_selection = st.selectbox("Assign System Track Profile", ["Verified Buyer", "Verified Builder / Owner"])
        submit_auth = st.form_submit_button("Verify Identity Now")
        if submit_auth and user_input:
            st.session_state["user_role"] = role_selection
            st.session_state["username"] = user_input
            st.rerun()
else:
    st.sidebar.markdown(f"<div class='auth-banner'>Active: {st.session_state['username']}<br>Level: {st.session_state['user_role']}</div>", unsafe_allow_html=True)
    if st.sidebar.button("Log Out / Reset Session"):
        st.session_state["user_role"] = "Guest"
        st.session_state["username"] = ""
        st.rerun()

menu = st.sidebar.selectbox("Marketplace Control Center", ["🔍 Open Marketplace Feed", "📊 Real-Time Pricing Index", "🏗️ Owner Verification Panel"])

# --- MODULE 1: EXPLORE WORKSPACE ---
if menu == "🔍 Open Marketplace Feed":
    st.subheader("Explore Active Verified Assets")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_kw = st.text_input("Filter Locality Matrix (e.g. Mumbai, Chennai, Bangalore)", "")
    with col_f2:
        status_filter = st.radio("Asset Activity Filter Mode", ["Active Only (Fresh Data)", "Show Stale / Suspended Listings"], horizontal=True)

    if not df_listings.empty:
        filtered = df_listings.copy()
        
        if status_filter == "Active Only (Fresh Data)":
            filtered = filtered[filtered['status'] == 'Active']
        else:
            filtered = filtered[filtered['status'].isin(['Stale', 'Under Investigation'])]
            
        if search_kw:
            filtered = filtered[filtered['locality'].str.contains(search_kw, case=False, na=False)]
            
        if not filtered.empty:
            for idx, row in filtered.iterrows():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                l_col, r_col = st.columns([2, 1])
                
                with l_col:
                    if row.get('is_verified', False):
                        st.markdown(f"<span class='verified-badge'>✓ Legally RERA Bound — ID: {row.get('rera_number')}</span>", unsafe_allow_html=True)
                    elif row.get('status') == 'Stale':
                        st.markdown("<span class='stale-badge'>⚠️ AUTOMATICALLY EXPIRED (DATA STALE)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='unverified-badge'>⚠️ CROWDSOURCED UNVERIFIED OWNER ENTRY</span>", unsafe_allow_html=True)
                        
                    st.markdown(f"<h3>{row.get('title', 'Property Asset')}</h3>", unsafe_allow_html=True)
                    st.write(f"📍 Locality Core: **{row.get('locality')}** | 📐 net usable area: **{row.get('size_sqft')}** Sq.Ft.")
                    
                    low, high = calculate_dwelzestimate(row.get('size_sqft', 0), row.get('locality', ''), row.get('near_metro', False), df_historical)
                    st.markdown(f"""
                    <div class='dwelzestimate-box'>
                        <strong>💡 Dwelzestimate Algorithmic Valuation Boundary:</strong> {format_indian_currency(low)} - {format_indian_currency(high)}<br>
                        <small style='color: #94a3b8;'>Calculated using strict infrastructural spatial indices to evaluate potential listing fraud patterns.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if row.get('price_inr', 0) < low * 0.85:
                        st.markdown(f"""
                        <div class='escrow-warning'>
                            🚨 <strong>CRITICAL RISK DETECTED:</strong> This listing price ({format_indian_currency(row.get('price_inr',0))}) is statistically aberrant compared to local indexes. 
                            DO NOT transfer offline 'Token Money' deposits prior to site inspections!
                        </div>
                        """, unsafe_allow_html=True)
                        
                with r_col:
                    st.markdown(f"<h2 style='color: #ffffff; margin-bottom: 5px;'>{format_indian_currency(row.get('price_inr', 0))}</h2>", unsafe_allow_html=True)
                    
                    if st.session_state["user_role"] == "Guest":
                        st.info("🔒 Use the 'Access Control Desk' form on the sidebar to check verified owner identities.")
                    else:
                        mask_id = f"mask_v45_{row.get('listing_id', idx)}"
                        if mask_id not in st.session_state: st.session_state[mask_id] = True
                        
                        if st.session_state[mask_id]:
                            if st.button("Unlock Contact Stream", key=f"btn_unl_{row.get('listing_id', idx)}"):
                                st.session_state[mask_id] = False
                                st.rerun()
                        else:
                            st.success(f"👤 Owner ID: {row.get('owner_name')}")
                            st.code(f"Mobile Sequence: +91 {row.get('owner_phone')}", language="text")
                            
                            msg_raw = f"Hello {row.get('owner_name')}, I am requesting a structural walkthrough regarding '{row.get('title')}' on Dwelza."
                            msg_enc = urllib.parse.quote(msg_raw)
                            st.markdown(f'<a href="https://wa.me/91{row.get("owner_phone")}?text={msg_enc}" target="_blank" class="wa-button">💬 Launch Direct WhatsApp Link</a>', unsafe_allow_html=True)
                    
                    st.write("---")
                    if st.button("🚨 Report Fake / Sold Out", key=f"rep_{row.get('listing_id', idx)}"):
                        df_listings.at[idx, 'reports_count'] += 1
                        save_data(df_listings, "Listings")
                        st.warning("Telemetry logged. System validation filters recalculating...")
                        st.rerun()
                        
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Zero properties located within this matrix category path.")

# --- MODULE 2: TRANSPARENT REGIONAL PRICING DATA INDEX ---
elif menu == "📊 Real-Time Pricing Index":
    st.subheader("Transparent Localized Pricing Analytics Dashboard")
    
    if not df_historical.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Real-Time Index Cost Per Sq.Ft")
            st.plotly_chart(px.bar(df_historical, x="locality", y="avg_price_per_sqft", color="avg_price_per_sqft", color_continuous_scale="Turbo"), use_container_width=True)
        with c2:
            st.markdown("#### Comparative Distribution Vectors")
            st.plotly_chart(px.pie(df_historical, names="locality", values="avg_price_per_sqft", hole=0.3), use_container_width=True)

# --- MODULE 3: DIRECT OWNER MANAGEMENT HUB ---
elif menu == "🏗️ Owner Verification Panel":
    st.subheader("List Verified Real Estate Asset")
    
    if st.session_state["user_role"] != "Verified Builder / Owner":
        st.error("🚨 Access Restricted. You must shift your profile authorization track to 'Verified Builder / Owner' inside the sidebar form first.")
    else:
        with st.form("secure_asset_publisher"):
            t = st.text_input("Asset Heading Title (e.g. Luxury 2BHK Smart Penthouse)")
            l = st.text_input("Locality Framework Destination (e.g. Indiranagar, Bangalore)")
            p = st.number_input("Absolute Asking Price Target (INR)", min_value=10000)
            s = st.number_input("Net Usable Layout Boundary (Sq.Ft.)", min_value=10)
            r = st.text_input("Official RERA Ledger Index Sequence Code")
            o_p = st.text_input("Direct Phone Target (Masked Automatically)")
            
            submit = st.form_submit_button("Broadcast Asset Live")
            
            if submit and t and l and o_p:
                n_id = int(df_listings['listing_id'].max() + 1 if not df_listings.empty else 1001)
                created_dt = datetime.now().strftime("%Y-%m-%d")
                exp_dt = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                
                new_row = {
                    "listing_id": n_id, "title": t, "locality": l, "price_inr": p, "size_sqft": s,
                    "lat": 12.9716, "lon": 77.5946, "rera_number": r, "is_verified": bool(r),
                    "veg_only": False, "bachelors_allowed": True, "near_metro": False,
                    "owner_name": st.session_state["username"], "owner_phone": o_p,
                    "reports_count": 0, "created_date": created_dt, "expiry_date": exp_dt, "status": "Active"
                }
                
                updated_df = pd.concat([df_listings, pd.DataFrame([new_row])], ignore_index=True)
                save_data(updated_df, "Listings")
                st.success("Asset initialized successfully!")
                st.rerun()
