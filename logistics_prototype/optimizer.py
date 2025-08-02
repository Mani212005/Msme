from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def create_data_model(addresses):
    """Create the data model for the problem."""
    data = {}
    data['addresses'] = addresses
    data['num_vehicles'] = 1
    data['depot'] = 0
    
    # Create distance matrix
    num_locations = len(addresses)
    data['distance_matrix'] = []
    
    for i in range(num_locations):
        row = []
        for j in range(num_locations):
            if i == j:
                distance = 0
            else:
                # Calculate actual distance between coordinates
                lat1, lon1 = addresses[i]
                lat2, lon2 = addresses[j]
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                # Convert to meters and round to integer for OR-Tools
                distance = int(distance * 1000)
            row.append(distance)
        data['distance_matrix'].append(row)
    
    return data

def get_solution(data, manager, routing, solution):
    """Extract solution information."""
    index = routing.Start(0)
    route_distance = 0
    route = []
    
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        route.append(node_index)
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    
    # Add the final node
    route.append(manager.IndexToNode(index))
    
    # Convert distance back to kilometers
    route_distance_km = route_distance / 1000.0
    
    return route, route_distance_km

def optimize_route(addresses):
    """Solve the Vehicle Routing Problem and return optimized route."""
    if len(addresses) < 2:
        return None, None
    
    # Create the data model
    data = create_data_model(addresses)
    
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['addresses']), 
        data['num_vehicles'], 
        data['depot']
    )
    
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return get_solution(data, manager, routing, solution)
    else:
        return None, None

# Example usage and testing
if __name__ == "__main__":
    # Test with some sample coordinates
    test_addresses = [
        [28.6139, 77.2090],  # New Delhi
        [28.5355, 77.3910],  # Noida
        [28.4595, 77.0266],  # Gurgaon
        [28.7041, 77.1025],  # North Delhi
    ]
    
    route, distance = optimize_route(test_addresses)
    print(f"Optimized route: {route}")
    print(f"Total distance: {distance:.2f} km")