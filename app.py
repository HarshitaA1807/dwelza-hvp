
import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
import plotly.express as px
from datetime import datetime, timedelta

# --- PRE-LOAD INTERACTIVE CONFIGURATION & ENTERPRISE DESIGN SHIMS ---
st.set_page_config(page_title="Dwelza Ecosystem Pro v5.0", page_icon="🏢", layout="wide")

# Extreme contrast CSS configuration enforcing absolute dark mode text visibility
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .main-title { font-size: 46px; font-weight: 800; color: #FF5A5F; text-align: center; margin-bottom: 2px; letter-spacing: -1px; }
    .sub-title { font-size: 16px; color: #cbd5e1; text-align: center; margin-bottom: 35px; letter-spacing: 1px; }
    
    /* Ultra-High Contrast Dark Mode Property Cards */
    .pro-card { 
        padding: 30px; 
        border-radius: 16px; 
        background-color: #0f172a !important; 
        margin-bottom: 30px; 
        border: 2px solid #334155 !important; 
        box-shadow: 0px 12px 30px rgba(0,0,0,0.5);
    }
    
    /* Strict font overrides to completely destroy white-out bugs */
    .pro-card h3, .pro-card h2, .pro-card p, .pro-card div, .pro-card span, .pro-card label {
        color: #ffffff !important;
    }
    .pro-text-muted {
        color: #94a3b8 !important;
        font-size: 14px;
    }
    .pro-highlight-blue {
        color: #38bdf8 !important;
        font-weight: 700;
    }
    
    /* Anti-Fraud Badges */
    .badge-rera { background-color: #16a34a; color: #ffffff !important; padding: 6px 14px; border-radius: 50px; font-size: 11px; font-weight: 800; text-transform: uppercase; display: inline-block; margin-bottom: 15px; letter-spacing: 0.5px; }
    .badge-unverified { background-color: #d97706; color: #ffffff !important; padding: 6px 14px; border-radius: 50px; font-size: 11px; font-weight: 800; text-transform: uppercase; display: inline-block; margin-bottom: 15px; letter-spacing: 0.5px; }
    .badge-stale { background-color: #dc2626; color: #ffffff !important; padding: 6px 14px; border-radius: 50px; font-size: 11px; font-weight: 800; text-transform: uppercase; display: inline-block; margin-bottom: 15px; letter-spacing: 0.5px; }
    
    /* Sub-Boxes with distinctive boundary lines */
    .pro-valuation-box { 
        background-color: #1e293b !important; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #475569 !important; 
        margin-top: 15px; 
    }
    .pro-escrow-alert { 
        background-color: #451a03 !important; 
        border: 1px solid #b45309 !important; 
        padding: 14px; 
        border-radius: 8px; 
        margin-top: 15px; 
    }
    
    /* Corporate Styled CTAs */
    .wa-pro-btn { 
        background-color: #25D366 !important; 
        color: #ffffff !important; 
        padding: 12px 24px; 
        border-radius: 8px; 
        text-decoration: none; 
        display: inline-block; 
        font-weight: bold; 
        margin-top: 12px; 
        font-size: 14px; 
        text-align: center; 
        box-shadow: 0px 4px 12px rgba(37,211,102,0.3);
        border: none;
    }
    .panel-header-box {
        background-color: #1d4ed8 !important;
        color: white !important;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE LAYER SETUP ---
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
        "avg_price_per_sqft":
