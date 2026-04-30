import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load and Clean Data
df = pd.read_csv('Walmart_Sales.csv')
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df = df.sort_values(by='Date')

# Winsorize Outliers at 99th percentile
cap_value = df["Weekly_Sales"].quantile(0.99)
df["Weekly_Sales"] = df["Weekly_Sales"].clip(upper=cap_value)

# Standardize Holiday Flag
df["Holiday_Status"] = df["Holiday_Flag"].map({1: "Holiday Week", 0: "Regular Week"})

# Logic check for negative values
numeric_cols = ["Weekly_Sales", "Fuel_Price", "CPI", "Unemployment"]
df[numeric_cols] = df[numeric_cols].abs()

st.write(df.head())

# --- 1. BRAND IDENTITY & THEME ---
W_BLUE = "#0053E2"    # Main Background Blue
W_YELLOW = "#FFC220"  # Walmart Yellow
W_WHITE = "#FFFFFF"   # Card Background
TEXT_MAIN = "#001E60" # High-contrast Navy
TEXT_SOFT = "#A9DDF7" # Light blue

# --- 2. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Walmart Retail Analytics Dashboard", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700;800&display=swap');
    .stApp {{ background-color: {W_BLUE}; font-family: 'Open Sans', sans-serif; }}
    .huge-title {{ font-size: 104px !important; color: {W_WHITE}; font-weight: 800; text-align: center; margin-bottom: 0px; line-height: 0.8; text-transform: uppercase; }}
    .sub-title {{ font-size: 30px !important; color: {W_YELLOW}; font-weight: 700; text-align: center; margin-top: 10px; letter-spacing: 5px; }}
    .content-card {{ background-color: {W_WHITE}; padding: 25px; border-radius: 15px; border: 2px solid {W_YELLOW}; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px; color: #001E60 !important; }}
    .outside-text {{ color: {W_WHITE} !important; font-weight: bold; margin-bottom: 10px; }}
    .inside-text {{ color: {TEXT_MAIN} !important; font-size: 22px !important; font-weight: 500; line-height: 1.6; }}
    [data-testid="stMetricValue"] {{ font-size: 32px !important; color: {W_WHITE} !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 16px !important; color: {TEXT_SOFT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {W_WHITE}; }}
    span[data-baseweb="tag"] {{ background-color: #FFC220 !important; color: #001E60 !important; border-radius: 5px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & FILTERS ---
st.markdown('<p class="huge-title">WALMART</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ANALYTICS</p>', unsafe_allow_html=True)

st.sidebar.image("walmart-logo-png-27971.png", use_container_width=True)
st.sidebar.header("Filter Data")
store_list = sorted(df['Store'].unique())
selected_stores = st.sidebar.multiselect("Select Store IDs", store_list, default=store_list[:2])

if selected_stores:
    filtered_df = df[df['Store'].isin(selected_stores)]

    # --- 4. KPI SECTION ---
    st.markdown('<p class="outside-text" style="font-size:28px;">Key Performance Indicators</p>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Avg Weekly Sales", f"${filtered_df['Weekly_Sales'].mean():,.2f}")
    k2.metric("Aggregate Revenue", f"${filtered_df['Weekly_Sales'].sum():,.0f}")
    k3.metric("Fuel Price Index", f"${filtered_df['Fuel_Price'].mean():.2f}")
    k4.metric("Unemployment Avg", f"{filtered_df['Unemployment'].mean():.2f}%")

    # --- 5. VISUALIZATIONS ---
    col_a, col_b = st.columns(2)
    chart_theme = dict(paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#001E60", size=12), margin=dict(l=50, r=30, t=20, b=50))

    with col_a:
        st.markdown('<div class="content-card" style="padding: 10px; margin-bottom: 5px; text-align: center;"><p style="color:#001E60; font-weight:bold; font-size:18px; margin:0;">Sales Velocity Trend</p></div>', unsafe_allow_html=True)
        trend_df = filtered_df.groupby("Date")["Weekly_Sales"].sum().reset_index()
        fig_line = px.line(trend_df, x="Date", y="Weekly_Sales", color_discrete_sequence=[W_BLUE])
        fig_line.update_layout(**chart_theme, height=350)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        st.markdown('<div class="content-card" style="padding: 10px; margin-bottom: 5px; text-align: center;"><p style="color:#001E60; font-weight:bold; font-size:18px; margin:0;">Fuel Price vs. Sales</p></div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(filtered_df, x="Fuel_Price", y="Weekly_Sales", color_discrete_sequence=["#F47321"])
        fig_scatter.update_layout(**chart_theme, height=350)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 6. SUMMARY & FOOTER ---
    st.markdown('<p class="outside-text" style="font-size:40px; margin-top:30px;">EXECUTIVE ANALYSIS SUMMARY</p>', unsafe_allow_html=True)
    top_store = filtered_df.groupby('Store')['Weekly_Sales'].sum().idxmax()
    st.markdown(f'<div class="content-card"><div class="inside-text">Evaluating <strong>Store(s): {", ".join(map(str, selected_stores))}</strong>. <strong>Store {top_store}</strong> leads in revenue generation.</div></div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; padding: 40px; color:white; border-top: 1px solid {TEXT_SOFT}; margin-top:50px;"><p style="font-size:18px;"><strong>Business Analysts:</strong> Sheikha Maris Nicolas, Duane Ryann Montes, Mikaela Angela Patopaten</p><p>© 2026 Business Analytics Project</p></div>', unsafe_allow_html=True)

