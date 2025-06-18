import streamlit as st
import pandas as pd
import pydeck as pdk

# Load all data
login_df = pd.read_excel("src/code/synthetic_login_metadata.xlsx")
session_df = pd.read_excel("src/code/synthetic_logs/session_metadata.xlsx")
transaction_df = pd.read_excel("src/code/synthetic_logs/transaction_metadata.xlsx")
feature_df = pd.read_excel("src/code/synthetic_logs/feature_usage_logs.xlsx")

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

# Common user selector
user_ids = login_df['user_id'].unique()
user_id = st.sidebar.selectbox("Select User ID", user_ids)

# --- LOGIN PROFILE TAB --- #
with login_tab:
    st.header(f"Login Behavior for {user_id}")
    user_login = login_df[login_df['user_id'] == user_id]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logins", len(user_login))
    col2.metric("Most Used Device", user_login['device_type'].mode()[0])
    col3.metric("Top Login Hour", user_login['login_hour'].mode()[0])

    st.subheader("Login Hour Distribution")
    st.bar_chart(user_login['login_hour'].value_counts().sort_index())

    st.subheader("Login Map")
    map_data = user_login[['lat', 'lon']].drop_duplicates()
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_data['lat'].mean(),
            longitude=map_data['lon'].mean(),
            zoom=4,
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
    st.dataframe(user_login)

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
