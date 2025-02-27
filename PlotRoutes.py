import pandas as pd
from pyproj import Transformer
import matplotlib.pyplot as plt
from TrainTracker import get_vehicle_data


SHAPES_PATH = 'gtfs/shapes.txt'
STOPS_PATH = 'gtfs/stops.txt'
TRIPS_PATH = 'gtfs/trips.txt'

ROUTE_COLORS = {
    '91': '#0071CE',
    'AV': '#00AF43',
    'IEOC': '#E92076',
    'OC': '#FF8400',
    'RIVER': '#682E86',
    'SB': '#A32136',
    'VT': '#FFB81D'
}


def transform_and_normalize(dataframe, x_min=None, x_max=None, y_min=None, y_max=None):\
    # UTM Zone 11N (Southern California)
    # EPSG:4326 is the coordinate system for standard lat/long
    # EPSG:32611 is UTM Zone 11N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32611", always_xy=True)
    
    # Transform coordinates based on available column names
    if 'shape_pt_lon' in dataframe.columns and 'shape_pt_lat' in dataframe.columns:
        dataframe['x'], dataframe['y'] = transformer.transform(
            dataframe['shape_pt_lon'],
            dataframe['shape_pt_lat']
        )
    elif 'latitude' in dataframe.columns and 'longitude' in dataframe.columns:
        dataframe['x'], dataframe['y'] = transformer.transform(
            dataframe['longitude'],
            dataframe['latitude']
        )
    else:
        raise ValueError("No latitude or longitude columns found in dataframe")

    # Calculate normalization bounds if not provided
    if x_min is None:
        x_min = dataframe['x'].min()
    if x_max is None:
        x_max = dataframe['x'].max()
    if y_min is None:
        y_min = dataframe['y'].min()
    if y_max is None:
        y_max = dataframe['y'].max()
    
    # Create normalized columns
    dataframe['x_norm'] = (dataframe['x'] - x_min) / (x_max - x_min)
    dataframe['y_norm'] = (dataframe['y'] - y_min) / (y_max - y_min)
    
    return dataframe


def get_bounds(shapes_df):
    x_min = shapes_df['x'].min()
    x_max = shapes_df['x'].max()
    y_min = shapes_df['y'].min()
    y_max = shapes_df['y'].max()
    return x_min, x_max, y_min, y_max


def plot_routes(shapes_df, x_min, x_max, y_min, y_max):
    print("plotting routes...")
    # Get the normalization bounds from shapes_df first
    shapes_df = transform_and_normalize(shapes_df, x_min, x_max, y_min, y_max)

    # Plot each route with its corresponding color
    for route_id, color in ROUTE_COLORS.items():
        route_data = shapes_df[shapes_df['shape_id'].str.startswith(route_id)]
        if not route_data.empty:
            plt.plot(route_data['x_norm'], route_data['y_norm'], 
                    color=color, label=route_id, linewidth=2)
            

def plot_stops(stops_df):
    pass


def plot_trains(trains_df, x_min, x_max, y_min, y_max):
    print("plotting trains...")
    trains_df = transform_and_normalize(trains_df, x_min, x_max, y_min, y_max)
    
    # Plot train points
    plt.scatter(trains_df['x_norm'], trains_df['y_norm'], 
                c='red', label='Trains', alpha=1, zorder=10)
    
    # Add labels for each train
    for _, train in trains_df.iterrows():
        plt.annotate(train['vehicle_label'], 
                    (train['x_norm'], train['y_norm']),
                    xytext=(5, 5),  # 5 pixels offset
                    textcoords='offset points',
                    fontsize=8,
                    alpha=0.7)

if __name__ == '__main__':
    shapes_df = pd.read_csv(SHAPES_PATH)
    shapes_df = transform_and_normalize(shapes_df)

    x_min, x_max, y_min, y_max = get_bounds(shapes_df)

    trains_df = get_vehicle_data()
    trains_df = transform_and_normalize(trains_df, x_min, x_max, y_min, y_max)

    trips_df = pd.read_csv(TRIPS_PATH)

    # Create a new figure
    plt.figure(figsize=(10, 10))

    plot_routes(shapes_df, x_min, x_max, y_min, y_max)
    plot_trains(trains_df, x_min, x_max, y_min, y_max)

    plt.title('Metrolink Routes')
    plt.xlabel('Normalized X')
    plt.ylabel('Normalized Y')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Save the plot
    plt.show()
    