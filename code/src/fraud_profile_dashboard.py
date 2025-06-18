import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.distance import geodesic

# Load all data
login_df = pd.read_excel("code/src/synthetic_logs/synthetic_login_metadata.xlsx")
session_df = pd.read_excel("code/src/synthetic_logs/session_metadata.xlsx")
transaction_df = pd.read_excel("code/src/synthetic_logs/transaction_metadata.xlsx")
feature_df = pd.read_excel("code/src/synthetic_logs/feature_usage_logs.xlsx")

# Preprocess timestamps
login_df['timestamp'] = pd.to_datetime(login_df['timestamp'])
session_df['timestamp'] = pd.to_datetime(session_df['timestamp'])
transaction_df['timestamp'] = pd.to_datetime(transaction_df['timestamp'])
feature_df['timestamp'] = pd.to_datetime(feature_df['timestamp'])

# Extract hour for login patterns
login_df['login_hour'] = login_df['timestamp'].dt.hour

st.set_page_config(layout="wide")
st.title("🔒 Fraud Profile Explorer")

# Tabs
login_tab, session_tab, transaction_tab, feature_tab = st.tabs([
    "🔐 Login Profile", "🔄 Session Activity", "💳 Transactions", "🔧 Feature Usage"
])

# --- LOGIN PROFILE TAB --- #
with login_tab:
    st.sidebar.title("🛡️ Fraud Profile Dashboard")
    user_id = st.sidebar.selectbox("Select a User", login_df['user_id'].unique())

    user_df = login_df[login_df['user_id'] == user_id].sort_values(by='timestamp').reset_index(drop=True)

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

    # Strict Anomaly Detection
    st.subheader("🚨 Strict Anomaly Detection with Risk Scoring")

    mode_device = user_df['device_type'].mode()[0]
    mode_method = user_df['login_method'].mode()[0]
    mode_channel = user_df['channel'].mode()[0]
    mode_hour = user_df['login_hour'].mode()[0]

    user_df['anomaly_reason'] = ""
    user_df['anomaly_score'] = 0

    user_df.loc[user_df['device_type'] != mode_device, ['anomaly_reason', 'anomaly_score']] = ["Unusual Device", 0.25]
    user_df.loc[user_df['login_method'] != mode_method, ['anomaly_reason', 'anomaly_score']] += ["; Unusual Method", 0.25]
    user_df.loc[user_df['channel'] != mode_channel, ['anomaly_reason', 'anomaly_score']] += ["; Unusual Channel", 0.2]
    user_df.loc[abs(user_df['login_hour'] - mode_hour) > 3, ['anomaly_reason', 'anomaly_score']] += ["; Odd Login Hour", 0.2]

    for i in range(1, len(user_df)):
        prev = user_df.loc[i - 1]
        curr = user_df.loc[i]
        loc1 = (prev['lat'], prev['lon'])
        loc2 = (curr['lat'], curr['lon'])
        time_diff_hr = (curr['timestamp'] - prev['timestamp']).total_seconds() / 3600
        if time_diff_hr > 0:
            distance_km = geodesic(loc1, loc2).km
            speed = distance_km / time_diff_hr
            if speed > 500:
                user_df.loc[i, 'anomaly_reason'] += "; High GeoVelocity"
                user_df.loc[i, 'anomaly_score'] += 0.3

    user_df['anomaly_score'] = user_df['anomaly_score'].clip(upper=1.0)
    anomalies = user_df[user_df['anomaly_score'] > 0.4].copy().reset_index(drop=True)

    def highlight_risk(row):
        if row['anomaly_score'] > 0.7:
            return ['background-color: red'] * len(row)
        elif row['anomaly_score'] > 0.4:
            return ['background-color: orange'] * len(row)
        else:
            return ['background-color: lightgreen'] * len(row)

    st.markdown("### ⚠️ Anomalies Detected (with Risk Levels)")

    selected_index = st.selectbox("Select an anomaly row to explain:", anomalies.index)
    st.dataframe(anomalies[['timestamp', 'device_type', 'login_method', 'channel', 'login_hour', 'lat', 'lon', 'anomaly_reason', 'anomaly_score']].style.apply(highlight_risk, axis=1))

    if selected_index is not None and selected_index in anomalies.index:
        st.markdown("#### 🧾 Explanation for Selected Anomaly")
        selected_row = anomalies.loc[selected_index]
        for col in ['timestamp', 'device_type', 'login_method', 'channel', 'login_hour', 'lat', 'lon', 'anomaly_reason', 'anomaly_score']:
            st.write(f"**{col}**: {selected_row[col]}")

    # Raw data toggle
    with st.expander("📄 Show Raw Login Data"):
        st.dataframe(user_df)

# --- SESSION ACTIVITY TAB --- #
with session_tab:
    st.header(f"Session Activity for {user_id}")
    user_sessions = session_df[session_df['user_id'] == user_id]

    st.subheader("Session Duration Stats")
    st.metric("Average Duration (s)", round(user_sessions['session_duration_sec'].mean(), 2))

    st.subheader("Pages Visited")
    st.dataframe(user_sessions[['timestamp', 'session_duration_sec', 'pages_visited']])

# --- TRANSACTION TAB --- #
with transaction_tab:
    st.header(f"Transactions for {user_id}")
    user_txn = transaction_df[transaction_df['user_id'] == user_id]

    st.metric("Total Transactions", len(user_txn))
    st.metric("Avg. Amount", round(user_txn['amount'].mean(), 2))

    st.subheader("Transaction Breakdown")
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(user_txn['transaction_type'].value_counts())
    with col2:
        st.bar_chart(user_txn['method'].value_counts())

    st.dataframe(user_txn)

# --- FEATURE USAGE TAB --- #
with feature_tab:
    st.header(f"Feature Usage for {user_id}")
    user_features = feature_df[feature_df['user_id'] == user_id]

    st.metric("Features Used", user_features['feature'].nunique())

    st.subheader("Usage Frequency")
    freq_df = user_features.groupby('feature')['frequency'].sum().sort_values(ascending=False)
    st.bar_chart(freq_df)

    st.dataframe(user_features)

# --- DATA INPUT TAB --- #
input_tab = st.sidebar.checkbox("➕ Add New Login Data")

if input_tab:
    st.title("📥 Add New Login Record")

    input_method = st.radio("Choose input method", ["Manual Entry", "Upload CSV"])

    if input_method == "Manual Entry":
        with st.form("manual_entry_form"):
            user_id = st.text_input("User ID")
            timestamp = st.text_input("Timestamp (e.g. 2025-06-18 14:30:00)")
            device_type = st.text_input("Device Type")
            os_browser = st.text_input("OS/Browser")
            screen_resolution = st.text_input("Screen Resolution")
            ip = st.text_input("IP Address")
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            city = st.text_input("City")
            login_method = st.text_input("Login Method")
            channel = st.text_input("Channel")

            submitted = st.form_submit_button("Submit")
            if submitted:
                st.success("✅ Data Submitted")
                st.json({
                    "user_id": user_id,
                    "timestamp": timestamp,
                    "device_type": device_type,
                    "os_browser": os_browser,
                    "screen_resolution": screen_resolution,
                    "ip": ip,
                    "lat": lat,
                    "lon": lon,
                    "city": city,
                    "login_method": login_method,
                    "channel": channel
                })

    elif input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file:
            df_uploaded = pd.read_csv(uploaded_file)
            st.write("📄 Uploaded Data Preview:")
            st.dataframe(df_uploaded)

            expected_cols = ['user_id', 'timestamp', 'device_type', 'os_browser', 'screen_resolution', 'ip', 'lat', 'lon', 'city', 'login_method', 'channel']
            missing_cols = set(expected_cols) - set(df_uploaded.columns)

            if missing_cols:
                st.error(f"Missing columns in uploaded file: {missing_cols}")
            else:
                st.success("✅ File structure is valid.")
