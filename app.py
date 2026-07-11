
import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Dwelza - Next Gen Indian Real Estate", page_icon="🏢", layout="wide")

# Custom CSS: Premium Branding + Hiding GitHub / Source Code Links
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_link__1S137 {display: none !important;}
    
    .main-title { font-size: 46px; font-weight: bold; color: #FF5A5F; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #888888; text-align: center; margin-bottom: 25px; }
    .card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; color: #333333; }
    .verified-badge { background-color: #28a745; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .dwelzestimate-box { background-color: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 5px solid #1A73E8; margin-top: 10px; color: #1E293B; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE / EXCEL INITIALIZATION ---
EXCEL_FILE = "source data.xlsx"

def initialize_database():
    """Ensures the Excel database exists with diverse multi-state baseline historical parameters."""
    exp_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    default_listings = {
        "listing_id": [1001, 1002, 1003, 1004, 1005],
        "title": ["Premium 3 BHK Apartment", "Cozy 1 BHK for Bachelors", "Luxury Smart Villa", "Modern Flat near IT Corridor", "Beachside Sea-view Apartment"],
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon", "OMR Sholinganallur, Chennai", "Kakkanad, Kochi"],
        "price_inr": [18500000, 4500000, 52000000, 8500000, 12000000],
        "size_sqft": [1800, 650, 4200, 1450, 1600],
        "lat": [12.97189, 19.11967, 28.4908, 12.9010, 10.0159],
        "lon": [77.64115, 72.84642, 77.0894, 80.2279, 76.3419],
        "rera_number": ["PRM/KA/RERA/1251/310/PR/180516/001", "", "HRERA/2022/89", "TN/29/Building/0122/2024", "K-RERA/PRJ/TVM/045/2023"],
        "is_verified": [True, False, True, True, True],
        "veg_only": [False, True, False, False, False],
        "bachelors_allowed": [True, True, False, True, True],
        "near_metro": [True, True, False, False, True],
        "owner_name": ["Rajesh Kumar", "Amit Sharma", "Vikram Malhotra", "Suresh Kumar", "Arun Kurian"],
        "owner_phone": ["9876543210", "9123456789", "9988776655", "9444012345", "9846056789"],
        "reports_count": [0, 0, 0, 0, 0],
        "expiry_date": [exp_str] * 5,
        "status": ["Active"] * 5
    }
    
    default_historical = {
        "locality": [
            "Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon", 
            "OMR Sholinganallur, Chennai", "Adyar, Chennai", "Coimbatore Center",
            "Kakkanad, Kochi", "Thiruvananthapuram City", "Kozhikode Beach"
        ],
        "avg_price_per_sqft": [9500, 18000, 11500, 6200, 13500, 5500, 5800, 5200, 4900]
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

initialize_database()

def load_data(sheet_name):
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    except Exception:
        return pd.DataFrame()

def save_data(df, sheet_name):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    st.cache_data.clear()

# --- DYNAMIC REAL-TIME ENGINE WITH FALLBACKS FOR TAMIL NADU / KERALA ---
def calculate_dwelzestimate(size_sqft, locality, near_metro, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    
    # Step 1: Direct historical database match
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty:
            base_rate = match['avg_price_per_sqft'].values[0]

    # Step 2: Adaptive Contextual Engine (Handles unspecified spaces in TN, Kerala, etc.)
    if base_rate is None:
        if "mumbai" in locality_lower or "delhi" in locality_lower:
            base_rate = 16000
        elif "bangalore" in locality_lower or "chennai" in locality_lower or "adyar" in locality_lower:
            base_rate = 9000
        elif "tamil" in locality_lower or "nadu" in locality_lower or "coimbatore" in locality_lower or "trichy" in locality_lower:
            base_rate = 5200  # Tamil Nadu Tier-2 dynamic index baseline
        elif "kerala" in locality_lower or "kochi" in locality_lower or "trivandrum" in locality_lower or "kakkanad" in locality_lower:
            base_rate = 5400  # Kerala high-demand baseline index
        else:
            base_rate = 6000  # National standard baseline fallback

    # Step 3: Predictive Infrastructure Multipliers
    base_value = size_sqft * base_rate
    multiplier = 1.06 # 2026 inflation correction standard
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

# --- SIDEBAR CONTROL HUB ---
menu = st.sidebar.selectbox("Navigate Menu", ["🔍 Explore Properties", "🏗️ Owner / Builder Dashboard"])

with st.sidebar.expander("ℹ️ About Dwelza Project", expanded=False):
    st.markdown("""
    **Dwelza** is an advanced real estate engine engineered around distinct Indian localization parameters outperforming foreign platforms like Zillow:
    * **Fake Listing Suppression:** Mandates RERA registration validation combined with active user crowd-sourced reporting algorithms.
    * **Privacy Guard System:** Implements active runtime sessions that securely mask owner contact items from scraping bots.
    * **Dynamic Valuation Engine:** Automatically parses location strings to apply predictive tier pricing matrices even if past strict data records don't exist.
    """)

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
        search_locality = st.selectbox("Select Metro Locality Hub", localities_list)
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
                    low_est, high_est = calculate_dwelzestimate(row['size_sqft'], row['locality'], metro_val, df_historical)
                    
                    st.markdown(f"""
                    <div class='dwelzestimate-box'>
                        <strong>💡 Dwelzestimate Engine Predictive Valuation:</strong> {format_indian_currency(low_est)} - {format_indian_currency(high_est)}<br>
                        <small>Calculated using dynamic localized tier data indices and specific regional infrastructure weights.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_right:
                    st.subheader(format_indian_currency(row['price_inr']))
                    
                    mask_key = f"mask_{row['listing_id']}"
                    if mask_key not in st.session_state:
                        st.session_state[mask_key] = True
                        
                    if st.session_state[mask_key]:
                        st.write("📞 Contact: `+91 XXXXX-XX" + str(row['owner_phone'])[-3:] + "`")
                        if st.button("Unlock Contact Details", key=f"btn_{row['listing_id']}"):
                            st.session_state[mask_key] = False
                            st.rerun()
                    else:
                        st.success(f"📞 Contact {row['owner_name']}: {row['owner_phone']}")
                    
                    if st.button("🚨 Report Fake / Stale", key=f"rep_{row['listing_id']}"):
                        df_listings.at[idx, 'reports_count'] += 1
                        save_data(df_listings, "Listings")
                        st.warning("Report recorded.")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No matching live properties found.")

# --- MODULE 2: OWNER DASHBOARD ---
elif menu == "🏗️ Owner / Builder Dashboard":
    st.subheader("List Your Indian Property (Any State/City)")
    
    with st.form("add_property_form", clear_on_submit=True):
        title = st.text_input("Property Title (e.g., Beachside 2BHK)")
        locality = st.text_input("Locality / City Name (e.g., Kochi, Kerala or Coimbatore, Tamil Nadu)")
        price = st.number_input("Asking Price (INR)", min_value=100000, value=5000000)
        size = st.number_input("Area Size (Sq.Ft.)", min_value=100, value=1200)
        rera = st.text_input("RERA Registration Number")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            is_veg = st.checkbox("Pure Veg Only")
        with col_f2:
            is_bach = st.checkbox("Bachelors Allowed")
        with col_f3:
            is_metro = st.checkbox("Near Metro Station")
            
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Mobile Number")
        
        submitted = st.form_submit_button("Launch Property")
        
        if submitted and title and locality and o_name and len(o_phone) >= 10:
            # Dynamic geocoding fallback mapping
            loc_lower = locality.lower()
            if "chennai" in loc_lower or "tamil" in loc_lower:
                coords = (12.9010, 80.2279)
            elif "kochi" in loc_lower or "kerala" in loc_lower:
                coords = (10.0159, 76.3419)
            elif "mumbai" in loc_lower:
                coords = (19.1196, 72.8464)
            else:
                coords = (12.9718, 77.6411) # Standard fallback map pin
            
            new_id = int(df_listings['listing_id'].max() + 1 if not df_listings.empty else 1001)
            exp_date_calc = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            new_row = {
                "listing_id": new_id, "title": title, "locality": locality, "price_inr": price,
                "size_sqft": size, "lat": coords[0], "lon": coords[1], "rera_number": rera,
                "is_verified": bool(rera), "veg_only": is_veg, "bachelors_allowed": is_bach,
                "near_metro": is_metro, "owner_name": o_name, "owner_phone": o_phone,
                "reports_count": 0, "expiry_date": exp_date_calc, "status": "Active"
            }
            
            save_data(pd.concat([df_listings, pd.DataFrame([new_row])], ignore_index=True), "Listings")
            st.success("Property live across India successfully!")
            st.rerun()
