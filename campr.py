import json
import requests
from datetime import datetime, timedelta

base_url = 'https://reservemn.usedirect.com'
post_url = 'https://mnrdr.usedirect.com' # /minnesotardr/rdr/search/place

place_ids = [
    {
        "id":"104",
        "name":'Tettegouche State Park',
    },
    {
        "id":"",
        "name":"",
    },
    {
        "id":"",
        "name":"",
    },
    {
        "id":"",
        "name":"",
    },
    {
        "id":"",
        "name":"",
    },
]

available_sites = []

def nearest_friday():
    """
    Returns the nearest Friday to today in the format "MM-DD-YYYY".
    """
    today = datetime.now().date()
    days_to_friday = (4 - today.weekday()) % 7
    friday = today + timedelta(days=days_to_friday)
    return friday.strftime("%m-%d-%Y")

def generate_dates(start_date, end_date):
    """
    Generates dates seven days apart in the format "MM-DD-YYYY" between the given start and end dates.
    """
    dates = []
    current_date = datetime.strptime(start_date, "%m-%d-%Y")
    end_date = datetime.strptime(end_date, "%m-%d-%Y")
    while current_date <= end_date:
        dates.append(current_date.strftime("%m-%d-%Y"))
        current_date += timedelta(days=7)
    return dates

def get_og_data():
    og_url = f'{base_url}/MinnesotaWeb/'

    res = requests.get(og_url)
    return res

def get_facilites(needle):
    # gets list of facilties by contains
    url = f'{base_url}/minnesotardr/rdr/fd/citypark/namecontains/{needle}'
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return dict()

def post_types():

    headers = {
        # ":authority": "mnrdr.usedirect.com",
        # ":method": "POST",
        # ":path": "/minnesotardr/rdr/search/place",
        # ":scheme": "https",
        # "accept": "application/json, text/javascript, */*; q=0.01",
        # "accept-encoding": "gzip, deflate, br",
        # "accept-language": "en-US,en;q=0.9",
        # "content-length": "380",
        "content-type": "application/json",
        "origin": "https://reservemn.usedirect.com",
        "referer": "https://reservemn.usedirect.com/",
        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}
    payload = {
        "PlaceId":"104",
        "Latitude":0,
        "Longitude":0,
        "HighlightedPlaceId":0,
        "StartDate":"07-01-2023",
        "Nights":"2",
        "CountNearby":False,
        "NearbyLimit":100,
        "NearbyOnlyAvailable":False,
        "NearbyCountLimit":10,
        "Sort":"Distance",
        "CustomerId":"0",
        "RefreshFavourites":True,
        "IsADA":False,
        "UnitCategoryId":0,
        "SleepingUnitId":0,
        "MinVehicleLength":0,
        "UnitTypesGroupIds": ["162","163"],
        "Highlights":[],
        "AmenityIds":[]
    } 
    url = f'{post_url}/minnesotardr/rdr/search/place'
    res = requests.post(url, data=json.dumps(payload),headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        return dict()

def check_availability(data):
    if "SelectedPlace" not in data:
        return None
    elif 'Available' not in data['SelectedPlace']:
        return None
    else:
        return data['SelectedPlace']['Available']

if __name__ == '__main__':
    start_date = nearest_friday()
    end_date = "09-15-2023"
    dates = generate_dates(start_date, end_date)
    data = post_types()

    print(data)