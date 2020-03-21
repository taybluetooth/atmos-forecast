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


def get_query(location):
    arr = []
    link_arr = []
    url = "https://www.forecast.co.uk/s?l=" + location
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    content = BeautifulSoup(response.content, "html.parser")
    list = content.find("ol")

    if(len(list.findAll('li')) > 1):
        for i in range(0, len(list.findAll('li')), 1):
            item = list.findAll('li')[i]
            link = item.find('a')['href']
            arr.append(item.text.strip('\n'))
            link_arr.append(link)
            print("~ " + str(i + 1) + ". " + arr[i])

        print("\nThere's quite a few " + location.title() + "'s!\n")
        choice = int(input("~ Enter the number of the one you meant: "))
        while(not(choice >= 0 and choice < len(link_arr))):
            choice = int(input("~ Please enter a valid choice: "))
        location = link_arr[choice - 1]

    return location


def get_basic_response(location):
    city = get_query(location)
    url = "https://www.forecast.co.uk" + city
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("~ That location does not exist!")
        sys.exit(1)
    return response


def get_detailed_response(location):
    url = "https://www.forecast.co.uk/" + location + ".html?v=detailed"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("~ That location does not exist!")
        sys.exit(1)
    return response


def get_content(response):
    content = BeautifulSoup(response.content, "html.parser")
    return content


def get_data(content):
    table = content.find('tbody')
    return table


def get_location(content):
    location = content.find("meta", attrs={"name": "locality"})['content']
    return location


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
        details = row.find("td", attrs={'class': 'weather'})
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
        sun = data.find("dd", attrs={'class': 'sun-up'}).text
    else:
        sun = data.find("dd", attrs={'class': 'sun-down'}).text
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
    rain = row.find("td", attrs={'class': 'rain'}
                    ).text.split('\n')[1].replace(' ', '')
    return rain


def get_uv_index(table):
    row = table.findAll('tr')[2]
    uv = row.find("td", attrs={'class': 'uv'}).text.split(
        '\n')[1].replace(' ', '')
    return uv


def get_cloudiness(table):
    row = table.findAll('tr')[1]
    cloud = row.find("td").text.split('\n')[1].replace(' ', '')
    return cloud


print("\n----- SISMOS Weather Forecasting -----")
print("----- Developed by Callum Taylor -----")
print("----- MEng Software Engineering -----")
print("----- Heriot Watt University -----\n")

location = input("~ Please Enter Your Location: ").replace(' ', '-')
response = get_basic_response(location)
basic_content = get_content(response)
basic_table = get_data(basic_content)
condition = get_condition_array(basic_table)

detailed = get_detailed_response(location)
detailed_content = get_content(detailed)
detailed_table = get_data(detailed_content)


class Weather:

    def __init__(self):
        self.location = get_location(basic_content)
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
        self.uv_index = get_uv_index(detailed_table)
        self.cloudiness = get_cloudiness(detailed_table)


def main():

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
    print("~ UV Radiation: " + weather.uv_index)
    print("~ Cloudiness: " + weather.cloudiness)


main()
