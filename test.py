import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

coordinates = {
    "Les Trois Vallées": {"lat": 45.3271, "lon": 6.5783},
    "Sölden": {"lat": 46.9655, "lon": 11.0076},
    "Chamonix-Mont Blanc": {"lat": 45.9237, "lon": 6.869},
    "Val di Fassa": {"lat": 46.4424081, "lon": 11.6968477},
    "Salzburger Sportwelt": {"lat": 46.8012, "lon": 9.2305},
    "Alpenarena Flims-Laax-Falera": {"lat": 47.8095, "lon": 13.0550},
    "Kitzsteinhorn Kaprun": {"lat": 47.1948, "lon": 10.1602},
    "Ski Arlberg": {"lat": 45.4692, "lon": 6.9068},
    "Espace Killy": {"lat": 50.7261, "lon": 15.6094}
}


def calculate_booking_score(avg_temp, tot_snow):
    score = 0
    if avg_temp < 0:
        score = 5
    elif 0 <= avg_temp <= 5:
        score = 4
    elif 5 < avg_temp <= 10:
        score = 3
    else:
        score = 1

    if tot_snow > 5:
        score = min(score + 1, 5)

    return score


def send_email(receiver_email, subject, body):
    sender_email = "your_email@example.com"  # Update with your email
    password = "your_email_password"  # Update with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.example.com', 587)  # Update SMTP server details
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()


for resort, coord in coordinates.items():
    lat = coord["lat"]
    lon = coord["lon"]

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

    booking_score = calculate_booking_score(avg_temp, tot_snow)

    email_body = f"Resort: {resort}\nAverage Temperature: {avg_temp:.2f}°C\nTotal Snowfall: {tot_snow:.2f}cm\nBooking.com Recommendation Score: {booking_score}/5"

    # Replace the email address with the receiver's email address
   print(email_body)
