import pandas as pd
import uuid
import os

DATA_FILE = os.path.join(os.getcwd(), 'logistics_prototype', 'data', 'orders.csv')

# Load existing data or create a new DataFrame if the file doesn't exist
try:
    orders_df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    orders_df = pd.DataFrame(columns=['id', 'pickup_address', 'delivery_address', 'assigned_to', 'status', 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop', 'eta'])

new_orders_data = [
    {
        'pickup_address': 'Plot No 23, Bawana Industrial Area, Delhi',
        'lat_pick': 28.7982,
        'lon_pick': 77.03431,
        'delivery_address': 'C-19, Patparganj Industrial Area, Delhi',
        'lat_drop': 28.637063,
        'lon_drop': 77.307978
    },
    {
        'pickup_address': 'F-11, Narela Industrial Complex, Delhi',
        'lat_pick': 28.832652,
        'lon_pick': 77.099613,
        'delivery_address': 'A-45, Okhla Industrial Area Phase II, Delhi',
        'lat_drop': 28.53068,
        'lon_drop': 77.272406
    },
    {
        'pickup_address': 'D-60, Mayapuri Industrial Area Phase I, Delhi',
        'lat_pick': 28.6333498,
        'lon_pick': 77.1270148,
        'delivery_address': 'Plot No 23, Bawana Industrial Area, Delhi', # Example of a return trip
        'lat_drop': 28.7982,
        'lon_drop': 77.03431
    }
]

for order_data in new_orders_data:
    # Calculate distance and ETA (using dummy values for now, actual calculation will happen in app)
    # For this script, we'll just put N/A for ETA as it's calculated in the app
    new_order = pd.DataFrame([{
        'id': str(uuid.uuid4()),
        'pickup_address': order_data['pickup_address'],
        'delivery_address': order_data['delivery_address'],
        'assigned_to': 'N/A',
        'status': 'Pending',
        'lat_pick': order_data['lat_pick'],
        'lon_pick': order_data['lon_pick'],
        'lat_drop': order_data['lat_drop'],
        'lon_drop': order_data['lon_drop'],
        'eta': 'N/A' # Will be calculated by the app
    }])
    orders_df = pd.concat([orders_df, new_order], ignore_index=True)

orders_df.to_csv(DATA_FILE, index=False)
print(f"Successfully added new orders to {DATA_FILE}")
