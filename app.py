import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Dwelza House Value Prediction",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Dwelza - House Value Prediction App")
st.markdown("AI Powered Real Estate Valuation Platform")

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    return pd.read_csv("hvp_dataset.csv")

df = load_data()

# ---------------- LOAD MODEL ----------------

try:
    model = pickle.load(open("model.pkl", "rb"))
except:
    st.error("model.pkl not found")
    st.stop()

# ---------------- SIDEBAR ----------------

st.sidebar.header("Property Details")

area = st.sidebar.number_input(
    "Area (Sq Ft)",
    min_value=200,
    max_value=10000,
    value=1200
)

bedrooms = st.sidebar.number_input(
    "Bedrooms",
    min_value=1,
    max_value=10,
    value=2
)

bathrooms = st.sidebar.number_input(
    "Bathrooms",
    min_value=1,
    max_value=10,
    value=2
)

# ---------------- PREDICTION ----------------

st.header("📈 House Price Prediction")

if st.button("Predict House Value"):

    try:
        prediction = model.predict(
            np.array([[area, bedrooms, bathrooms]])
        )

        st.success(
            f"Estimated House Value: ₹{prediction[0]:,.0f}"
        )

    except Exception as e:
        st.error(
            f"Prediction Error: {e}"
        )

# ---------------- DATASET PREVIEW ----------------

st.header("📋 Historical Housing Dataset")

st.dataframe(df.head())

# ---------------- MARKET ANALYTICS ----------------

st.header("📊 Market Analytics")

if "Price" in df.columns:

    fig = px.histogram(
        df,
        x="Price",
        title="Price Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------- PRICE STATS ----------------

st.header("📌 Market Summary")

if "Price" in df.columns:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Price",
        f"₹{df['Price'].mean():,.0f}"
    )

    col2.metric(
        "Maximum Price",
        f"₹{df['Price'].max():,.0f}"
    )

    col3.metric(
        "Minimum Price",
        f"₹{df['Price'].min():,.0f}"
    )

# ---------------- EMI CALCULATOR ----------------

st.header("🏦 EMI Calculator")

loan_amount = st.number_input(
    "Loan Amount",
    value=5000000
)

interest_rate = st.number_input(
    "Interest Rate (%)",
    value=8.5
)

loan_years = st.number_input(
    "Loan Tenure (Years)",
    value=20
)

if st.button("Calculate EMI"):

    r = interest_rate / 12 / 100
    n = loan_years * 12

    emi = (
        loan_amount
        * r
        * (1 + r) ** n
    ) / (
        (1 + r) ** n - 1
    )

    st.success(
        f"Monthly EMI: ₹{emi:,.0f}"
    )

# ---------------- PROPERTY RECOMMENDATION ----------------

st.header("💡 Budget Based Recommendation")

budget = st.number_input(
    "Enter Budget",
    value=5000000
)

if "Price" in df.columns:

    recommendations = df[
        df["Price"] <= budget
    ]

    st.write(
        f"Properties within ₹{budget:,.0f}"
    )

    st.dataframe(
        recommendations.head(10)
    )

# ---------------- FOOTER ----------------

st.markdown("---")
st.markdown(
    "Developed using Python, Streamlit, Machine Learning, Pandas, Plotly and Kaggle Housing Data."
)
