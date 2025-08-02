
import streamlit as st
import pandas as pd
from utils import get_lat_lon, update_order_status, get_estimated_delivery_time, haversine_distance
from optimizer import optimize_route
import uuid
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'orders.csv')

st.set_page_config(layout="wide")

st.title("AI Logistics Platform for MSMEs")

# Initialize session state for orders_df
if 'orders_df' not in st.session_state:
    try:
        st.session_state.orders_df = pd.read_csv(DATA_FILE)
        if 'eta' not in st.session_state.orders_df.columns:
            st.session_state.orders_df['eta'] = 'N/A'
    except FileNotFoundError:
        st.session_state.orders_df = pd.DataFrame(columns=['id', 'pickup_address', 'delivery_address', 'assigned_to', 'status', 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop', 'eta'])

# Ensure all IDs are unique and valid UUIDs in session_state
existing_ids = set()
ids_changed = False
for index, row in st.session_state.orders_df.iterrows():
    current_id = str(row['id'])
    try:
        # Check if it's a valid UUID and not already seen
        uuid.UUID(current_id)
        if current_id in existing_ids:
            raise ValueError("Duplicate ID")
        existing_ids.add(current_id)
    except (ValueError, AttributeError):
        # If not a valid UUID or duplicate, generate a new one
        new_id = str(uuid.uuid4())
        st.session_state.orders_df.at[index, 'id'] = new_id
        existing_ids.add(new_id)
        ids_changed = True

# Save changes if any IDs were regenerated
if ids_changed:
    st.session_state.orders_df.to_csv(DATA_FILE, index=False)
    st.rerun() # Rerun to load the cleaned data

# MSME Dashboard
st.header("MSME Dashboard")

# Load Sample Data Button
SAMPLE_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'sample_dataset.csv')
if st.button("Load Sample Data"):
    try:
        sample_df = pd.read_csv(SAMPLE_DATA_FILE)
        # Clean up column names (strip whitespace and convert to lowercase)
        sample_df.columns = sample_df.columns.str.strip().str.lower()

        pickup_col = 'pickupaddress'
        delivery_col = 'deliveryaddress'

        if pickup_col in sample_df.columns and delivery_col in sample_df.columns:
            processed_orders = 0
            failed_addresses = []
            for index, row in sample_df.iterrows():
                pickup_address_str = row[pickup_col]
                delivery_address_str = row[delivery_col]

                lat_pick, lon_pick, lat_drop, lon_drop = None, None, None, None

                # Try to get coordinates from CSV first
                if 'lat_pick' in sample_df.columns and 'lon_pick' in sample_df.columns and \
                   pd.notna(row.get('lat_pick')) and pd.notna(row.get('lon_pick')):
                    lat_pick = float(row['lat_pick'])
                    lon_pick = float(row['lon_pick'])
                
                if 'lat_drop' in sample_df.columns and 'lon_drop' in sample_df.columns and \
                   pd.notna(row.get('lat_drop')) and pd.notna(row.get('lon_drop')):
                    lat_drop = float(row['lat_drop'])
                    lon_drop = float(row['lon_drop'])

                # If coordinates not provided in CSV, try geocoding
                if lat_pick is None or lon_pick is None:
                    temp_pickup_address = pickup_address_str + ", Delhi, India"
                    lat_pick, lon_pick = get_lat_lon(temp_pickup_address)
                    if lat_pick is None:
                        failed_addresses.append(pickup_address_str)
                        continue

                if lat_drop is None or lon_drop is None:
                    temp_delivery_address = delivery_address_str + ", Delhi, India"
                    lat_drop, lon_drop = get_lat_lon(temp_delivery_address)
                    if lat_drop is None:
                        failed_addresses.append(delivery_address_str)
                        continue

                distance = haversine_distance(lat_pick, lon_pick, lat_drop, lon_drop)
                eta = get_estimated_delivery_time(distance)
                new_order = pd.DataFrame([{\
                    'id': str(uuid.uuid4()),
                    'pickup_address': pickup_address_str,
                    'delivery_address': delivery_address_str,
                    'assigned_to': 'N/A',
                    'status': 'Pending',
                    'lat_pick': lat_pick,
                    'lon_pick': lon_pick,
                    'lat_drop': lat_drop,
                    'lon_drop': lon_drop,
                    'eta': eta
                }])
                st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_order], ignore_index=True)
                processed_orders += 1
            
            if processed_orders > 0:
                st.session_state.orders_df.to_csv(DATA_FILE, index=False)
                st.success(f"Successfully processed {processed_orders} new orders from sample data!")
                st.rerun()

            if failed_addresses:
                st.warning("The following addresses from sample data could not be found via geocoding and were skipped:")
                for address in set(failed_addresses):
                    st.write(f"- {address}")

        else:
            st.error("The sample data CSV must have 'pickupaddress' and 'deliveryaddress' columns. Optionally, you can include 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop' for direct coordinate input.")
    except Exception as e:
        st.error(f"An error occurred while loading sample data: {e}")

# Bulk upload
st.subheader("Upload a CSV with multiple orders")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
        new_orders_df = pd.read_csv(uploaded_file)
        # Clean up column names (strip whitespace and convert to lowercase)
        new_orders_df.columns = new_orders_df.columns.str.strip().str.lower()

        # Use the correct column names from the user's CSV
        pickup_col = 'pickupaddress'
        delivery_col = 'deliveryaddress'

        if pickup_col in new_orders_df.columns and delivery_col in new_orders_df.columns:
            processed_orders = 0
            failed_addresses = []
            for index, row in new_orders_df.iterrows():
                pickup_address_str = row[pickup_col]
                delivery_address_str = row[delivery_col]

                lat_pick, lon_pick, lat_drop, lon_drop = None, None, None, None

                # Try to get coordinates from CSV first
                if 'lat_pick' in new_orders_df.columns and 'lon_pick' in new_orders_df.columns and \
                   pd.notna(row.get('lat_pick')) and pd.notna(row.get('lon_pick')):
                    lat_pick = float(row['lat_pick'])
                    lon_pick = float(row['lon_pick'])
                
                if 'lat_drop' in new_orders_df.columns and 'lon_drop' in new_orders_df.columns and \
                   pd.notna(row.get('lat_drop')) and pd.notna(row.get('lon_drop')):
                    lat_drop = float(row['lat_drop'])
                    lon_drop = float(row['lon_drop'])

                # If coordinates not provided in CSV, try geocoding
                if lat_pick is None or lon_pick is None:
                    temp_pickup_address = pickup_address_str + ", Delhi, India"
                    lat_pick, lon_pick = get_lat_lon(temp_pickup_address)
                    if lat_pick is None:
                        failed_addresses.append(pickup_address_str)
                        continue

                if lat_drop is None or lon_drop is None:
                    temp_delivery_address = delivery_address_str + ", Delhi, India"
                    lat_drop, lon_drop = get_lat_lon(temp_delivery_address)
                    if lat_drop is None:
                        failed_addresses.append(delivery_address_str)
                        continue

                distance = haversine_distance(lat_pick, lon_pick, lat_drop, lon_drop)
                eta = get_estimated_delivery_time(distance)
                new_order = pd.DataFrame([{
                    'id': str(uuid.uuid4()),
                    'pickup_address': pickup_address_str,
                    'delivery_address': delivery_address_str,
                    'assigned_to': 'N/A',
                    'status': 'Pending',
                    'lat_pick': lat_pick,
                    'lon_pick': lon_pick,
                    'lat_drop': lat_drop,
                    'lon_drop': lon_drop,
                    'eta': eta
                }])
                st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_order], ignore_index=True)
                processed_orders += 1
            
            if processed_orders > 0:
                st.session_state.orders_df.to_csv(DATA_FILE, index=False)
                st.success(f"Successfully processed {processed_orders} new orders!")

            if failed_addresses:
                st.warning("The following addresses could not be found via geocoding and were skipped. Consider adding 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop' columns to your CSV for these entries:")
                for address in set(failed_addresses):
                    st.write(f"- {address}")

        else:
            st.error("The uploaded CSV must have 'pickupaddress' and 'deliveryaddress' columns. Optionally, you can include 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop' for direct coordinate input.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

with st.form("new_shipment_form"):
    st.subheader("Create New Shipment")
    pickup_address = st.text_input("Pickup Address")
    delivery_address = st.text_input("Delivery Address")
    submitted = st.form_submit_button("Create Shipment")

    if submitted:
        if pickup_address and delivery_address:
            lat_pick, lon_pick = get_lat_lon(pickup_address)
            lat_drop, lon_drop = get_lat_lon(delivery_address)
            if lat_pick is not None:
                new_order = pd.DataFrame([{
                    'id': str(uuid.uuid4()),
                    'pickup_address': pickup_address,
                    'delivery_address': delivery_address,
                    'assigned_to': 'N/A',
                    'status': 'Pending',
                    'lat_pick': lat_pick,
                    'lon_pick': lon_pick,
                    'lat_drop': lat_drop,
                    'lon_drop': lon_drop
                }])
                distance = haversine_distance(lat_pick, lon_pick, lat_drop, lon_drop)
                eta = get_estimated_delivery_time(distance)
                new_order['eta'] = eta
                st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_order], ignore_index=True)
                st.session_state.orders_df.to_csv(DATA_FILE, index=False)
                st.success("Shipment created successfully!")
                st.info(f"Estimated delivery time: {eta}")
            else:
                st.error("Could not geocode the address. Please check and try again.")
        else:
            st.error("Please provide both pickup and delivery addresses.")


# Delivery Partner Interface
tabs = st.tabs(["MSME Dashboard", "Delivery Partner View"])

with tabs[0]:
    st.dataframe(st.session_state.orders_df)

    for index, order in st.session_state.orders_df.iterrows():
        with st.expander(f"Order {order['id']}"):
            st.write(f"**Pickup:** {order['pickup_address']}")
            st.write(f"**Delivery:** {order['delivery_address']}")
            st.write(f"**Status:** {order['status']}")
            st.write(f"**Assigned to:** {order['assigned_to']}")
            st.write(f"**Estimated Delivery Time:** {order.get('eta', 'N/A')}")

            delivery_partners = ["Partner A", "Partner B", "Partner C"] # Replace with your actual list
            selected_partner = st.selectbox("Assign to", ["N/A"] + delivery_partners, key=f"partner_{order['id']}")

            if st.button("Assign", key=f"assign_{order['id']}"):
                st.session_state.orders_df.loc[st.session_state.orders_df['id'] == order['id'], 'assigned_to'] = selected_partner
                st.session_state.orders_df.to_csv(DATA_FILE, index=False)
                st.success(f"Order {order['id']} assigned to {selected_partner}")


    if st.button("Optimize Routes"):
        pending_orders = st.session_state.orders_df[st.session_state.orders_df['status'] == 'Pending']
        if not pending_orders.empty:
            st.write(pending_orders)
            # The optimizer needs a depot and a list of stops.
            # We'll use the first pending order's pickup as the depot.
            depot = pending_orders.iloc[0][['lat_pick', 'lon_pick']].values.tolist()
            
            # All delivery locations will be the stops.
            stops = pending_orders[['lat_drop', 'lon_drop']].values.tolist()
            
            # Combine depot and stops.
            locations = [depot] + stops
            
            # Create a list of unique locations, preserving the depot as the first element.
            unique_locations = []
            for item in locations:
                if item not in unique_locations:
                    unique_locations.append(item)

            optimized_route, total_distance = optimize_route(unique_locations)
            if optimized_route:
                st.success(f"Optimized route found!")
                
                # Display the optimized route using the actual coordinates
                route_coords = [unique_locations[i] for i in optimized_route]
                st.write("Optimized Route (sequence of coordinates):")
                st.dataframe(pd.DataFrame(route_coords, columns=['Latitude', 'Longitude']))
                
                st.info(f"Total distance: {total_distance:.2f} km")
                total_eta = get_estimated_delivery_time(total_distance)
                st.info(f"Estimated delivery time for the entire route: {total_eta}")
            else:
                st.error("Could not optimize routes. Ensure you have at least one order.")
        else:
            st.warning("No pending orders to optimize.")

    if st.button("Auto Assign Deliveries"):
        pending_orders = st.session_state.orders_df[st.session_state.orders_df['status'] == 'Pending']
        if not pending_orders.empty:
            delivery_partners = ["Partner A", "Partner B", "Partner C"] # Replace with your actual list
            if not delivery_partners:
                st.warning("No delivery partners available to assign.")
            else:
                partner_index = 0
                for index, order in pending_orders.iterrows():
                    assigned_partner = delivery_partners[partner_index % len(delivery_partners)]
                    st.session_state.orders_df.loc[st.session_state.orders_df['id'] == order['id'], 'assigned_to'] = assigned_partner
                    partner_index += 1
                st.session_state.orders_df.to_csv(DATA_FILE, index=False)
                st.success(f"Successfully assigned {len(pending_orders)} pending orders to delivery partners.")
                st.rerun()
        else:
            st.warning("No pending orders to auto-assign.")

    # Clear Data Button
    if st.button("Clear All Order Data"):
        st.session_state.orders_df = pd.DataFrame(columns=['id', 'pickup_address', 'delivery_address', 'assigned_to', 'status', 'lat_pick', 'lon_pick', 'lat_drop', 'lon_drop', 'eta'])
        st.session_state.orders_df.to_csv(DATA_FILE, index=False)
        st.success("All order data cleared!")
        st.rerun()

with tabs[1]:
    st.header("Delivery Partner View")
    delivery_partners = ["Partner A", "Partner B", "Partner C"] # Replace with your actual list
    selected_partner = st.selectbox("Select Delivery Partner", delivery_partners)

    if selected_partner:
        assigned_orders = st.session_state.orders_df[st.session_state.orders_df['assigned_to'] == selected_partner]
        st.subheader(f"Assigned Orders for {selected_partner}")
        st.dataframe(assigned_orders)

        for index, order in assigned_orders.iterrows():
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Update Status for Order {order['id']}"):
                    new_status = st.selectbox("New Status", ["Picked Up", "Delivered"], key=f"status_{order['id']}")
                    if new_status:
                        update_order_status(order['id'], new_status)
                        st.success(f"Order {order['id']} status updated to {new_status}")
            with col2:
                if st.button(f"Share Details for Order {order['id']}"):
                    eta = order.get('eta', 'N/A')
                    share_text = f"Your order from {order['pickup_address']} is on its way! It will be delivered to {order['delivery_address']} in approximately {eta} by our delivery partner, {order['assigned_to']}."
                    st.text_area("Share this with the receiver:", share_text, key=f"share_{order['id']}")
