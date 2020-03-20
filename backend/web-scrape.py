from bs4 import BeautifulSoup
import requests
import sys
import re

## GLOBAL VARIABLE DECLARATION ##

basic_response = ""
basic_content = ""
basic_table = ""
detailed_response = ""
detailed_content = ""
detailed_table = ""
regex = re.compile('([^\s\w]|_)+')

def get_basic_response(location):
    url = "https://www.forecast.co.uk/"+location+".html"
    try:
        response = requests.get(url, timeout = 5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("That location does not exist!")
        sys.exit(1)
    return response

def get_detailed_response(location):
    url = "https://www.forecast.co.uk/"+location+".html?v=detailed"
    try:
        response = requests.get(url, timeout = 5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("That location does not exist!")
        sys.exit(1)
    return response

def get_content(response):
    content = BeautifulSoup(response.content, "html.parser")
    return content

def get_data(content):
    table = content.find('tbody')
    return table

def get_temp(table, type):
    row = table.findAll('tr')[1]
    if(type == 'max'):
        temp = row.select("td")[0].text.replace("º", " Degrees Celsius")
    else:
        temp = row.select("td")[1].text.replace("º", " Degrees Celsius")
    temp = temp.strip('\n')
    return temp

def get_condition_array(table):
    condition = []
    for i in range(9, 15, 2):
        row = table.findAll('tr')[i]
        details = row.find("td", attrs = {'class' : 'weather'})
        condition.append(details.find('p').text.split('\n')[2])
    for j in range(0, 3, 1):
        condition[j] = regex.sub('', condition[j]).title()
    return condition

def get_morning(condition):
    return condition[0]

def get_afternoon(condition):
    return condition[1]

def get_evening(condition):
    return condition[2]

def get_sun(table, type):
    row = table.findAll('tr')[14]
    data = row.select("td")[0]
    sun = ""
    if(type == 'sunrise'):
        sun = data.find("dd", attrs = {'class' : 'sun-up'}).text
    else:
        sun = data.find("dd", attrs = {'class' : 'sun-down'}).text
    sun = sun.strip('\n')
    return sun

def get_wind(table):
    row = table.findAll('tr')[4]
    wind = row.select("td")[0].text
    wind = wind.strip('\n').replace(' ', '')
    return wind

def get_precipitation(table):
    row = table.findAll('tr')[6]
    precipitation = row.select("td")[0].text
    precipitation = precipitation.strip('\n').replace(' ', '')
    return precipitation

def get_rain(table):
    row = table.findAll('tr')[0]
    rain = row.find("td", attrs = {'class' : 'rain'}).text.split('\n')[1].replace(' ', '')
    return rain


location = input("Please Enter Your Location: ").replace(' ', '-')
response = get_basic_response(location)
basic_content = get_content(response)
basic_table = get_data(basic_content)
condition = get_condition_array(basic_table)

detailed = get_detailed_response(location)
detailed_content = get_content(detailed)
detailed_table = get_data(detailed_content)

class Weather:

    def __init__(self):
        self.location = location.title()
        self.max_temp = get_temp(basic_table, "max")
        self.min_temp = get_temp(basic_table, "min")
        self.morning = get_morning(condition)
        self.afternoon = get_afternoon(condition)
        self.evening = get_evening(condition)
        self.sunrise = get_sun(basic_table, "sunrise")
        self.sunset = get_sun(basic_table, "sunset")
        self.wind = get_wind(basic_table)
        self.precipitation = get_precipitation(basic_table)
        self.rain_chance = get_rain(detailed_table)
        """
        self.humidity = get_humidity()
        self.pressure = get_pressure()
        self.visibility = get_visibility()
        self.air_quality_index = get_air_index()
        self.air_quality = get_air_quality()
        self.uv_index = get_uv_index()
        """

def main():

    print("\n----- SISMOS Weather Forecasting -----")
    print("----- Developed by Callum Taylor -----")
    print("----- MEng Software Engineering -----")
    print("----- Heriot Watt University -----\n")

    weather = Weather()

    print("~ Location: " + weather.location)
    print("~ Maximum Temperature: " + weather.max_temp)
    print("~ Minimum Temperature: " + weather.min_temp)
    print("~ 08:00 - 14:00 Conditions: " + weather.morning)
    print("~ 14:00 - 20:00 Conditions: " + weather.afternoon)
    print("~ 20:00 - 06:00 Conditions: " + weather.evening)
    print("~ Sunrise Time: " + weather.sunrise)
    print("~ Sunset Time: " + weather.sunset)
    print("~ Average Wind Speed: " + weather.wind)
    print("~ Precipitation: " + weather.precipitation)
    print("~ Chance of Rain: " + weather.rain_chance)


main()
