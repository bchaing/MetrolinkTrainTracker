from google.transit import gtfs_realtime_pb2
import requests
import logging
import os
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.ERROR)

load_dotenv()
API_KEY = os.getenv('METROLINK_API_KEY')
if not API_KEY:
    raise ValueError('API Key not found! Set it in a .env file or environment variables.')

FEED_URLS = {
    'trip_update': 'https://metrolink-gtfsrt.gbsdigital.us/feed/gtfsrt-trips',
    'vehicle': 'https://metrolink-gtfsrt.gbsdigital.us/feed/gtfsrt-vehicles',
    'alert': 'https://metrolink-gtfsrt.gbsdigital.us/feed/gtfsrt-alerts'
}
HEADERS = {'X-Api-Key': API_KEY}

def get_gtfs_data(feed_type):
    url = FEED_URLS.get(feed_type)
    if not url:
        logging.error('Feed type not found')
        return

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching data from {url}: {str(e)}')
        return None

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    return feed

def print_feed(feed_type):
    feed = get_gtfs_data(feed_type)
    if not feed:
        return
    
    for entity in feed.entity:
        logging.info(getattr(entity, feed_type))

def get_vehicle_data():
    feed = get_gtfs_data('vehicle')
    if not feed:
        return

    logging.info(f'Total vehicles: {len(feed.entity)}')
    
    vehicle_data = []
    for entity in feed.entity:
        logging.info(f'''
        Vehicle ID: {entity.vehicle.vehicle.id}
        Route ID: {entity.vehicle.trip.route_id}
        Position: {entity.vehicle.position.latitude}, {entity.vehicle.position.longitude}
        Speed: {entity.vehicle.position.speed}
        ''')

        vehicle_data.append({
            'vehicle_id': entity.vehicle.vehicle.id,
            'vehicle_label': entity.vehicle.vehicle.label,
            'route_id': entity.vehicle.trip.route_id,
            'latitude': entity.vehicle.position.latitude,
            'longitude': entity.vehicle.position.longitude
        })

    return pd.DataFrame(vehicle_data)

def main():
    get_vehicle_data()

if __name__ == "__main__":
    main()
