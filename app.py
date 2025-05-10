import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shopify Campaign Analyzer", layout="wide")
st.title("📊 Shopify Campaign Analyzer")

uploaded_file = st.file_uploader("Upload your Shopify Sessions CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean and normalize column names
    df.columns = df.columns.str.strip()

    # Rename columns
    df = df.rename(columns={
        'UTM campaign': 'utm_campaign',
        'Sessions': 'sessions',
        'Sessions that completed checkout': 'conversions',
        'Sessions with cart additions': 'add_to_cart',
        'Sessions that reached checkout': 'reached_checkout',
        'Average session duration': 'time_on_site'
    })

    # Drop rows where UTM campaign is missing
    df = df.dropna(subset=['utm_campaign'])
    df['utm_campaign'] = df['utm_campaign'].astype(str).str.strip()

    # Group and aggregate
    grouped = df.groupby('utm_campaign').agg({
        'sessions': 'sum',
        'conversions': 'sum',
        'add_to_cart': 'sum',
        'reached_checkout': 'sum',
        'time_on_site': 'mean'  # Average across grouped sessions
    }).reset_index()

    # Calculate conversion rates
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['sessions']) * 100
    grouped['add_to_cart_rate'] = (grouped['add_to_cart'] / grouped['sessions']) * 100
    grouped['reached_checkout_rate'] = (grouped['reached_checkout'] / grouped['sessions']) * 100

    # Round all rates and time_on_site
    grouped[['conversion_rate', 'add_to_cart_rate', 'reached_checkout_rate', 'time_on_site']] = (
        grouped[['conversion_rate', 'add_to_cart_rate', 'reached_checkout_rate', 'time_on_site']].round(2)
    )

    # Show full performance table
    st.subheader("📊 Campaign Performance Summary")
    st.dataframe(grouped.sort_values(by='conversion_rate', ascending=False), use_container_width=True)

    # Optional: Top 10 by each metric
    metric_labels = {
        'conversions': 'Conversions',
        'add_to_cart': 'Add to Carts',
        'reached_checkout': 'Reached Checkout',
        'conversion_rate': 'Conversion Rate (%)',
        'add_to_cart_rate': 'Add to Cart Rate (%)',
        'reached_checkout_rate': 'Reached Checkout Rate (%)',
        'time_on_site': 'Avg. Session Duration (s)'
    }

    for metric, label in metric_labels.items():
        top_10 = grouped[['utm_campaign', metric]].sort_values(by=metric, ascending=False).head(10)
        st.markdown(f"### 🔝 Top 10 Campaigns by {label}")
        st.dataframe(top_10, use_container_width=True)
