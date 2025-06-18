import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk

# Load data
df = pd.read_excel("src/code/synthetic_login_metadata.xlsx")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['login_hour'] = df['timestamp'].dt.hour

# Sidebar user selector
st.sidebar.title("🛡️ Fraud Profile Dashboard")
user_id = st.sidebar.selectbox("Select a User", df['user_id'].unique())

user_df = df[df['user_id'] == user_id]

st.title(f"Fraud Profile for: {user_id}")

# Summary Panel
st.subheader("📌 User Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Logins", len(user_df))
col2.metric("Most Used Device", user_df['device_type'].mode()[0])
col3.metric("Preferred Channel", user_df['channel'].mode()[0])

col4, col5, col6 = st.columns(3)
col4.metric("Most Used Login Method", user_df['login_method'].mode()[0])
col5.metric("Top City", user_df['city'].mode()[0])
col6.metric("Common OS/Browser", user_df['os_browser'].mode()[0])

# Login Time Histogram
st.subheader("⏰ Login Hours Distribution")
hour_counts = user_df['login_hour'].value_counts().sort_index()
st.bar_chart(hour_counts)

# Geolocation Map
st.subheader("🗺️ Login Location Map")
map_data = user_df[['lat', 'lon']].drop_duplicates()
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=map_data['lat'].mean(),
        longitude=map_data['lon'].mean(),
        zoom=4,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=80000,
        )
    ]
))

# Device / Channel / Login Method Breakdown
st.subheader("📊 Behavior Breakdown")
col7, col8, col9 = st.columns(3)

with col7:
    st.markdown("**Device Type**")
    st.bar_chart(user_df['device_type'].value_counts())

with col8:
    st.markdown("**Login Methods**")
    st.bar_chart(user_df['login_method'].value_counts())

with col9:
    st.markdown("**Channels**")
    st.bar_chart(user_df['channel'].value_counts())

# Raw data toggle
with st.expander("📄 Show Raw Login Data"):
    st.dataframe(user_df)

# Optional: Compare 2 users
with st.expander("🆚 Compare with Another User"):
    other_user = st.selectbox("Compare with user:", [u for u in df['user_id'].unique() if u != user_id])
    other_df = df[df['user_id'] == other_user]

    st.markdown(f"**Comparison: {user_id} vs {other_user}**")

    comp_df = pd.DataFrame({
        "Login Count": [len(user_df), len(other_df)],
        "Device Type": [user_df['device_type'].mode()[0], other_df['device_type'].mode()[0]],
        "Top Login Hour": [user_df['login_hour'].mode()[0], other_df['login_hour'].mode()[0]],
        "Top Channel": [user_df['channel'].mode()[0], other_df['channel'].mode()[0]]
    }, index=[user_id, other_user])

    st.dataframe(comp_df)

