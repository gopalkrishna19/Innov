import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the synthetic login metadata
df = pd.read_excel("src/code/synthetic_login_metadata.xlsx")

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['login_hour'] = df['timestamp'].dt.hour

# Create output directory
os.makedirs("fraud_profiles", exist_ok=True)

# Group by user_id
users = df['user_id'].unique()

for user in users:
    user_df = df[df['user_id'] == user]

    # Profile Summary (Text)
    profile = {
        "user_id": user,
        "total_logins": len(user_df),
        "device_type": user_df['device_type'].mode()[0],
        "os_browser": user_df['os_browser'].mode()[0],
        "screen_resolution": user_df['screen_resolution'].mode()[0],
        "city": user_df['city'].mode()[0],
        "frequent_login_hours": user_df['login_hour'].value_counts().head(3).index.tolist(),
        "most_used_login_method": user_df['login_method'].mode()[0],
        "preferred_channel": user_df['channel'].mode()[0]
    }

    print(f"\nFraud Profile for {user}")
    for k, v in profile.items():
        print(f"{k}: {v}")

    # ---- VISUALIZATIONS ----
    plt.figure(figsize=(14, 8))

    # Login Hours Histogram
    plt.subplot(2, 2, 1)
    sns.histplot(user_df['login_hour'], bins=24, kde=False, color='skyblue')
    plt.title("Login Hour Distribution")
    plt.xlabel("Hour of Day")
    plt.ylabel("Login Count")

    # Device Type Pie
    plt.subplot(2, 2, 2)
    user_df['device_type'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title("Device Type Usage")
    plt.ylabel('')

    # Login Method Count
    plt.subplot(2, 2, 3)
    sns.countplot(data=user_df, x='login_method', palette='viridis')
    plt.title("Login Method Usage")

    # Channel Usage
    plt.subplot(2, 2, 4)
    sns.countplot(data=user_df, x='channel', palette='Set2')
    plt.title("Channel Usage")

    plt.suptitle(f"Fraud Profile Visuals - {user}", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the image
    plt.savefig(f"fraud_profiles/{user}_profile.png")
    plt.close()