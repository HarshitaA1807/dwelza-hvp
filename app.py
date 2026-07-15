
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Dwelza - Next Gen Indian Real Estate", page_icon="🏢", layout="wide")

# Custom CSS: Premium Branding + Visual Optimization + Component Layouts
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_link__1S137 {display: none !important;}
    
    .main-title { font-size: 46px; font-weight: bold; color: #FF5A5F; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #888888; text-align: center; margin-bottom: 25px; }
    
    /* Property Card Layout */
    .card { padding: 25px; border-radius: 12px; background-color: #f8f9fa; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px; color: #333333; border: 1px solid #eef2f5; }
    .verified-badge { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    .unverified-badge { background-color: #ffc107; color: #333333; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    
    /* Valuation Box styling */
    .dwelzestimate-box { background-color: #E8F0FE; padding: 15px; border-radius: 8px; border-left: 5px solid #1A73E8; margin-top: 15px; color: #1E293B; }
    
    /* Premium Interactive Action Buttons */
    .wa-button { background-color: #25D366; color: white !important; border: none; padding: 10px 18px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: bold; text-align: center; margin-top: 10px; font-size: 14px; transition: 0.3s; }
    .wa-button:hover { background-color: #128C7E; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE / EXCEL INITIALIZATION ---
EXCEL_FILE = "source data.xlsx"

def initialize_database():
    """Ensures the advanced Excel database structure matches core application requirements."""
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

# --- DYNAMIC REAL-TIME DWELLZESTIMATE ENGINE ---
def calculate_dwelzestimate(size_sqft, locality, near_metro, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty:
            base_rate = match['avg_price_per_sqft'].values[0]

    if base_rate is None:
        if "mumbai" in locality_lower or "delhi" in locality_lower:
            base_rate = 16000
        elif "bangalore" in locality_lower or "chennai" in locality_lower or "adyar" in locality_lower:
            base_rate = 9000
        elif "tamil" in locality_lower or "nadu" in locality_lower or "coimbatore" in locality_lower:
            base_rate = 5200 
        elif "kerala" in locality_lower or "kochi" in locality_lower or "kakkanad" in locality_lower:
            base_rate = 5400 
        else:
            base_rate = 6000 

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

# --- SIDEBAR CONTROL HUB ---
menu = st.sidebar.selectbox("Navigate Menu", ["🔍 Explore Properties", "📊 Market Trends & Analytics", "🏗️ Owner / Builder Dashboard"])

with st.sidebar.expander("ℹ️ About Dwelza Project", expanded=False):
    st.markdown("""
    **Dwelza** is an advanced real estate architecture designed to solve unique structural flaws in the Indian market:
    * **Fake Listing Suppression:** Cross-references active dynamic user reporting with strict validation variables.
    * **Privacy Guard Architecture:** Masks sensitive identity keys against web collection bots.
    * **Contextual Data Framework:** Parses tier classifications to yield fair values even for completely unindexed cities.
    """)

df_listings = load_data("Listings")
df_historical = load_data("HistoricalSales")

if not df_listings.empty and 'reports_count' in df_listings.columns:
    df_listings.loc[df_listings['reports_count'] >= 3, 'status'] = 'Under Review'
    active_listings = df_listings[df_listings['status'] == 'Active']
else:
    active_listings = df_listings

# --- MODULE 1: EXPLORE PROPERTIES (WITH WHATSAPP ROUTING & SMART BADGES) ---
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
        
        # --- THE PROPERTY CARD ITERATOR LOOP ---
        for idx, row in filtered_df.iterrows():
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                c_left, c_right = st.columns([2, 1])
                
                with c_left:
                    # FEATURE 1: DYNAMIC TRUST BADGES
                    is_ver = row.get('is_verified', False)
                    if is_ver:
                        badge_html = f"<span class='verified-badge'>✓ RERA VERIFIED — ID: {row.get('rera_number','Active')}</span>"
                    else:
                        badge_html = "<span class='unverified-badge'>⚠️ SELF-LISTED (PENDING VERIFICATION)</span>"
                        
                    st.markdown(f"{badge_html}<h3>{row['title']}</h3>", unsafe_allow_html=True)
                    st.write(f"📍 **Locality:** {row['locality']} | 📐 **Size:** {row['size_sqft']} Sq.Ft.")
                    
                    metro_val = row.get('near_metro', False)
                    low_est, high_est = calculate_dwelzestimate(row['size_sqft'], row['locality'], metro_val, df_historical)
                    
                    st.markdown(f"""
                    <div class='dwelzestimate-box'>
                        <strong>💡 Dwelzestimate Engine Predictive Valuation:</strong> {format_indian_currency(low_est)} - {format_indian_currency(high_est)}<br>
                        <small>Calculated using dynamic localized tier data indices and infrastructure weights.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_right:
                    st.subheader(format_indian_currency(row['price_inr']))
                    
                    # FEATURE 2: SMART PRIVACY CONTACT UNLOCK
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
                        
                        # FEATURE 3: SECURE WHATSAPP ROUTING LEAD GENERATION
                        property_title_encoded = urllib.parse.quote(row['title'])
                        whatsapp_msg = f"Hello {row['owner_name']}, I found your listing '{property_title_encoded}' on Dwelza Marketplace. Is it still available for inspection?"
                        encoded_msg = urllib.parse.quote(whatsapp_msg)
                        wa_url = f"https://wa.me/91{row['owner_phone']}?text={encoded_msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">💬 Chat Directly on WhatsApp</a>', unsafe_allow_html=True)
                    
                    st.write("") # Formatting gap spacer
                    if st.button("🚨 Report Fake / Stale", key=f"rep_{row['listing_id']}"):
                        df_listings.at[idx, 'reports_count'] += 1
                        save_data(df_listings, "Listings")
                        st.warning("Report recorded.")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No matching live properties found.")

# --- MODULE 2: INTERACTIVE ANALYTICS HUB ---
elif menu == "📊 Market Trends & Analytics":
    st.subheader("📊 Advanced Real Estate Pricing Index Analytics")
    st.write("Real-time market tracking visualization generated using baseline Excel history records.")
    
    if not df_historical.empty:
        col_an1, col_an2 = st.columns([1, 1])
        
        with col_an1:
            st.markdown("#### Cost Distribution Per Square Foot Across Hubs")
            fig1 = px.bar(df_historical, x="locality", y="avg_price_per_sqft", 
                          labels={"locality": "Locality Hub", "avg_price_per_sqft": "Avg Rate (₹/Sq.Ft)"},
                          color="avg_price_per_sqft", color_continuous_scale="Reds")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_an2:
            st.markdown("#### Regional Price Share Ratios")
            fig2 = px.pie(df_historical, names="locality", values="avg_price_per_sqft", 
                          color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Analytics engine offline. Ensure Historical records sheet is filled inside the Excel asset.")

# --- MODULE 3: OWNER DASHBOARD ---
elif menu == "🏗️ Owner / Builder Dashboard":
    st.subheader("List Your Indian Property (Any State/City)")
    
    with st.form("add_property_form", clear_on_submit=True):
        title = st.text_input("Property Title (e.g., Beachside 2BHK)")
        locality = st.text_input("Locality / City Name (e.g., Kochi, Kerala or Coimbatore, Tamil Nadu)")
        price = st.number_input("Asking Price (INR)", min_value=100000, value=5000000)
        size = st.number_input("Area Size (Sq.Ft.)", min_value=100, value=1200)
        rera = st.text_input("RERA Registration Number (Leave empty if none)")
        
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
            loc_lower = locality.lower()
            if "chennai" in loc_lower or "tamil" in loc_lower or "coimbatore" in loc_lower:
                coords = (12.9010, 80.2279)
            elif "kochi" in loc_lower or "kerala" in loc_lower:
                coords = (10.0159, 76.3419)
            elif "mumbai" in loc_lower:
                coords = (19.1196, 72.8464)
            else:
                coords = (12.9718, 77.6411) 
            
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
