![Image_Alt](https://github.com/Mani212005/Msme/blob/030c328166903f21de3e10af65901c654a3b761a/Screenshot%202025-08-02%20163920.jpg)


# AI Logistics Platform for MSMEs

This project is a Streamlit-based web application designed to serve as a prototype for an AI-powered logistics platform for Micro, Small, and Medium Enterprises (MSMEs). The platform offers a suite of tools for order management, delivery partner coordination, and real-time route optimization, aiming to streamline and enhance logistics operations for small businesses.

## Features

- **MSME Dashboard**: A centralized dashboard for managing shipments, including creating new orders, viewing existing ones, and assigning them to delivery partners.
- **Delivery Partner Interface**: A separate interface for delivery partners to view their assigned orders, update delivery statuses, and share estimated times of arrival (ETAs) with customers.
- **Route Optimization**: Utilizes Google OR-Tools to calculate the shortest and most efficient delivery routes, based on the Haversine distance formula for accurate geospatial calculations.
- **Bulk Order Upload**: Supports the bulk upload of orders via CSV files, with intelligent column name handling and the option to bypass geocoding by providing direct latitude and longitude coordinates.
- **Sample Data**: Includes a "Load Sample Data" feature to quickly populate the application with a predefined set of orders for demonstration and testing purposes.

## Getting Started

To get started with the AI Logistics Platform, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Mani212005/Msme.git
   cd Msme
   ```
2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit application**:
   ```bash
   streamlit run logistics_prototype/app.py
    ```
![Image_Alt](https://github.com/Mani212005/Msme/blob/030c328166903f21de3e10af65901c654a3b761a/Screenshot%202025-08-02%20163950.jpg)
## Usage

- **Creating a Shipment**: Navigate to the "Create New Shipment" form, enter the pickup and delivery addresses, and click "Create Shipment."
- **Uploading Bulk Orders**: Use the "Upload a CSV with multiple orders" feature to upload a CSV file with your order data.
- **Optimizing Routes**: Click the "Optimize Routes" button to automatically calculate the most efficient delivery routes for all pending orders.
- **Assigning Deliveries**: Manually assign orders to delivery partners or use the "Auto Assign Deliveries" feature for automated round-robin assignment.

## Technologies Used

- **Streamlit**: For building the interactive web application.
- **Pandas**: For data manipulation and management.
- **Google OR-Tools**: For route optimization and solving vehicle routing problems.
- **Geopy**: For geocoding addresses to obtain latitude and longitude coordinates.
