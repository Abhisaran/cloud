# from cryptography.fernet import Fernet
#
#
# def encrypt(message: bytes, key: bytes) -> bytes:
#     return Fernet(key).encrypt(message)
#
#
# def decrypt(token: bytes, key: bytes) -> bytes:
#     return Fernet(key).decrypt(token)
#
# # key = Fernet.generate_key()
# # print(key.decode())
# # print(key)
# key = b'lggCcPdSdMHqH6c7P8C88B9KpysMoo5_zCjUTxhqPyA='
# print(type(key))
# mess = 'Hello there'
# e = encrypt(mess.encode(), key)
# print(encrypt(mess.encode(), key))
# print(decrypt(e, key).decode())
import boto3

import python_weather
import asyncio

import requests

resource, client = boto3.resource('dynamodb', region_name='ap-southeast-2'), boto3.client('dynamodb',
                                                                                          region_name='ap-southeast-2')
table = resource.Table('user-donor')

# form_data_dict = {'name': 'asda', 'dob': '', 'address': '', 'availability': '1', 'emergency-contact': '',
#                   'emergency-contact-rel': '', 'blood-group': '', 'total-blood-donations': '', 'membership-ids': '',
#                   'alcoholic': '', 'diabetic': '', 'medical-conditions': '', 'submit': 'Submit'}
# email = 'b'
#
# response = table.get_item(
#         Key={
#             'email': email
#         }
#     )
# # print(response)
# item1 = response.get('Item')
# item2 = form_data_dict
# print(item1)
# print(item2)
# print(item1.update(item2))
# print(item1)

# table = resource.Table('blood-requests')
# res = table.scan()
# print(res.get('Items'))
#
# response = client.get_item(
#     TableName='user-donor',
#     Key={
#         'email': {
#             'S' :'a'}
#     }
# )
#
# print(response)
#
# if 'Item' in response:
#     print(True)


api_key = "kG9Xfg5wM7GcyIVVsnRZN4G7hT3mAcCp"


async def getweather():
    # declare the client. format defaults to metric system (celcius, km/h, etc.)
    client = python_weather.Client(format=python_weather.METRIC)

    # fetch a weather forecast from a city
    weather = await client.find("Melbourne")

    # returns the current day's forecast temperature (int)
    print(weather.current.temperature)
    print(weather.current)
    # get the weather forecast for a few days
    for forecast in weather.forecasts:
        print(str(forecast.date), forecast.sky_text, forecast.temperature)

    # close the wrapper once done
    await client.close()


#
#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(getweather())

from geopy.geocoders import Nominatim
import weather_forecast as wf
from datetime import datetime

# weather = wf.forecast(place="Melbourne")
# print(weather)
date_time = datetime.now()
time = date_time.strftime("%H:%M:%S")
date = date_time.strftime("%Y-%m-%d")
place = "Melbourne"
geolocator = Nominatim(user_agent="forecast")
location = geolocator.geocode(place)
latitude = round(location.latitude, 2)
longitude = round(location.longitude, 2)

api_endpoint = f"https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode={latitude}%2C{longitude}&language=en-IN&units=m"
response = requests.get(api_endpoint)
response_data = response.json()
# print(response_data)
# print(weather.get('day').get('temperature'))

try:
    # data wise data
    dates_time_list = response_data["vt1dailyForecast"]["validDate"]
    dates_list = [_.split("T0")[0] for _ in dates_time_list]
    # today's date index
    date_index = dates_list.index(date)
except Exception as e:
    print("Please check the date format. [Y-m-d]")

try:
    # day
    temperature_day = response_data["vt1dailyForecast"][
        "day"]["temperature"][date_index]
    precipitate_day = response_data["vt1dailyForecast"][
        "day"]["precipPct"][date_index]
    uv_description_day = response_data["vt1dailyForecast"][
        "day"]["uvDescription"][date_index]
    wind_speed_day = response_data["vt1dailyForecast"][
        "day"]["windSpeed"][date_index]
    humidity_day = response_data["vt1dailyForecast"][
        "day"]["humidityPct"][date_index]
    phrases_day = response_data["vt1dailyForecast"][
        "day"]["phrase"][date_index]
    narrative_day = response_data["vt1dailyForecast"][
        "day"]["narrative"][date_index]

    # night
    temperature_night = response_data["vt1dailyForecast"][
        "night"]["temperature"][date_index]
    precipitate_night = response_data["vt1dailyForecast"][
        "night"]["precipPct"][date_index]
    uv_description_night = response_data["vt1dailyForecast"][
        "night"]["uvDescription"][date_index]
    wind_speed_night = response_data["vt1dailyForecast"][
        "night"]["windSpeed"][date_index]
    humidity_night = response_data["vt1dailyForecast"][
        "night"]["humidityPct"][date_index]
    phrases_night = response_data["vt1dailyForecast"][
        "night"]["phrase"][date_index]
    narrative_night = response_data["vt1dailyForecast"][
        "night"]["narrative"][date_index]

    forecast_output = {}
    forecast_output["place"] = place
    forecast_output["time"] = time
    forecast_output["date"] = date
    forecast_output["day"] = {"temperature": temperature_day,
                              "precipitate": precipitate_day,
                              "uv_description": uv_description_day,
                              "wind_speed": wind_speed_day,
                              "humidity": humidity_day,
                              "phrases": phrases_day,
                              "narrative": narrative_day

                              }

    forecast_output["night"] = {"temperature": temperature_night,
                                "precipitate": precipitate_night,
                                "uv_description": uv_description_night,
                                "wind_speed": wind_speed_night,
                                "humidity": humidity_night,
                                "phrases": phrases_night,
                                "narrative": narrative_night
                                }

except Exception as e:
    print("Exception while fetching data")

print(forecast_output.get('day').get('temperature'))
