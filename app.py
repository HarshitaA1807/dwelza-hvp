
# app.py - Complete single file for Dwelza Real Estate Platform

import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import json
from werkzeug.security import generate_password_hash, check_password_hash
import random

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'dwelza_secret_key_2026'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dwelza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    is_broker = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50))  # House, Apartment, Villa, etc.
    listing_type = db.Column(db.String(50))  # Rent, Sale, Lease
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area_sqft = db.Column(db.Float)
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    description = db.Column(db.Text)
    broker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    broker_name = db.Column(db.String(100))
    broker_phone = db.Column(db.String(20))
    broker_email = db.Column(db.String(120))
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_type = db.Column(db.String(50))  # Visit, Rent, Buy
    booking_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Generate sample data (realistic Indian real estate data)
def generate_sample_properties():
    if Property.query.count() == 0:
        # Indian cities with realistic data
        cities = {
            'Mumbai': ['Andheri', 'Bandra', 'Colaba', 'Powai', 'Worli'],
            'Delhi': ['Connaught Place', 'Lajpat Nagar', 'Saket', 'Dwarka', 'Rohini'],
            'Bangalore': ['Koramangala', 'Indiranagar', 'Whitefield', 'Jayanagar', 'MG Road'],
            'Chennai': ['T Nagar', 'Adyar', 'Mylapore', 'Velachery', 'Ann Arbor'],
            'Hyderabad': ['Banjara Hills', 'Jubilee Hills', 'Gachibowli', 'Hitec City', 'Kukatpally'],
            'Pune': ['Koregaon Park', 'Kothrud', 'Wakad', 'Hinjewadi', 'Viman Nagar']
        }
        
        property_types = ['Apartment', 'Villa', 'Independent House', 'Studio', 'Penthouse']
        listing_types = ['Rent', 'Sale', 'Lease']
        
        # Sample brokers (realistic Indian names and numbers)
        brokers = [
            {'name': 'Rajesh Kumar', 'phone': '+91 98100 12345', 'email': 'rajesh.k@dwelza.com'},
            {'name': 'Priya Sharma', 'phone': '+91 98200 23456', 'email': 'priya.s@dwelza.com'},
            {'name': 'Amit Patel', 'phone': '+91 98300 34567', 'email': 'amit.p@dwelza.com'},
            {'name': 'Sneha Reddy', 'phone': '+91 98400 45678', 'email': 'sneha.r@dwelza.com'},
            {'name': 'Vikram Singh', 'phone': '+91 98500 56789', 'email': 'vikram.s@dwelza.com'},
            {'name': 'Anjali Mehta', 'phone': '+91 98600 67890', 'email': 'anjali.m@dwelza.com'},
            {'name': 'Suresh Iyer', 'phone': '+91 98700 78901', 'email': 'suresh.i@dwelza.com'},
            {'name': 'Deepa Nair', 'phone': '+91 98800 89012', 'email': 'deepa.n@dwelza.com'},
        ]
        
        for city, areas in cities.items():
            for area in areas:
                for _ in range(3):  # 3 properties per area
                    broker = random.choice(brokers)
                    prop_type = random.choice(property_types)
                    listing = random.choice(listing_types)
                    
                    # Generate realistic price based on city and type
                    base_price = random.randint(3000, 20000)
                    if city == 'Mumbai':
                        base_price *= 2
                    elif city in ['Delhi', 'Bangalore']:
                        base_price *= 1.5
                    
                    if listing == 'Rent':
                        price = base_price * random.randint(5, 20)
                    else:
                        price = base_price * random.randint(100, 300)
                    
                    property = Property(
                        title=f"{random.choice(['Luxury', 'Premium', 'Spacious', 'Elegant', 'Modern'])} {prop_type} in {area}",
                        property_type=prop_type,
                        listing_type=listing,
                        price=round(price, 0),
                        bedrooms=random.randint(1, 5),
                        bathrooms=random.randint(1, 4),
                        area_sqft=round(random.randint(500, 4000) / 100) * 100,
                        location=area,
                        city=city,
                        state=city + " State",
                        description=f"Beautiful {prop_type.lower()} located in prime location of {area}. "
                                   f"Features {random.randint(1, 5)} bedrooms, {random.randint(1, 4)} bathrooms, "
                                   f"and modern amenities. Close to schools, hospitals, and shopping centers.",
                        broker_id=1,  # Default user
                        broker_name=broker['name'],
                        broker_phone=broker['phone'],
                        broker_email=broker['email'],
                        image_url=f"https://source.unsplash.com/800x600/?house,{city},{area}",
                        is_available=True
                    )
                    db.session.add(property)
        
        db.session.commit()

# Generate sample users
def generate_sample_users():
    if User.query.count() == 0:
        # Create broker users
        brokers = [
            {'username': 'rajesh_k', 'email': 'rajesh.k@dwelza.com', 'phone': '+91 98100 12345'},
            {'username': 'priya_s', 'email': 'priya.s@dwelza.com', 'phone': '+91 98200 23456'},
            {'username': 'amit_p', 'email': 'amit.p@dwelza.com', 'phone': '+91 98300 34567'},
        ]
        
        for broker in brokers:
            user = User(
                username=broker['username'],
                email=broker['email'],
                phone=broker['phone'],
                is_broker=True
            )
            user.set_password('broker123')
            db.session.add(user)
        
        # Create regular user
        user = User(
            username='dwelza_user',
            email='user@dwelza.com',
            phone='+91 90000 00000',
            is_broker=False
        )
        user.set_password('user123')
        db.session.add(user)
        
        db.session.commit()

# Generate sample data
with app.app_context():
    generate_sample_users()
    generate_sample_properties()

# Routes
@app.route('/')
def home():
    # Get featured properties
    featured = Property.query.filter_by(is_available=True).limit(6).all()
    return render_template('index.html', featured=featured)

@app.route('/properties')
def properties():
    # Filter properties
    listing_type = request.args.get('type', 'all')
    city = request.args.get('city', 'all')
    min_price = request.args.get('min_price', '0')
    max_price = request.args.get('max_price', '10000000')
    
    query = Property.query.filter_by(is_available=True)
    
    if listing_type != 'all':
        query = query.filter_by(listing_type=listing_type)
    if city != 'all':
        query = query.filter_by(city=city)
    if min_price:
        query = query.filter(Property.price >= float(min_price))
    if max_price:
        query = query.filter(Property.price <= float(max_price))
    
    properties = query.all()
    
    # Get unique cities for filter
    cities = db.session.query(Property.city).distinct().all()
    cities = [c[0] for c in cities]
    
    return render_template('properties.html', properties=properties, cities=cities)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('property_detail.html', property=property)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_broker'] = user.is_broker
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        is_broker = request.form.get('is_broker') == 'on'
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            is_broker=is_broker
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if user.is_broker:
        properties = Property.query.filter_by(broker_id=user.id).all()
        return render_template('broker_dashboard.html', user=user, properties=properties)
    else:
        bookings = Booking.query.filter_by(user_id=user.id).all()
        return render_template('user_dashboard.html', user=user, bookings=bookings)

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session or not session.get('is_broker'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        property = Property(
            title=request.form.get('title'),
            property_type=request.form.get('property_type'),
            listing_type=request.form.get('listing_type'),
            price=float(request.form.get('price')),
            bedrooms=int(request.form.get('bedrooms')),
            bathrooms=int(request.form.get('bathrooms')),
            area_sqft=float(request.form.get('area_sqft')),
            location=request.form.get('location'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            description=request.form.get('description'),
            broker_id=session['user_id'],
            broker_name=User.query.get(session['user_id']).username,
            broker_phone=User.query.get(session['user_id']).phone,
            broker_email=User.query.get(session['user_id']).email,
            is_available=True
        )
        db.session.add(property)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('add_property.html')

@app.route('/book_property/<int:property_id>', methods=['POST'])
def book_property(property_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    booking = Booking(
        property_id=property_id,
        user_id=session['user_id'],
        booking_type=request.form.get('booking_type'),
        booking_date=datetime.now()
    )
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Booking confirmed!'})

@app.route('/api/properties')
def api_properties():
    properties = Property.query.filter_by(is_available=True).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'price': p.price,
        'city': p.city,
        'listing_type': p.listing_type,
        'broker_name': p.broker_name,
        'broker_phone': p.broker_phone
    } for p in properties])

# Create templates directory and template files
def create_templates():
    os.makedirs('templates', exist_ok=True)
    
    # Base template
    with open('templates/base.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dwelza - India's Premier Real Estate Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #1a73e8;
            --secondary-color: #34a853;
            --accent-color: #ea4335;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
        }
        
        .navbar-dwelza {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .navbar-dwelza .navbar-brand {
            font-weight: 700;
            font-size: 1.8rem;
            color: white !important;
        }
        
        .navbar-dwelza .nav-link {
            color: rgba(255,255,255,0.9) !important;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .navbar-dwelza .nav-link:hover {
            color: white !important;
            transform: translateY(-2px);
        }
        
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
            margin-bottom: 50px;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        
        .property-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s;
            height: 100%;
        }
        
        .property-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .property-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        
        .property-card .card-body {
            padding: 20px;
        }
        
        .property-card .price {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .property-card .location {
            color: #666;
            font-size: 0.95rem;
        }
        
        .property-card .broker-info {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        .btn-dwelza {
            background: var(--primary-color);
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            border: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .btn-dwelza:hover {
            background: #0d47a1;
            transform: scale(1.05);
            color: white;
        }
        
        .btn-dwelza-outline {
            border: 2px solid var(--primary-color);
            color: var(--primary-color);
            background: transparent;
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .btn-dwelza-outline:hover {
            background: var(--primary-color);
            color: white;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            padding: 50px 0 20px 0;
            margin-top: 50px;
        }
        
        .footer a {
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .footer a:hover {
            color: white;
        }
        
        .filter-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        
        .badge-dwelza {
            background: var(--primary-color);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dwelza">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">
                <i class="fas fa-home"></i> Dwelza
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('properties') }}">
                            <i class="fas fa-search"></i> Properties
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('about') }}">
                            <i class="fas fa-info-circle"></i> About
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('contact') }}">
                            <i class="fas fa-phone"></i> Contact
                        </a>
                    </li>
                    {% if session.user_id %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">
                                <i class="fas fa-user"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">
                                <i class="fas fa-sign-in-alt"></i> Login
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('register') }}">
                                <i class="fas fa-user-plus"></i> Register
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% block content %}{% endblock %}

    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h4><i class="fas fa-home"></i> Dwelza</h4>
                    <p>India's premier real estate platform for buying, selling, and renting properties.</p>
                    <div class="mt-3">
                        <a href="#" class="me-2"><i class="fab fa-facebook fa-2x"></i></a>
                        <a href="#" class="me-2"><i class="fab fa-twitter fa-2x"></i></a>
                        <a href="#" class="me-2"><i class="fab fa-instagram fa-2x"></i></a>
                        <a href="#"><i class="fab fa-linkedin fa-2x"></i></a>
                    </div>
                </div>
                <div class="col-md-4">
                    <h5>Quick Links</h5>
                    <ul class="list-unstyled">
                        <li><a href="{{ url_for('properties') }}">Browse Properties</a></li>
                        <li><a href="{{ url_for('about') }}">About Us</a></li>
                        <li><a href="{{ url_for('contact') }}">Contact Us</a></li>
                        <li><a href="#">Privacy Policy</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Contact Info</h5>
                    <p><i class="fas fa-phone"></i> +91 1800 123 4567</p>
                    <p><i class="fas fa-envelope"></i> info@dwelza.com</p>
                    <p><i class="fas fa-map-marker-alt"></i> Mumbai, India</p>
                </div>
            </div>
            <hr class="bg-light">
            <div class="text-center">
                <p>&copy; 2026 Dwelza. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
        ''')

    # Index page
    with open('templates/index.html', 'w') as f:
        f.write('''
{% extends "base.html" %}

{% block content %}
<div class="hero-section">
    <div class="container text-center">
        <h1 class="hero-title">Find Your Dream Home in India</h1>
        <p class="hero-subtitle">Discover the perfect property across India's top cities. Rent, buy, or lease with Dwelza.</p>
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="input-group input-group-lg">
                    <input type="text" class="form-control" placeholder="Search by city, location, or property type...">
                    <button class="btn btn-light"><i class="fas fa-search"></i> Search</button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="container">
    <div class="row mb-4">
        <div class="col-12">
            <h2 class="text-center">Featured Properties</h2>
            <p class="text-center text-muted">Handpicked properties across India</p>
        </div>
    </div>
    <div class="row">
        {% for property in featured %}
        <div class="col-md-4 mb-4">
            <div class="property-card">
                <img src="{{ property.image_url or 'https://via.placeholder.com/800x600' }}" alt="{{ property.title }}">
                <div class="card-body">
                    <h5 class="card-title">{{ property.title }}</h5>
                    <p class="price">₹{{ "{:,.0f}".format(property.price) }}/-</p>
                    <p class="location"><i class="fas fa-map-marker-alt"></i> {{ property.location }}, {{ property.city }}</p>
                    <div class="d-flex justify-content-between mb-2">
                        <span><i class="fas fa-bed"></i> {{ property.bedrooms }} BHK</span>
                        <span><i class="fas fa-bath"></i> {{ property.bathrooms }} Bath</span>
                        <span><i class="fas fa-vector-square"></i> {{ property.area_sqft }} sq ft</span>
                    </div>
                    <span class="badge badge-dwelza mb-2">{{ property.listing_type }}</span>
                    <div class="broker-info">
                        <small><i class="fas fa-user"></i> {{ property.broker_name }}</small>
                        <small class="float-end"><i class="fas fa-phone"></i> {{ property.broker_phone }}</small>
                    </div>
                    <a href="{{ url_for('property_detail', property_id=property.id) }}" class="btn btn-dwelza w-100 mt-2">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="row mt-5">
        <div class="col-12 text-center">
            <a href="{{ url_for('properties') }}" class="btn btn-dwelza-outline btn-lg">View All Properties</a>
        </div>
    </div>
</div>

<!-- Quick Stats -->
<div class="container mt-5">
    <div class="row text-center">
        <div class="col-md-3">
            <div class="stat-box">
                <h3>500+</h3>
                <p>Properties Listed</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h3>50+</h3>
                <p>Trusted Brokers</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h3>20+</h3>
                <p>Cities Covered</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h3>1000+</h3>
                <p>Happy Clients</p>
            </div>
        </div>
    </div>
</div>

<style>
.stat-box {
    background: white;
    padding: 30px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.3s;
}
.stat-box:hover {
    transform: scale(1.05);
}
.stat-box h3 {
    color: var(--primary-color);
    font-weight: 700;
    font-size: 2.5rem;
}
.stat-box p {
    color: #666;
    margin-bottom: 0;
}
</style>
{% endblock %}
        ''')

    # Properties page
    with open('templates/properties.html', 'w') as f:
        f.write('''
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h1 class="text-center mb-4">Browse Properties</h1>
    
    <div class="filter-section">
        <form method="GET" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Listing Type</label>
                <select name="type" class="form-select">
                    <option value="all">All Types</option>
                    <option value="Rent">Rent</option>
                    <option value="Sale">Sale</option>
                    <option value="Lease">Lease</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">City</label>
                <select name="city" class="form-select">
                    <option value="all">All Cities</option>
                    {% for city in cities %}
                    <option value="{{ city }}">{{ city }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Min Price</label>
                <input type="number" name="min_price" class="form-control" placeholder="Min">
            </div>
            <div class="col-md-2">
                <label class="form-label">Max Price</label>
                <input type="number" name="max_price" class="form-control" placeholder="Max">
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button type="submit" class="btn btn-dwelza w-100">Apply Filters</button>
            </div>
        </form>
    </div>
    
    <div class="row">
        {% for property in properties %}
        <div class="col-md-4 mb-4">
            <div class="property-card">
                <img src="{{ property.image_url or 'https://via.placeholder.com/800x600' }}" alt="{{ property.title }}">
                <div class="card-body">
                    <h5 class="card-title">{{ property.title }}</h5>
                    <p class="price">₹{{ "{:,.0f}".format(property.price) }}/-</p>
                    <p class="location"><i class="fas fa-map-marker-alt"></i> {{ property.location }}, {{ property.city }}</p>
                    <div class="d-flex justify-content-between mb-2">
                        <span><i class="fas fa-bed"></i> {{ property.bedrooms }} BHK</span>
                        <span><i class="fas fa-bath"></i> {{ property.bathrooms }} Bath</span>
                        <span><i class="fas fa-vector-square"></i> {{ property.area_sqft }} sq ft</span>
                    </div>
                    <span class="badge badge-dwelza mb-2">{{ property.listing_type }}</span>
                    <div class="broker-info">
                        <small><i class="fas fa-user"></i> {{ property.broker_name }}</small>
                        <small class="float-end"><i class="fas fa-phone"></i> {{ property.broker_phone }}</small>
                    </div>
                    <a href="{{ url_for('property_detail', property_id=property.id) }}" class="btn btn-dwelza w-100 mt-2">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
        ''')

    # Property detail page
    with open('templates/property_detail.html', 'w') as f:
        f.write('''
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <img src="{{ property.image_url or 'https://via.placeholder.com/800x600' }}" class="img-fluid rounded" alt="{{ property.title }}">
            <h2 class="mt-3">{{ property.title }}</h2>
            <p><i class="fas fa-map-marker-alt"></i> {{ property.location }}, {{ property.city }}, {{ property.state }}</p>
            
            <div class="row mt-4">
                <div class="col-md-3">
                    <div class="border rounded p-3 text-center">
                        <h5>₹{{ "{:,.0f}".format(property.price) }}</h5>
                        <small>Price</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="border rounded p-3 text-center">
                        <h5>{{ property.bedrooms }} BHK</h5>
                        <small>Bedrooms</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="border rounded p-3 text-center">
                        <h5>{{ property.bathrooms }}</h5>
                        <small>Bathrooms</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="border rounded p-3 text-center">
                        <h5>{{ property.area_sqft }} sq ft</h5>
                        <small>Area</small>
                    </div>
                </div>
            </div>
            
            <h4 class="mt-4">Description</h4>
            <p>{{ property.description }}</p>
            
            <h4 class="mt-4">Property Details</h4>
            <ul class="list-group">
                <li class="list-group-item"><strong>Property Type:</strong> {{ property.property_type }}</li>
                <li class="list-group-item"><strong>Listing Type:</strong> {{ property.listing_type }}</li>
                <li class="list-group-item"><strong>Location:</strong> {{ property.location }}</li>
                <li class="list-group-item"><strong>City:</strong> {{ property.city }}</li>
                <li class="list-group-item"><strong>State:</strong> {{ property.state }}</li>
            </ul>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Contact Broker</h5>
                    <div class="broker-info mb-3">
                        <p><strong><i class="fas fa-user"></i> {{ property.broker_name }}</strong></p>
                        <p><i class="fas fa-phone"></i> {{ property.broker_phone }}</p>
                        <p><i class="fas fa-envelope"></i> {{ property.broker_email }}</p>
                    </div>
                    
                    <form action="{{ url_for('book_property', property_id=property.id) }}" method="POST">
                        <div class="mb-3">
                            <label class="form-label">Interested in</label>
                            <select name="booking_type" class="form-select" required>
                                <option value="Visit">Visit</option>
                                <option value="Rent">Rent</option>
                                <option value="Buy">Buy</option>
                            </select
