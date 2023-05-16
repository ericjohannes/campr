import json
import boto3
import requests
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, date

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

def post_types(place_id, start_date):
    """
    place_id: string of numbers representing the place id of a parkr
    start_date: string of date like "MM-DD-YYY"
    Gets availability data for a park for two nights starting on one date.
    """
    post_url = 'https://mnrdr.usedirect.com' # /minnesotardr/rdr/search/place

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
        "PlaceId": place_id,
        "Latitude":0,
        "Longitude":0,
        "HighlightedPlaceId":0,
        "StartDate": start_date,
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

def check_name(data):
    if "SelectedPlace" not in data:
        return None
    elif 'Name' not in data['SelectedPlace']:
        return None
    else:
        return data['SelectedPlace']['Name']

def make_tr(data_row):
    return f"<tr><td>{data_row['date']}</td><td>{data_row['name']}</td></tr>"

def send_email(data, start_date, end_date, places, sendgrid_api_key):

    # initialize as if no sites found
    subject = "No campsites found"
    html_content = '<p>Could not find any campsites available</p>'

    if len(data):
        subject = "Campsites found!"
        location_names = ''
        for i, p in enumerate(places):
            if i == (len(places)-1): # last one
                location_names += f"and {p['name']}."
            else:
                location_names += f"{p['name']}, "
        
        table_rows = [make_tr(row) for row in data]
        table_rows = ''.join(table_rows)
    
        html_content = f"""
            <h1>Found campsites</h1>
            <p>Searched between {start_date} and {end_date}.</p>
            <p>Looked at: {location_names}</p>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Park</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
        """
    message = Mail(
        from_email='ericjohannesblom@gmail.com',
        to_emails='ericjohannesblom@gmail.com',
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(api_key=sendgrid_api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def save_results(data):
    """
    save a json of results based on today's date
    """
    today = date.today().strftime("%m-%d-%Y")
    filename = f"results/found_{today}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

# if __name__ == '__main__':
#     start_date = nearest_friday()
#     end_date = "09-15-2023"
#     dates = generate_dates(start_date, end_date)
#     for d in dates:
#         for p in place_ids:
#             data = post_types(p['id'], d)
#             if check_availability(data):
#                 name = check_name(data)
#                 available_sites.append({
#                     "name": name,
#                     "date": d
#                 })

#     send_email(available_sites, start_date, end_date, place_ids)
    # save_results(available_sites)



def get_secret():

    secret_name = "SENDGRID_API_KEY"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    return get_secret_value_response['SecretString']