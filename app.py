
import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Dwelza - Next Gen Indian Real Estate", page_icon="🏢", layout="wide")

# Custom CSS: Premium Branding + Hiding GitHub / Source Code Links + High Contrast Text
st.markdown("""
    <style>
    /* Hide the default Streamlit core structural link accents */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_link__1S137 {display: none !important;}
    
    /* Branding Styles */
    .main-title { font-size: 46px; font-weight: bold; color: #FF5A5F; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #555555; text-align: center; margin-bottom: 25px; }
    
    /* FIXED: Explicitly set text and heading colors to dark colors for maximum readability */
    .about-box { 
        background-color: #F0F4F8; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #DCE6F1; 
        margin-bottom: 30px; 
        color: #1E293B !important;
    }
    .about-box h4 { color: #0F172A !important; font-weight: bold !important; }
    .about-box li { color: #334155 !important; margin-bottom: 6px; }
    .about-box strong { color: #0F172A !important; }
    
    .card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; color: #333333; }
    .verified-badge { background-color: #28a745; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .dwelzestimate-box { background-color: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 5px solid #1A73E8; margin-top: 10px; color: #1E293B; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE / EXCEL INITIALIZATION ---
EXCEL_FILE = "source data.xlsx"

def initialize_database():
    """Ensures the Excel database exists and fixes missing sheets if file already exists."""
    exp_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    default_listings = {
        "listing_id": [1001, 1002, 1003],
        "title": ["Premium 3 BHK Apartment", "Cozy 1 BHK for Bachelors", "Luxury Smart Villa"],
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon"],
        "price_inr": [18500000, 4500000, 52000000],
        "size_sqft": [1800, 650, 4200],
        "lat": [12.97189, 19.11967, 28.4908],
        "lon": [77.64115, 72.84642, 77.0894],
        "rera_number": ["PRM/KA/RERA/1251/310/PR/180516/001", "", "HRERA/2022/89"],
        "is_verified": [True, False, True],
        "veg_only": [False, True, False],
        "bachelors_allowed": [True, True, False],
        "near_metro": [True, True, False],
        "owner_name": ["Rajesh Kumar", "Amit Sharma", "Vikram Malhotra"],
        "owner_phone": ["9876543210", "9123456789", "9988776655"],
        "reports_count": [0, 0, 0],
        "expiry_date": [exp_str, exp_str, exp_str],
        "status": ["Active", "Active", "Active"]
    }
    
    default_historical = {
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon"],
        "avg_price_per_sqft": [9500, 18000, 11500]
    }

    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
            pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
            pd.DataFrame(columns=["inquiry_id", "listing_id", "user_name", "user_phone", "timestamp"]).to_excel(writer, sheet_name="Inquiries", index=False)
    else:
        try:
            excel_reader = pd.ExcelFile(EXCEL_FILE)
            sheets_present = excel_reader.sheet_names
        except Exception:
            sheets_present = []
        
        if "Listings" not in sheets_present or "HistoricalSales" not in sheets_present:
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
                pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
                pd.DataFrame(columns=["inquiry_id", "listing_id", "user_name", "user_phone", "timestamp"]).to_excel(writer, sheet_name="Inquiries", index=False)

initialize_database()

def load_data(sheet_name):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        if sheet_name == "Listings":
            if "near_metro" not in df.columns:
                df["near_metro"] = True
            if "reports_count" not in df.columns:
                df["reports_count"] = 0
        return df
    except Exception:
        if sheet_name == "HistoricalSales":
            return pd.DataFrame({"locality": ["Indiranagar, Bangalore"], "avg_price_per_sqft": [9500]})
        return pd.DataFrame()

def save_data(df, sheet_name):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    st.cache_data.clear()

# --- REAL-TIME VALUATION SYSTEM ---
def calculate_dwelzestimate(size_sqft, locality, near_metro, historical_df):
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'] == locality]
        base_rate = match['avg_price_per_sqft'].values[0] if not match.empty else 7000
    else:
        base_rate = 7000
        
    base_value = size_sqft * base_rate
    multiplier = 1.06
    if near_metro:
        multiplier += 0.12
    
    final_val = int(base_value * multiplier)
    return int(final_val * 0.95), int(final_val * 1.05)

def format_indian_currency(num):
    if num >= 10000000:
        return f"₹{num / 10000000:.2f} Crore"
    elif num >= 100000:
        return f"₹{num / 100000:.2f} Lakh"
    else:
        return f"₹{num:,}"

# --- APP BRANDING HEADER ---
st.markdown("<div class='main-title'>DWELZA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Next-Gen Fraud-Free Indian Real Estate Marketplace</div>", unsafe_allow_html=True)

# --- "ABOUT THE APP" OVERVIEW CONTAINER ---
st.markdown("""
<div class='about-box'>
    <h4>💡 What is Dwelza?</h4>
    <p><strong>Dwelza</strong> is an advanced web portal built specifically to address the core challenges of the Indian residential real estate market. 
    Unlike foreign platforms like Zillow, Dwelza is engineered around local market dynamics with three key structural goals:</p>
    <ul>
        <li><strong>Fake Listing Suppression:</strong> Integrates mandatory Indian RERA registration checks and community reporting algorithms to instantly eliminate broker bait-and-switch listings.</li>
        <li><strong>Privacy Protection (Anti-Spam):</strong> Masks owner contact details using active sessions to keep telephone details hidden from continuous scraping bots and spam telemarketers.</li>
        <li><strong>The Real-Time Dwelzestimate:</strong> An algorithmic valuation engine adjusted for Indian properties using historical area records, local public infrastructure parameters (like Metro proximity), and current index factors to counter manual market price manipulation.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Navigate Menu", ["🔍 Explore Properties", "🏗️ Owner / Builder Dashboard"])

df_listings = load_data("Listings")
df_historical = load_data("HistoricalSales")

if not df_listings.empty and 'reports_count' in df_listings.columns:
    df_listings.loc[df_listings['reports_count'] >= 3, 'status'] = 'Under Review'
    active_listings = df_listings[df_listings['status'] == 'Active']
else:
    active_listings = df_listings

# --- MODULE 1: EXPLORE PROPERTIES ---
if menu == "🔍 Explore Properties":
    st.subheader("Explore Verified Property Feeds")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        localities_list = ["All"] + list(df_historical['locality'].unique()) if not df_historical.empty else ["All"]
        search_locality = st.selectbox("Select Metro Locality", localities_list)
    with col2:
        diet_pref = st.checkbox("🟢 Pure Veg Only")
    with col3:
        bachelor_pref = st.checkbox("🎓 Bachelors Welcome")
    with col4:
        max_price = st.slider("Max Budget (INR)", min_value=1000000, max_value=100000000, value=75000000, step=500000)

    filtered_df = active_listings.copy()
    if not filtered_df.empty:
        if search_locality != "All" and 'locality' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['locality'] == search_locality]
        if diet_pref and 'veg_only' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['veg_only'] == True]
        if bachelor_pref and 'bachelors_allowed' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['bachelors_allowed'] == True]
        if 'price_inr' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['price_inr'] <= max_price]

    if not filtered_df.empty and 'lat' in filtered_df.columns:
        st.write(f"Showing {len(filtered_df)} verified live listings:")
        st.map(filtered_df[['lat', 'lon']])
        
        for idx, row in filtered_df.iterrows():
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                c_left, c_right = st.columns([2, 1])
                
                with c_left:
                    is_ver = row.get('is_verified', False)
                    badge = "<span class='verified-badge'>✓ RERA VERIFIED</span>" if is_ver else ""
                    st.markdown(f"### {row['title']} {badge}", unsafe_allow_html=True)
                    st.write(f"📍 **Locality:** {row['locality']} | 📐 **Size:** {row['size_sqft']} Sq.Ft.")
                    
                    metro_val = row.get('near_metro', False)
                    low_est, high_est = calculate_dwelzestimate(row['size_sqft'], row['locality'], metro_val)
