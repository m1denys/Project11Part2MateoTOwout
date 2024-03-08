import os.path
import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

# Vraag de reiziger om de ideale temperatuur en regentolerantie in te voeren
print("Welkom bij de Summer Sun!")
idealetemp = float(input("Wat is uw ideale temperatuur? (in graden Celsius): "))
hoeveelheid_regen = input("Wat is uw maximale regen wat u wilt hebben?\n1. Zeer weinig regen (minder dan 1mm per "
                          "dag)\n2. Minder dan 2mm"
                          "per dag (het Belgische gemiddelde)\n3. Geen voorkeur\nVoer het nummer van uw keuze in: ")
print("even geduld")


# Functie om de regenval te converteren naar de benamingen
def convert_rain_label(hoeveelheid_regen):
    if hoeveelheid_regen == "1":
        return "Zeer weinig"
    elif hoeveelheid_regen == "2":
        return "Minder dan 2mm"
    elif hoeveelheid_regen == "3":
        return "meer dan 2mm"
    else:
        return "Onbekend"


# Functie om de score te berekenen op basis van de gemiddelde temperatuur en regenval
def calculate_score(avg_temp, total_rain):
    score = 0

    # Score op basis van temperatuur
    temp_difference = abs(avg_temp - idealetemp)
    if temp_difference <= 2:
        score += 5
    elif temp_difference <= 3:
        score += 4
    elif temp_difference <= 5:
        score += 3
    elif temp_difference <= 7:
        score += 2
    elif temp_difference <= 10:
        score += 1

    # Bereken gemiddelde regen en pas de score aan
    avg_rain = total_rain / 5
    if avg_rain < 1:
        score += 4
    elif avg_rain < 2:
        score += 3
    else:
        score += 2

    return score


SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


# Functie om de temperatuur en regenval voor verschillende skigebieden te halen
def temps():
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

    avg_temps = {}
    total_rains = {}  # Een dictionary om de totale regen per gebied bij te houden

    for resort, coord in coordinates.items():
        lat = coord["lat"]
        lon = coord["lon"]
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid"
            f"=50d520feae8bb9a6d968a0fa080baf1f&units=metric")
        data = response.json()

        maxtemps = []
        total_rain = 0

        for forecast in data['list']:
            if 'main' in forecast and 'temp_max' in forecast['main']:
                maxtemps.append(forecast['main']['temp_max'])
            if 'rain' in forecast and '3h' in forecast['rain']:
                total_rain += forecast['rain']['3h']

        avg_temp = sum(maxtemps) / len(maxtemps) if maxtemps else 0

        avg_temps[resort] = avg_temp
        total_rains[resort] = total_rain / 5  # De totale regen wordt opgedeeld door 5

    return avg_temps, total_rains


# Functie om een e-mail te sturen met skiaanbevelingen
def email(avg_temps, rain_data, hoeveelheid_regen):
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)

        # Bereken scores voor elk resort
        scores = {}
        for resort, avg_temp in avg_temps.items():
            scores[resort] = calculate_score(avg_temp, rain_data[resort])

        # Sorteer de resorts op basis van hun score
        sorted_resorts = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Maak een e-mailbericht met de top 10 resorts
        message = EmailMessage()
        message["To"] = input("Geef uw e-mailadres: ")
        message["From"] = "woutbleyen@gmail.com"
        message["Subject"] = "Summer Sun van Booking.com"

        content = "Hier is de ranking van de top 10 gebieden voor uw zomervakantie:\n\n\n"
        for i, resort in enumerate(sorted_resorts[:10], start=1):
            avg_temp = avg_temps[resort]
            rain_label = convert_rain_label(hoeveelheid_regen)
            content += (f"{i}. {resort}:\n"
                        f"Gemiddelde temp: {round(avg_temp)}°C\n"
                        f" Hoeveelheid regen: {rain_label}\n\n")

        message.set_content(content)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"message": {"raw": encoded_message}}

        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
        service.users().drafts().send(userId="me", body=draft).execute()
        print("de mail is gstuurd")
    except HttpError as error:
        print(f"An error occurred: {error}")




if __name__ == "__main__":
    avg_temps, rain_data = temps()
    email(avg_temps, rain_data, hoeveelheid_regen)
