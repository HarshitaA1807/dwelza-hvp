
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

DB_FILE = "source data.xlsx"

# --- AUTOMATED SCHEMA TRANSLATION ENGINE ---
def auto_map_dataframe(df):
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
    if 'locality' not in df.columns: df['locality'] = 'Unknown Location Axis'
    if 'size_sqft' not in df.columns: df['size_sqft'] = 1000
    if 'price_inr' not in df.columns: df['price_inr'] = 5000000
    if 'transaction_type' not in df.columns: df['transaction_type'] = 'Buy'
    if 'status' not in df.columns: df['status'] = 'Active'
    
    df['locality'] = df['locality'].astype(str).str.strip()
    df['transaction_type'] = df['transaction_type'].astype(str).str.capitalize()
    df['status'] = df['status'].astype(str).str.capitalize()
    return df

# --- DATABASE SEED MATRIX (WITH SAMPLE IMAGES) ---
def seed_initial_database():
    if not os.path.exists(DB_FILE):
        default_listings = {
            "listing_id": [2001, 2002, 2003, 2004],
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
                "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=500&auto=format&fit=crop", # Apartment
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500&auto=format&fit=crop", # Studio
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=500&auto=format&fit=crop", # Modern flat
                "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=500&auto=format&fit=crop"  # Villa
            ],
            "rera_number": ["PRM/KA/RERA/1251", "", "", "TN/29/Building/0122/2026"],
            "is_verified": [True, False, False, True],
            "near_metro": [True, True, False, False],
            "owner_name": ["Rajesh Kumar", "Amit Sharma", "Karthik Raja", "Suresh Kumar"],
            "owner_phone": ["9999999999", "8888888888", "9444012345", "9846056789"],
            "status": ["Active", "Active", "Active", "Active"]
        }
        default_historical = {
            "locality": ["Whitefield, Bangalore", "Andheri West, Mumbai", "Ramanathapuram, Coimbatore", "Saravanampatti, Coimbatore"],
            "avg_price_per_sqft": [9500, 18000, 6000, 5200]
        }
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
            pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)

seed_initial_database()
df_listings = auto_map_dataframe(pd.read_excel(DB_FILE, sheet_name="Listings"))
df_historical = pd.read_excel(DB_FILE, sheet_name="HistoricalSales")

if "user_role" not in st.session_state: st.session_state["user_role"] = "Guest"
if "username" not in st.session_state: st.session_state["username"] = ""

def calculate_dynamic_valuation(size_sqft, locality, near_metro, txn_mode, historical_df):
    locality_lower = str(locality).lower()
    base_rate = None
    if not historical_df.empty and 'locality' in historical_df.columns:
        match = historical_df[historical_df['locality'].str.lower() == locality_lower]
        if not match.empty: base_rate = match['avg_price_per_sqft'].values[0]
    if base_rate is None:
        if "mumbai" in locality_lower: base_rate = 18000
        elif "bangalore" in locality_lower: base_rate = 9500
        elif "coimbatore" in locality_lower: base_rate = 5500
        else: base_rate = 6500
    final_capital = int(size_sqft * base_rate * (1.10 if near_metro else 1.05))
    if txn_mode in ["Rent", "Rented"]:
        predicted_rent = int((final_capital * 0.035) / 12)
        return int(predicted_rent * 0.90), int(predicted_rent * 1.10)
    return int(final_capital * 0.93), int(final_capital * 1.07)

def format_currency(num, txn_mode):
    if txn_mode in ["Rent", "Rented"]: return f"₹{num:,}/mo"
    if num >= 10000000: return f"₹{num / 10000000:.2f} Cr"
    elif num >= 100000: return f"₹{num / 100000:.2f} L"
    return f"₹{num:,}"

# --- MAIN APP LAYOUT FEED ---
st.title("🏢 Dwelza Interactive Luxury Property Ledger")
st.write("A rich visual interface showcasing live residential property portfolios and predictive analytics indexes.")
st.markdown("---")

# Global Omnipresent Navigation Search Layout Panel
with st.container(border=True):
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search Any Location, City, or Property Title...", value="", placeholder="Type anywhere (e.g., Coimbatore, Bangalore, Andheri...)")
    with col_s2:
        market_filter = st.selectbox("Market System Core", ["All Listings", "For Sale / Buy Only", "Rented Houses Only"])
    with col_s3:
        verif_filter = st.toggle("Show Verified Only (RERA Approved)")

if not df_listings.empty:
    processed_df = df_listings[df_listings['status'] == 'Active'].copy()
    if market_filter == "For Sale / Buy Only":
        processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('b')]
    elif market_filter == "Rented Houses Only":
        processed_df = processed_df[processed_df['transaction_type'].str.lower().str.startswith('r')]
    if verif_filter and 'is_verified' in processed_df.columns:
        processed_df = processed_df[processed_df['is_verified'] == True]
    if search_query:
        processed_df = processed_df[
            processed_df['locality'].str.contains(search_query, case=False, na=False) |
            processed_df['title'].str.contains(search_query, case=False, na=False)
        ]

    if not processed_df.empty:
        # Loop over filtered rows and display them inside a rich user card grid
        for idx, row in processed_df.iterrows():
            current_mode = "Rent" if str(row['transaction_type']).lower().startswith('r') else "Buy"
            
            # Use fallback image url if none is provided by the dataset source file
            img_url = row.get('image_url', "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500&auto=format&fit=crop")
            if pd.isna(img_url) or not str(img_url).strip():
                img_url = "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500&auto=format&fit=crop"

            # Create an isolated card boundary container block
            with st.container(border=True):
                col_img, col_det = st.columns([1.2, 2.5])
                
                with col_img:
                    # Renders high resolution architectural asset preview cards
                    st.image(img_url, use_container_width=True)
                
                with col_det:
                    # Header Badging Block Layout
                    c_tag, c_rera = st.columns([1, 2])
                    with c_tag:
                        if current_mode == "Rent":
                            st.markdown("🟢 **FOR RENT**")
                        else:
                            st.markdown("🔵 **FOR SALE**")
                    with c_rera:
                        if row.get('is_verified', False) or (hasattr(row, 'rera_number') and str(row.get('rera_number','')) != 'nan' and row.get('rera_number','')):
                            st.markdown("🔒 **RERA VERIFIED PRO**")
                    
                    st.subheader(row['title'])
                    st.markdown(f"📍 **Location Matrix Node:** {row['locality']}")
                    
                    # Core Attribute Metric Pills Display Row
                    m_p1, m_p2, m_p3 = st.columns(3)
                    m_p1.metric("Listed Asset Price", format_currency(int(row['price_inr']), current_mode))
                    m_p2.metric("Total Size scale", f"{int(row['size_sqft']):,} Sq.Ft.")
                    
                    c_low, c_high = calculate_dynamic_valuation(int(row['size_sqft']), row['locality'], row.get('near_metro', False), current_mode, df_historical)
                    m_p3.metric("AI Market Benchmark", f"{format_currency(c_low, current_mode)}")
                    
                    # Collapsible dynamic analytics panel built underneath each visual asset row
                    with st.expander("📊 Run Deep Algorithmic Estimation Matrix"):
                        st.info(f"💡 **AI Predictive Fair Valuation Market Spectrum:** {format_currency(c_low, current_mode)} to {format_currency(c_high, current_mode)}")
                        
                        # Interactive horizontal metric gauges indicating index positions
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = int(row['price_inr']),
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Market Variance Delta", 'font': {'size': 12}},
                            gauge = {
                                'axis': {'range': [None, c_high * 1.3]},
                                'bar': {'color': "#38bdf8"},
                                'steps': [
                                    {'range': [0, c_low], 'color': "rgba(255,255,255,0.05)"},
                                    {'range': [c_low, c_high], 'color': "rgba(56,189,248,0.2)"}
                                ]
                            }
                        ))
                        fig.update_layout(height=140, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
                        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{idx}")
    else:
        st.error("No active property listing elements match your structural filter arrays.")
