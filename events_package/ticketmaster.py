import os
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def query_ticketmaster_events(keyword, location, start_date, end_date):

    print(f"Received arguments - Keyword: {keyword}, Location: {location}, Start Date: {start_date}, End Date: {end_date}")

    # Convert start_date and end_date from ISO 8601 string to datetime objects if they are not already
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': os.environ['TICKETMASTER_API_KEY'],
        'keyword': keyword,
        'locale': '*',
        'city': location,
        'startDateTime': datetime.strftime(start_date, "%Y-%m-%dT%H:%M:%SZ"),
        'endDateTime': datetime.strftime(end_date, "%Y-%m-%dT%H:%M:%SZ")
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to retrieve data: {response.status_code}"

# Example usage:

# keyword = 'rock concert'
# location = 'New York'
# start_date = datetime(2024, 6, 1)
# end_date = datetime(2024, 6, 30)
# events = query_ticketmaster_events(keyword, location, start_date, end_date)
# print(events)
