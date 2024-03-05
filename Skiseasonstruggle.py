import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        """Create and insert a draft email.
               Print the returned draft's message and id.
               Returns: Draft object, including draft id and message meta data.

              Load pre-authorized user credentials from the environment.
              TODO(developer) - See https://developers.google.com/identity
              for guides on implementing OAuth2 for the application.
              """

        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()

        message.set_content("Ski recomendations")

        message["To"] = 1
        message["From"] = "mateodenys@gmail.com"
        message["Subject"] = "SKi recommendations"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
        service.users().drafts().send(userId="me", body=draft).execute()

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()


coordinates = {
    "Les Trois Vallées": {"lat": 45.3271, "lon": 6.5783},
    "Sölden": {"lat": 46.9655, "lon": 11.0076},
    "Chamonix-Mont Blanc": {"lat": 45.9237, "lon": 6.869},
    "4": {"lat": 46.4424081, "lon": 11.6968477},
    "5": {"lat": 46.8012, "lon": 9.2305},
    "6": {"lat": 47.8095, "lon": 13.0550},
    "7": {"lat": 47.1948, "lon": 10.1602},
    "8": {"lat": 45.4692, "lon": 6.9068},
    "Espace Killy": {"lat": 50.7261, "lon": 15.6094}
}

avg_temps = {}
snowfalls = {}

for resort, coord in coordinates.items():
    lat = coord["lat"]
    lon = coord["lon"]
import requests

response = requests.get(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=50d520feae8bb9a6d968a0fa080baf1f&units=metric")
data = response.json()

maxtemps = []
snowpdays = []

for forecast in data['list']:
    if 'main' in forecast and 'temp_max' in forecast['main']:
            maxtemps.append(forecast['main']['temp_max'])
    if 'main' in forecast and 'snow' in forecast['main']:
            snowpdays.append(
                forecast['main']['snow']['3h'] / 10 if 'snow' in forecast['main'] else 0)

    avg_temp = sum(maxtemps) / len(maxtemps) if maxtemps else 0
    tot_snow = sum(snowpdays)

    avg_temps[resort] = avg_temp
    snowfalls[resort] = tot_snow

for resort, avg_temp in avg_temps.items():
    print(f"Resort: {resort}, Average Temperature: {avg_temp}°C")

for resort, snowfall in snowfalls.items():
    print(f"Resort: {resort}, Total Snowfall: {snowfall}cm")