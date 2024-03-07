import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# teken om ff te wachten = handig
print("even wachten, we komen zo tot u")

idealetemp = input("ideale tempratuur:")

def ideale_temp(avg_temp):
    if avg_temp < idealetemp:
        break

def calculate_score(avg_temp):
    score = 0
    # hier kijk het programma naar de gemiddelde temp en gaat dan naarop kijken welke score hij moet geven
    if avg_temp < 0:
        score += 5
    elif 0 <= avg_temp < 5:
        score += 4
    elif 5 <= avg_temp < 10:
        score += 3
    else:
        score += 1


    return score


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def main():
    coordinates = {
        "Ankara, Turkey": {"lat": 39.9334, "lon": 32.8597},
        "Athens, Greece": {"lat": 37.9838, "lon": 23.7275},
        "Valletta, Malta": {"lat": 35.8989, "lon": 14.5146},
        "Sardinia, Italy": {"lat": 40.1209, "lon": 9.0129},
        "Sicily, Italy": {"lat": 37.5990, "lon": 14.0154},
        "Nicosia, Cyprus": {"lat": 35.1856, "lon": 33.3823},
        "Mallorca, Spain": {"lat": 39.6953, "lon": 3.0176},
        "Lagos, Portugal": {"lat": 37.1028, "lon": -8.6741},
        "Mauritius": {"lat": -20.3484, "lon": 57.5522},
        "Bucharest, Romania": {"lat": 44.4268, "lon": 26.1025}

    }

    import requests

    avg_temps = {}
    scores = {}
    # voor ieder resort gaat het hier de coordinaten halen
    for resort, coord in coordinates.items():
        lat = coord["lat"]
        lon = coord["lon"]
        # dit is de api
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid"
            f"=50d520feae8bb9a6d968a0fa080baf1f&units=metric")
        data = response.json()

        maxtemps = []
        # deze functie haal de info uit de maximum temperatuur en de sneewval uit de api json file
        for forecast in data['list']:
            if 'main' in forecast and 'temp_max' in forecast['main']:
                maxtemps.append(forecast['main']['temp_max'])

        # berekening van gemiddelde temp en sneeuwval
        avg_temp = sum(maxtemps) / len(maxtemps) if maxtemps else 0

        # dit steekt voor iedere resort de gem temp en de totale sneeuwval in dicionairies
        avg_temps[resort] = avg_temp


        # berekent voor ieder skigebied score op 5 en stopt het in een dict
        scores[resort] = calculate_score(avg_temp)

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
        result_data = ""
        for resort, avg_temp in avg_temps.items():
            result_data += f"{resort}, Gemiddelde temp: {round(avg_temp)}°C, Score: {scores[resort]}/5\n\n"

        message = EmailMessage()

        message.set_content(result_data)
        # input mail
        message["To"] = input("geef je email adres: ")
        message["From"] = "woutbleyen@gmail.com"
        message["Subject"] = "SKi-aanbevelingen van Booking.com"

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
