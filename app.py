
import streamlit as st
import pandas as pd
import random
from datetime import datetime
import json
import base64
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Dwelza - India's Premier Real Estate Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main header gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 3rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Property cards */
    .property-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid #f0f0f0;
    }
    
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .property-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    /* Price tag */
    .price-tag {
        color: #1a73e8;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Badge styles */
    .badge-sale {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-rent {
        background: #ffc107;
        color: #333;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-lease {
        background: #17a2b8;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Broker info */
    .broker-info {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        border-left: 3px solid #1a73e8;
    }
    
    /* Stats boxes */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s;
    }
    
    .stat-box:hover {
        transform: scale(1.05);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a73e8;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        padding: 1rem 0;
    }
    
    .login-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1a73e8;
        color: white;
    }
    
    /* Footer */
    .footer {
        background: #2c3e50;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
    }
    
    .footer a {
        color: #8ab4f8;
        text-decoration: none;
    }
    
    .footer a:hover {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_broker' not in st.session_state:
        st.session_state.is_broker = False
    if 'users' not in st.session_state:
        # Sample users
        st.session_state.users = {
            "broker": {
                "password": "broker123",
                "email": "broker@dwelza.com",
                "phone": "+91 98765 43210",
                "is_broker": True
            },
            "user": {
                "password": "user123",
                "email": "user@dwelza.com",
                "phone": "+91 98765 43211",
                "is_broker": False
            }
        }
    if 'properties' not in st.session_state:
        st.session_state.properties = []
    if 'bookings' not in st.session_state:
        st.session_state.bookings = {}
    if 'favorites' not in st.session_state:
        st.session_state.favorites = set()

# Initialize sample data
def init_sample_data():
    if not st.session_state.properties:
        # Sample properties with real broker contacts
        sample_properties = [
            {
                "id": 1,
                "title": "Luxury Apartment in Andheri West",
                "price": 4500000,
                "location": "Andheri West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 1500,
                "type": "Sale",
                "property_type": "Apartment",
                "description": "Beautiful 3 BHK apartment with sea view, modular kitchen, and premium amenities. Close to shopping malls and restaurants.",
                "broker_name": "Rajesh Kumar",
                "broker_phone": "+91 98100 12345",
                "broker_email": "rajesh.k@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1560448204-603b3fc33ddc?w=800",
                "available": True,
                "features": ["Sea View", "Modular Kitchen", "Gym", "Pool", "Parking"]
            },
            {
                "id": 2,
                "title": "Premium Villa in Banjara Hills",
                "price": 25000000,
                "location": "Banjara Hills",
                "city": "Hyderabad",
                "state": "Telangana",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 3500,
                "type": "Sale",
                "property_type": "Villa",
                "description": "Stunning 4 BHK villa with private pool, landscaped garden, and 24/7 security. Located in one of Hyderabad's most prestigious neighborhoods.",
                "broker_name": "Priya Sharma",
                "broker_phone": "+91 98200 23456",
                "broker_email": "priya.s@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800",
                "available": True,
                "features": ["Private Pool", "Garden", "Security", "Gym", "Parking"]
            },
            {
                "id": 3,
                "title": "Modern 2 BHK in Koramangala",
                "price": 35000,
                "location": "Koramangala",
                "city": "Bangalore",
                "state": "Karnataka",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 1100,
                "type": "Rent",
                "property_type": "Apartment",
                "description": "Fully furnished 2 BHK with modern amenities, close to IT parks. Perfect for professionals working in the tech hub.",
                "broker_name": "Amit Patel",
                "broker_phone": "+91 98300 34567",
                "broker_email": "amit.p@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1560448204-603b3fc33ddc?w=800",
                "available": True,
                "features": ["Fully Furnished", "AC", "Security", "Parking"]
            },
            {
                "id": 4,
                "title": "Spacious Penthouse in Connaught Place",
                "price": 80000000,
                "location": "Connaught Place",
                "city": "Delhi",
                "state": "Delhi",
                "bedrooms": 5,
                "bathrooms": 4,
                "area": 4500,
                "type": "Sale",
                "property_type": "Penthouse",
                "description": "Luxurious 5 BHK penthouse with panoramic city views and terrace garden. Located in the heart of Delhi.",
                "broker_name": "Sneha Reddy",
                "broker_phone": "+91 98400 45678",
                "broker_email": "sneha.r@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
                "available": True,
                "features": ["Terrace Garden", "City View", "Security", "Parking"]
            },
            {
                "id": 5,
                "title": "Beach View Apartment in Colaba",
                "price": 120000,
                "location": "Colaba",
                "city": "Mumbai",
                "state": "Maharashtra",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 1800,
                "type": "Rent",
                "property_type": "Apartment",
                "description": "Premium 3 BHK with Arabian Sea views, fully furnished, gated community with all amenities.",
                "broker_name": "Vikram Singh",
                "broker_phone": "+91 98500 56789",
                "broker_email": "vikram.s@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800",
                "available": True,
                "features": ["Sea View", "Fully Furnished", "Pool", "Gym"]
            },
            {
                "id": 6,
                "title": "Elegant Villa in Jubilee Hills",
                "price": 38000000,
                "location": "Jubilee Hills",
                "city": "Hyderabad",
                "state": "Telangana",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 4200,
                "type": "Sale",
                "property_type": "Villa",
                "description": "Exclusive 4 BHK villa with landscaped garden, swimming pool, and private gym. Premium location with excellent connectivity.",
                "broker_name": "Anjali Mehta",
                "broker_phone": "+91 98600 67890",
                "broker_email": "anjali.m@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
                "available": True,
                "features": ["Pool", "Garden", "Gym", "Security", "Parking"]
            },
            {
                "id": 7,
                "title": "Studio Apartment in Whitefield",
                "price": 25000,
                "location": "Whitefield",
                "city": "Bangalore",
                "state": "Karnataka",
                "bedrooms": 1,
                "bathrooms": 1,
                "area": 600,
                "type": "Rent",
                "property_type": "Studio",
                "description": "Cozy studio apartment ideal for singles/couples, near tech parks and shopping centers.",
                "broker_name": "Suresh Iyer",
                "broker_phone": "+91 98700 78901",
                "broker_email": "suresh.i@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1560448204-603b3fc33ddc?w=800",
                "available": True,
                "features": ["Furnished", "AC", "Security"]
            },
            {
                "id": 8,
                "title": "Luxury Penthouse in Bandra",
                "price": 65000,
                "location": "Bandra",
                "city": "Mumbai",
                "state": "Maharashtra",
                "bedrooms": 3,
                "bathrooms": 3,
                "area": 2200,
                "type": "Rent",
                "property_type": "Penthouse",
                "description": "Stunning 3 BHK penthouse with sea views, private terrace, and high-end finishes.",
                "broker_name": "Deepa Nair",
                "broker_phone": "+91 98800 89012",
                "broker_email": "deepa.n@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
                "available": True,
                "features": ["Sea View", "Private Terrace", "Security", "Parking"]
            },
            {
                "id": 9,
                "title": "Independent House in Saket",
                "price": 55000000,
                "location": "Saket",
                "city": "Delhi",
                "state": "Delhi",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 2800,
                "type": "Sale",
                "property_type": "Independent House",
                "description": "Spacious 4 BHK independent house with garden, terrace, and parking. Prime location in South Delhi.",
                "broker_name": "Rajesh Kumar",
                "broker_phone": "+91 98100 12345",
                "broker_email": "rajesh.k@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
                "available": True,
                "features": ["Garden", "Terrace", "Parking", "Security"]
            },
            {
                "id": 10,
                "title": "Luxury Apartment in T Nagar",
                "price": 32000,
                "location": "T Nagar",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 1200,
                "type": "Rent",
                "property_type": "Apartment",
                "description": "Modern 2 BHK apartment with premium finishes, central location, and all amenities.",
                "broker_name": "Priya Sharma",
                "broker_phone": "+91 98200 23456",
                "broker_email": "priya.s@dwelza.com",
                "image_url": "https://images.unsplash.com/photo-1560448204-603b3fc33ddc?w=800",
                "available": True,
                "features": ["AC", "Security", "Parking", "Gym"]
            }
        ]
        st.session_state.properties = sample_properties

# Initialize session state and data
init_session_state()
init_sample_data()

# Sidebar content
with st.sidebar:
    # Logo and title
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #1a73e8; font-size: 2.5rem;">🏠 Dwelza</h1>
        <p style="color: #666; font-size: 0.9rem;">India's Premier Real Estate Platform</p>
        <hr>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 📌 Navigate")
    page = st.radio(
        "",
        ["🏠 Home", "🔍 Properties", "📖 About", "📞 Contact"],
        key="navigation"
    )
    
    st.markdown("---")
    
    # User Authentication
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Account")
        auth_tab = st.selectbox("", ["Login", "Register"])
        
        if auth_tab == "Login":
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if username in st.session_state.users:
                        if st.session_state.users[username]["password"] == password:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.is_broker = st.session_state.users[username]["is_broker"]
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid password!")
                    else:
                        st.error("❌ User not found!")
        
        else:  # Register
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_password = st.text_input("Password", type="password", placeholder="Choose a password")
                new_email = st.text_input("Email", placeholder="Enter email")
                new_phone = st.text_input("Phone", placeholder="Enter phone number")
                is_broker = st.checkbox("Register as Broker")
                submit = st.form_submit_button("Register")
                
                if submit:
                    if new_username and new_password:
                        if new_username not in st.session_state.users:
                            st.session_state.users[new_username] = {
                                "password": new_password,
                                "email": new_email,
                                "phone": new_phone,
                                "is_broker": is_broker
                            }
                            st.success("✅ Registration successful! Please login.")
                            st.rerun()
                        else:
                            st.error("❌ Username already exists!")
                    else:
                        st.error("❌ Please fill all required fields!")
    
    else:
        st.success(f"👋 Welcome, {st.session_state.username}!")
        if st.session_state.is_broker:
            st.info("🔑 Broker Account")
        else:
            st.info("👤 User Account")
        
        if st.button("📊 Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_broker = False
            st.rerun()

# Main content area
if page == "🏠 Home":
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3rem;">🏠 Find Your Dream Home in India</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Discover the perfect property across India's top cities. Rent, buy, or lease with Dwelza.</p>
        <p style="font-size: 1rem; margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;">
                🏙️ 10+ Cities
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;">
                🏡 50+ Properties
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;">
                👤 10+ Brokers
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    st.markdown("### 📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">50+</div>
            <p>Properties</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">10+</div>
            <p>Trusted Brokers</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">10</div>
            <p>Cities Covered</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">500+</div>
            <p>Happy Clients</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Search section
    st.markdown("### 🔍 Find Your Perfect Property")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search by city or location", placeholder="e.g., Mumbai, Bangalore...")
    with col2:
        search_type = st.selectbox("Listing Type", ["All", "Sale", "Rent", "Lease"])
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Search", use_container_width=True):
            st.session_state.search_query = search_query
            st.session_state.search_type = search_type
            st.session_state.page = "properties"
            st.rerun()
    
    # Featured Properties
    st.markdown("### 🌟 Featured Properties")
    st.markdown("*Handpicked properties across India*")
    
    cols = st.columns(3)
    for idx, property in enumerate(st.session_state.properties[:6]):
        with cols[idx % 3]:
            # Determine badge color
            badge_class = "badge-sale" if property["type"] == "Sale" else "badge-rent" if property["type"] == "Rent" else "badge-lease"
            
            st.markdown(f"""
            <div class="property-card">
                <img src="{property['image_url']}" alt="{property['title']}">
                <h4 style="margin-top: 0.5rem; font-size: 1.1rem;">{property['title']}</h4>
                <p class="price-tag">₹{property['price']:,}</p>
                <p style="color: #666; font-size: 0.9rem;">📍 {property['location']}, {property['city']}</p>
                <p>🛏️ {property['bedrooms']} BHK | 🛁 {property['bathrooms']} Bath | 📐 {property['area']} sq ft</p>
                <span class="{badge_class}">{property['type']}</span>
                <div class="broker-info">
                    <small>👤 {property['broker_name']}</small><br>
                    <small>📞 {property['broker_phone']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"View Details", key=f"view_{property['id']}"):
                    st.session_state.selected_property = property['id']
                    st.session_state.page = "property_detail"
                    st.rerun()
            with col2:
                if property['id'] in st.session_state.favorites:
                    if st.button(f"❤️", key=f"fav_{property['id']}"):
                        st.session_state.favorites.remove(property['id'])
                        st.rerun()
                else:
                    if st.button(f"🤍", key=f"fav_{property['id']}"):
                        st.session_state.favorites.add(property['id'])
                        st.success("Added to favorites!")
                        st.rerun()

elif page == "🔍 Properties":
    st.markdown("### 🔍 Browse All Properties")
    
    # Filters
    st.markdown("#### 📋 Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_type = st.selectbox("Listing Type", ["All", "Sale", "Rent", "Lease"])
    with col2:
        cities = ["All"] + sorted(list(set(p["city"] for p in st.session_state.properties)))
        filter_city = st.selectbox("City", cities)
    with col3:
        price_ranges = ["All", "Under ₹50L", "₹50L - ₹1Cr", "₹1Cr - ₹5Cr", "Above ₹5Cr"]
        filter_price = st.selectbox("Price Range", price_ranges)
    with col4:
        bedrooms = ["All"] + sorted(list(set(p["bedrooms"] for p in st.session_state.properties)))
        filter_bedrooms = st.selectbox("Bedrooms", bedrooms)
    
    # Apply filters
    filtered_properties = st.session_state.properties
    
    if filter_type != "All":
        filtered_properties = [p for p in filtered_properties if p["type"] == filter_type]
    if filter_city != "All":
        filtered_properties = [p for p in filtered_properties if p["city"] == filter_city]
    if filter_price != "All":
        if filter_price == "Under ₹50L":
            filtered_properties = [p for p in filtered_properties if p["price"] < 5000000]
        elif filter_price == "₹50L - ₹1Cr":
            filtered_properties = [p for p in filtered_properties if 5000000 <= p["price"] < 10000000]
        elif filter_price == "₹1Cr - ₹5Cr":
            filtered_properties = [p for p in filtered_properties if 10000000 <= p["price"] < 50000000]
        elif filter_price == "Above ₹5Cr":
            filtered_properties = [p for p in filtered_properties if p["price"] >= 50000000]
    if filter_bedrooms != "All":
        filtered_properties = [p for p in filtered_properties if p["bedrooms"] == filter_bedrooms]
    
    st.markdown(f"**Found {len(filtered_properties)} properties**")
    
    # Display properties
    for property in filtered_properties:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(property["image_url"], use_container_width=True)
            with col2:
                st.markdown(f"### {property['title']}")
                st.markdown(f"💰 **₹{property['price']:,}**")
                st.markdown(f"📍 {property['location']}, {property['city']}")
                st.markdown(f"🛏️ {property['bedrooms']} BHK | 🛁 {property['bathrooms']} Bath | 📐 {property['area']} sq ft")
                st.markdown(f"🏷️ **{property['type']}** | 🏠 {property['property_type']}")
                
                with st.expander("📝 Description"):
                    st.write(property["description"])
                
                with st.expander("✨ Features"):
                    for feature in property["features"]:
                        st.markdown(f"- ✅ {feature}")
                
                st.markdown("""
                <div class="broker-info">
                    <strong>📞 Contact Broker</strong><br>
                    👤 {}<br>
                    📱 {}<br>
                    📧 {}
                </div>
                """.format(property["broker_name"], property["broker_phone"], property["broker_email"]), unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"📞 Call", key=f"call_{property['id']}"):
                        st.success(f"📱 Call {property['broker_name']} at {property['broker_phone']}")
                with col2:
                    if st.button(f"📧 Email", key=f"email_{property['id']}"):
                        st.success(f"📧 Email sent to {property['broker_email']}")
                with col3:
                    if st.session_state.logged_in:
                        if st.button(f"📅 Book Visit", key=f"book_{property['id']}"):
                            if st.session_state.username not in st.session_state.bookings:
                                st.session_state.bookings[st.session_state.username] = []
                            st.session_state.bookings[st.session_state.username].append({
                                "property": property["title"],
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "status": "Confirmed"
                            })
                            st.success("✅ Visit booked successfully!")
                            st.balloons()
                    else:
                        st.info("🔐 Login to book")
                with col4:
                    if property['id'] in st.session_state.favorites:
                        if st.button(f"❤️ Favorited", key=f"favlist_{property['id']}"):
                            st.session_state.favorites.remove(property['id'])
                            st.rerun()
                    else:
                        if st.button(f"🤍 Save", key=f"favlist_{property['id']}"):
                            st.session_state.favorites.add(property['id'])
                            st.success("Saved!")
                            st.rerun()
            st.markdown("---")

elif page == "📖 About":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem;">📖 About Dwelza</h1>
        <p style="font-size: 1.2rem;">India's premier real estate platform connecting buyers, sellers, and renters with trusted brokers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🎯 Our Mission
        To make property transactions transparent, efficient, and accessible to everyone in India.
        
        ### 🌟 What We Offer
        - **Verified Properties**: All listings are verified by our team
        - **Trusted Brokers**: Connect with licensed and verified brokers
        - **Real-time Data**: Updated property listings across India
        - **Secure Transactions**: Safe and secure payment options
        
        ### 📊 Our Impact
        - 50+ Properties Listed
        - 10+ Trusted Brokers
        - 10+ Cities Covered
        - 500+ Happy Clients
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Why Choose Dwelza?
        
        **1. Transparent Pricing**
        No hidden charges or fees
        
        **2. Verified Brokers**
        All brokers are verified and licensed
        
        **3. Pan-India Coverage**
        Properties across 10+ major cities
        
        **4. 24/7 Support**
        Dedicated customer support team
        
        **5. Easy Booking**
        Simple and secure booking process
        
        ### 🏢 Office
        **Dwelza Real Estate Pvt Ltd**
        Mumbai, Maharashtra, India
        📧 info@dwelza.com
        📱 +91 1800 123 4567
        """)

elif page == "📞 Contact":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem;">📞 Contact Us</h1>
        <p style="font-size: 1.2rem;">We're here to help you find your dream home</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### 📞 Get in Touch
        
        **📱 Phone**
        +91 1800 123 4567
        (Mon-Sat, 9 AM - 8 PM)
        
        **📧 Email**
        info@dwelza.com
        support@dwelza.com
        
        **📍 Address**
        Dwelza Real Estate Pvt Ltd
        Mumbai, Maharashtra
        India
        
        **🕐 Office Hours**
        Monday - Friday: 9:00 AM - 8:00 PM
        Saturday: 10:00 AM - 6:00 PM
        Sunday: Closed
        """)
    
    with col2:
        st.markdown("#### 📝 Send us a Message")
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            phone = st.text_input("Your Phone")
            subject = st.selectbox("Subject", ["Property Inquiry", "Broker Registration", "Support", "Other"])
            message = st.text_area("Message", height=150)
            submit = st.form_submit_button("Send Message")
            
            if submit:
                if name and email and message:
                    st.success("✅ Message sent successfully! We'll get back to you within 24 hours.")
                    st.balloons()
                else:
                    st.error("❌ Please fill all required fields!")

# Dashboard (hidden page)
if hasattr(st.session_state, 'page') and st.session_state.page == "dashboard":
    st.markdown("### 📊 Dashboard")
    
    if st.session_state.logged_in:
        user = st.session_state.users[st.session_state.username]
        
        if user["is_broker"]:
            st.markdown("#### 🏢 Broker Dashboard")
            st.info(f"Welcome {st.session_state.username}! You are registered as a broker.")
            
            with st.expander("➕ Add New Property"):
                with st.form("add_property_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        title = st.text_input("
