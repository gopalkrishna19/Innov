import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Constants
NUM_USERS = 50
NUM_LOGINS = 500

device_types = ["mobile", "desktop", "tablet"]
os_browsers = {
    "mobile": ["Android/Chrome", "iOS/Safari"],
    "desktop": ["Windows/Chrome", "Mac/Safari", "Linux/Firefox"],
    "tablet": ["iOS/Safari", "Android/Chrome"]
}
resolutions = {
    "mobile": ["1080x2340", "750x1334", "720x1600"],
    "desktop": ["1920x1080", "1366x768", "1440x900"],
    "tablet": ["1536x2048", "1200x1920"]
}
login_methods = ["password", "biometric", "OTP"]
channels = ["web", "app", "API"]

locations = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston", "lat": 29.7604, "lon": -95.3698},
    {"city": "Miami", "lat": 25.7617, "lon": -80.1918},
]


def random_ip(seed=None):
    if seed:
        random.seed(seed)
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def create_user_profiles():
    profiles = {}
    for i in range(1, NUM_USERS + 1):
        user_id = f"U{str(i).zfill(4)}"
        device = random.choice(device_types)
        os_browser = random.choice(os_browsers[device])
        resolution = random.choice(resolutions[device])
        location = random.choice(locations)
        ip = random_ip(seed=user_id)  # make IP stable per user

        profiles[user_id] = {
            "device_type": device,
            "os_browser": os_browser,
            "screen_resolution": resolution,
            "ip": ip,
            "geolocation": location
        }
    return profiles


def generate_login_data():
    user_profiles = create_user_profiles()
    logins = []
    base_time = datetime.utcnow()

    for _ in range(NUM_LOGINS):
        user_id = random.choice(list(user_profiles.keys()))
        profile = user_profiles[user_id]

        login_entry = {
            "user_id": user_id,
            "timestamp": (base_time - timedelta(minutes=random.randint(0, 100000))).isoformat() + "Z",
            "device_type": profile["device_type"],
            "os_browser": profile["os_browser"],
            "screen_resolution": profile["screen_resolution"],
            "ip": profile["ip"],
            "lat": profile["geolocation"]["lat"],
            "lon": profile["geolocation"]["lon"],
            "city": profile["geolocation"]["city"],
            "login_method": random.choice(login_methods),
            "channel": random.choice(channels)
        }
        logins.append(login_entry)

    return logins


# Generate login records
logins = generate_login_data()

# Convert to DataFrame
df = pd.DataFrame(logins)

# Save to Excel
excel_file = "src/code/synthetic_login_metadata.xlsx"
df.to_excel(excel_file, index=False)

print(f"Saved {len(logins)} login events to {excel_file}")