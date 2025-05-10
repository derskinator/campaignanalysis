import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shopify Campaign Analyzer", layout="wide")
st.title("📊 Shopify Campaign Analyzer")

uploaded_file = st.file_uploader("Upload your Shopify Sessions CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean and normalize column names
    df.columns = df.columns.str.strip()

    # Rename columns for easier reference
    df = df.rename(columns={
        'UTM campaign': 'utm_campaign',
        'Sessions': 'sessions',
        'Sessions that completed checkout': 'conversions',
        'Sessions with cart additions': 'add_to_cart',
        'Sessions that reached checkout': 'reached_checkout',
        'Average session duration': 'time_on_site'
    })

    # Drop rows without UTM campaign
    df = df.dropna(subset=['utm_campaign'])
    df['utm_campaign'] = df['utm_campaign'].astype(str).str.strip()

    # Aggregate by campaign
    grouped = df.groupby('utm_campaign').agg({
        'sessions': 'sum',
        'conversions': 'sum',
        'add_to_cart': 'sum',
        'reached_checkout': 'sum',
        'time_on_site': 'mean'  # average time per session
    }).reset_index()

    # Calculate accurate performance rates
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['sessions']) * 100
    grouped['add_to_cart_rate'] = (grouped['add_to_cart'] / grouped['sessions']) * 100
    grouped['reached_checkout_rate'] = (grouped['reached_checkout'] / grouped['sessions']) * 100

    # Round for display
    grouped[['conversion_rate', 'add_to_cart_rate', 'reached_checkout_rate', 'time_on_site']] = (
        grouped[['conversion_rate', 'add_to_cart_rate', 'reached_checkout_rate', 'time_on_site']].round(2)
    )

    # Optional: Filter campaigns with very low session counts (adjust threshold if needed)
    grouped_filtered = grouped[grouped['sessions'] >= 50]

    st.subheader("📊 Campaign Performance Summary (Min 50 Sessions)")
    st.dataframe(grouped_filtered.sort_values(by='conversion_rate', ascending=False), use_container_width=True)

    # Leaderboards
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
        top_10 = grouped_filtered[['utm_campaign', 'sessions', metric]].sort_values(by=metric, ascending=False).head(10)
        st.markdown(f"### 🔝 Top 10 Campaigns by {label}")
        st.dataframe(top_10, use_container_width=True)
