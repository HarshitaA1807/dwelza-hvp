
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
from datetime import datetime, timedelta

# --- PRE-LOAD INTERACTIVE CONFIGURATION & CUSTOM DESIGN SHIMS ---
st.set_page_config(page_title="Dwelza Ecosystem v3.0", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .main-title { font-size: 44px; font-weight: 800; color: #FF5A5F; text-align: center; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #666666; text-align: center; margin-bottom: 30px; letter-spacing: 1px; }
    .card { padding: 25px; border-radius: 14px; background-color: #ffffff; box-shadow: 0px 8px 24px rgba(0,0,0,0.04); margin-bottom: 25px; border: 1px solid #f0f2f6; }
    .verified-badge { background-color: #00C851; color: white; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; display: inline-block; }
    .unverified-badge { background-color: #ffbb33; color: white; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; display: inline-block; }
    .dwelzestimate-box { background-color: #F0F4F9; padding: 18px; border-radius: 10px; border-left: 6px solid #007bff; margin-top: 15px; }
    .wa-button { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; font-size: 14px; box-shadow: 0px 4px 10px rgba(37,211,102,0.2); }
    .auth-banner { background-color: #3F51B5; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- STATE CONTEXT MANAGER AND DATABASE INITIALIZATION ---
EXCEL_FILE = "source data.xlsx"

def initialize_database():
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
        "locality": ["Indiranagar, Bangalore", "Andheri West, Mumbai", "DLF Phase 3, Gurgaon", "OMR Sholinganallur, Chennai", "Adyar, Chennai", "Coimbatore Center", "Kakkanad, Kochi", "Thiruvananthapuram City"],
        "avg_price_per_sqft": [9500, 18000, 11500, 6200, 13500, 5500, 5800, 5200]
    }
    
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
            pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
    else:
        # If file exists but sheets are missing or structured incorrectly, let's fix them safely
        try:
            xl = pd.ExcelFile(EXCEL_FILE)
            if "Listings" not in xl.sheet_names or "HistoricalSales" not in xl.sheet_names:
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                    pd.DataFrame(default_listings).to_excel(writer, sheet_name="Listings", index=False)
                    pd.DataFrame(default_historical).to_excel(writer, sheet_name="HistoricalSales", index=False)
        except:
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                pd.DataFrame(default_listings).to_excel(writer, sheet_
