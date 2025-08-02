import pandas as pd
from geopy.geocoders import Nominatim
import os
from optimizer import haversine_distance # Import the distance calculator

# Get the absolute path to the data file
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'orders.csv')

def get_lat_lon(address):
    """Geocode an address to get latitude and longitude."""
    geolocator = Nominatim(user_agent="logistics_prototype")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

def update_order_status(order_id, new_status):
    """Update the status of an order in the CSV file."""
    orders_df = pd.read_csv(DATA_FILE)
    orders_df.loc[orders_df['id'] == order_id, 'status'] = new_status
    orders_df.to_csv(DATA_FILE, index=False)

def get_estimated_delivery_time(distance_km):
    """Calculate estimated delivery time based on distance."""
    if distance_km < 100:
        return "1 day"
    elif distance_km < 1000:
        return "3 days"
    elif distance_km < 5000:
        return "5 days"
    else:
        return "7 days"