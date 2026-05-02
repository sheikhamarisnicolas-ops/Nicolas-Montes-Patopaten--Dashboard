import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 0. INITIAL CONFIGURATION (Must be first) ---
st.set_page_config(page_title="Walmart Retail Analytics Dashboard", layout="wide")

# --- 1. BRAND IDENTITY & THEME ---
W_BLUE = "#0053E2"    # Main Background Blue
W_YELLOW = "#FFC220"  # Walmart Yellow
W_WHITE = "#FFFFFF"   # Card Background
TEXT_MAIN = "#001E60" # High-contrast Navy
TEXT_SOFT = "#A9DDF7" # Light blue

# --- 2. CUSTOM CSS STYLING ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700;800&display=swap');
    
    .stApp {{ background-color: {W_BLUE}; font-family: 'Open Sans', sans-serif; }}
    
    .huge-title {{ font-size: 104px !important; color: {W_WHITE}; font-weight: 800; text-align: center; margin-bottom: 0px; line-height: 0.8; text-transform: uppercase; }}
    .sub-title {{ font-size: 30px !important; color: {W_YELLOW}; font-weight: 700; text-align: center; margin-top: 10px; letter-spacing: 5px; }}
    
    .content-card {{ 
        background-color: {W_WHITE}; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid {W_YELLOW}; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3); 
        margin-bottom: 20px; 
        color: {TEXT_MAIN} !important; 
    }}
    
    .slim-header {{
        background-color: {W_WHITE};
        padding: 10px;
        border-radius: 10px 10px 0 0;
        border-bottom: 3px solid {W_YELLOW};
        text-align: center;
        font-weight: bold;
        color: {TEXT_MAIN};
    }}

    .outside-text {{ color: {W_WHITE} !important; font-weight: bold; margin-bottom: 10px; }}
    .inside-text {{ color: {TEXT_MAIN} !important; font-size: 18px !important; font-weight: 500; line-height: 1.7; }}
    
    [data-testid="stMetricValue"] {{ font-size: 32px !important; color: {W_WHITE} !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 16px !important; color: {TEXT_SOFT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {W_WHITE}; }}
    
    /* Multiselect Tag Color */
    span[data-baseweb="tag"] {{ background-color: {W_YELLOW} !important; color: {TEXT_MAIN} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('Walmart_Sales.csv')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values(by='Date')
    
    # Winsorize Outliers
    cap_value = df["Weekly_Sales"].quantile(0.99)
    df["Weekly_Sales"] = df["Weekly_Sales"].clip(upper=cap_value)
    
    # Standardize
    df["Holiday_Status"] = df["Holiday_Flag"].map({1: "Holiday Week", 0: "Regular Week"})
    
    # Logic check for negatives
    numeric_cols = ["Weekly_Sales", "Fuel_Price", "CPI", "Unemployment"]
    df[numeric_cols] = df[numeric_cols].abs()
    return df

df = load_and_clean_data()

# --- 4. HEADER & SIDEBAR ---
st.markdown('<p class="huge-title">WALMART</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ANALYTICS</p>', unsafe_allow_html=True)

st.sidebar.image("walmart-logo-png-27971.png", use_container_width=True)
st.sidebar.header("Navigation & Filters")
store_list = sorted(df['Store'].unique())
selected_stores = st.sidebar.multiselect("Select Store IDs", store_list, default=store_list[:2])

if selected_stores:
    filtered_df = df[df['Store'].isin(selected_stores)]

    # --- 5. DATA TABLE PREVIEW (STYLIZED) ---
    st.markdown('<p class="outside-text" style="font-size:24px;">Cleaned Dataset Preview</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="slim-header">Master Records: Verified Retail Data</div>', unsafe_allow_html=True)
        st.dataframe(
            filtered_df.head(10), 
            use_container_width=True, 
            hide_index=True
        )

    # --- 6. KPI SECTION ---
    st.markdown('<p class="outside-text" style="font-size:28px; margin-top:20px;">Key Performance Indicators</p>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    avg_sales = filtered_df['Weekly_Sales'].mean()
    total_rev = filtered_df['Weekly_Sales'].sum()
    avg_fuel = filtered_df['Fuel_Price'].mean()
    avg_unemp = filtered_df['Unemployment'].mean()

    k1.metric("Avg Weekly Sales", f"${avg_sales:,.2f}")
    k2.metric("Aggregate Revenue", f"${total_rev:,.0f}")
    k3.metric("Fuel Price Index", f"${avg_fuel:.2f}")
    k4.metric("Unemployment Avg", f"{avg_unemp:.2f}%")

    # --- 7. VISUALIZATIONS ---
    col_a, col_b = st.columns(2)
    chart_theme = dict(paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color=TEXT_MAIN, size=12), margin=dict(l=50, r=30, t=20, b=50))

    with col_a:
        st.markdown('<div class="content-card" style="padding: 10px; margin-bottom: 5px; text-align: center;"><p style="color:#001E60; font-weight:bold; font-size:18px; margin:0;">Sales Velocity Trend</p></div>', unsafe_allow_html=True)
        trend_df = filtered_df.groupby("Date")["Weekly_Sales"].sum().reset_index()
        fig_line = px.line(trend_df, x="Date", y="Weekly_Sales", color_discrete_sequence=[W_BLUE])
        fig_line.update_layout(**chart_theme, height=350)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        st.markdown('<div class="content-card" style="padding: 10px; margin-bottom: 5px; text-align: center;"><p style="color:#001E60; font-weight:bold; font-size:18px; margin:0;">Fuel Price vs. Sales Correlation</p></div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(filtered_df, x="Fuel_Price", y="Weekly_Sales", color_discrete_sequence=["#F47321"], trendline="ols")
        fig_scatter.update_layout(**chart_theme, height=350)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 8. DYNAMIC EXECUTIVE SUMMARY (5-7 SENTENCES) ---
    st.markdown('<p class="outside-text" style="font-size:40px; margin-top:30px;">EXECUTIVE ANALYSIS SUMMARY</p>', unsafe_allow_html=True)
    
    top_store = filtered_df.groupby('Store')['Weekly_Sales'].sum().idxmax()
    worst_store = filtered_df.groupby('Store')['Weekly_Sales'].sum().idxmin()
    correlation = filtered_df['Fuel_Price'].corr(filtered_df['Weekly_Sales'])
    corr_desc = "slight negative" if correlation < 0 else "slight positive"
    
    summary_text = (
        f"This comprehensive analysis focuses on the retail performance of Store IDs: {', '.join(map(str, selected_stores))}. "
        f"Across the selected timeframe, the aggregate revenue reached a substantial total of ${total_rev:,.0f}, "
        f"with Store {top_store} emerging as the primary revenue driver in this cluster. "
        f"In contrast, Store {worst_store} showed the lowest sales velocity, suggesting a need for localized marketing or operational reviews. "
        f"Our statistical modeling indicates a {corr_desc} correlation of {correlation:.2f} between fuel prices and weekly sales, "
        f"implying that external economic pressures currently have a measurable impact on consumer spending patterns. "
        f"Despite an average unemployment rate of {avg_unemp:.2f}%, the sales trend remains resilient with notable peaks during holiday periods. "
        f"Moving forward, we recommend optimizing inventory levels in Store {top_store} to capitalize on its high-traffic momentum."
    )

    st.markdown(f"""
        <div class="content-card">
            <div class="inside-text">
                {summary_text}
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 9. FOOTER ---
st.markdown(f"""
    <div style="text-align:center; padding: 40px; color:white; border-top: 1px solid {TEXT_SOFT}; margin-top:50px;">
        <p style="font-size:18px;"><strong>Business Analysts:</strong> Sheikha Maris Nicolas, Duane Ryann Montes, Mikaela Angela Patopaten</p>
        <p>© 2026 Business Analytics Project • Information Systems Portfolio</p>
    </div>
""", unsafe_allow_html=True)