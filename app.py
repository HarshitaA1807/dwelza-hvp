
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
import sys

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'dwelza_secret_key_2026'

# Database configuration - using SQLite (works on Streamlit Cloud)
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
    property_type = db.Column(db.String(50))
    listing_type = db.Column(db.String(50))
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
    booking_type = db.Column(db.String(50))
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
                for _ in range(3):
                    broker = random.choice(brokers)
                    prop_type = random.choice(property_types)
                    listing = random.choice(listing_types)
                    
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
                        broker_id=1,
                        broker_name=broker['name'],
                        broker_phone=broker['phone'],
                        broker_email=broker['email'],
                        image_url=f"https://source.unsplash.com/800x600/?house,{city},{area}",
                        is_available=True
                    )
                    db.session.add(property)
        
        db.session.commit()

def generate_sample_users():
    if User.query.count() == 0:
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
        
        user = User(
            username='dwelza_user',
            email='user@dwelza.com',
            phone='+91 90000 00000',
            is_broker=False
        )
        user.set_password('user123')
        db.session.add(user)
        
        db.session.commit()

# Initialize data
with app.app_context():
    generate_sample_users()
    generate_sample_properties()

# Routes
@app.route('/')
def home():
    featured = Property.query.filter_by(is_available=True).limit(6).all()
    return render_template('index.html', featured=featured)

@app.route('/properties')
def properties():
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

# For Streamlit Cloud compatibility
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
