from bs4 import BeautifulSoup
from flask import render_template
from flask import request
from app import app
import requests
import sys
import re
import datetime

@app.route('/basic_req')
def basic_req(city):
    url = "https://www.forecast.co.uk" + city #
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("~ 404 Error - ATMOS Cannot Locate Data")
        sys.exit(1)
    return response

@app.route('/detail_req')
def detail_req(city):
    url = "https://www.forecast.co.uk" + city + "?v=detailed"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("~ 404 Error - ATMOS Cannot Locate Data")
    return response

@app.route('/basic_content')
def basic_content(city):
    return BeautifulSoup(basic_req(city).content, "html.parser")

@app.route('/basic_data')
def basic_data(city):
    return basic_content(city).find('tbody')

@app.route('/detail_content')
def detail_content(city):
    return BeautifulSoup(detail_req(city).content, "html.parser")

@app.route('/detail_data')
def detail_data(city):
    return detail_content(city).find('tbody')

@app.route('/location')
def location(city):
    return basic_content(city).find("meta", attrs={"name": "locality"})['content']

@app.route('/temp')
def temp(city):
    temp = basic_data(city).findAll('tr')[1].select("td")[0].text
    temp = temp.strip('\n')
    return temp

@app.route('/condition')
def condition(city):
    # morning 9
    # afternoon 11
    # evening 13
    regex = re.compile('([^\s\w]|_)+')
    row = basic_data(city).findAll('tr')[9]
    details = row.find("td", attrs={'class': 'weather'})
    condition = details.find('p').text.split('\n')[2].replace('-', '').strip()
    regex.sub('', condition).title()
    return condition

@app.route('/sun')
def sun(city, type):
    row = basic_data(city).findAll('tr')[14].select("td")[0]
    if(type == 'sunrise'):
        sun = row.find("dd", attrs={'class': 'sun-up'}).text
    else:
        sun = row.find("dd", attrs={'class': 'sun-down'}).text
    sun = sun.strip('\n')
    return sun

@app.route('/wind')
def wind(city):
    row = basic_data(city).findAll('tr')[4]
    wind = row.select("td")[0].text
    wind = wind.strip('\n').replace(' ', '')
    return wind

@app.route('/precipitation')
def precipitation(city):
    row = basic_data(city).findAll('tr')[6]
    precipitation = row.select("td")[0].text
    precipitation = precipitation.strip('\n').replace(' ', '')
    return precipitation

@app.route('/rain')
def rain(city):
    row = detail_data(city).findAll('tr')[0]
    rain = row.find("td", attrs={'class': 'rain'}).text.split('\n')[1].replace(' ', '')
    return rain

@app.route('/uv')
def uv(city):
    row = detail_data(city).findAll('tr')[2]
    uv = row.find("td", attrs={'class': 'uv'}).text.split('\n')[1].replace(' ', '')
    return uv

@app.route('/cloudiness')
def cloudiness(city):
    row = detail_data(city).findAll('tr')[1]
    cloud = row.find("td").text.split('\n')[1].replace(' ', '')
    return cloud

@app.route('/icon')
def icon(condition):
    if(condition == "Clear"):
        return "sun"

    elif(condition == "Mostly clear"):
        return "cloud-sun"

    elif(condition == "Overcast"):
        return "cloud"

    elif(condition == "Overcast and light rain"):
        return "cloud-rain"

    elif(condition == "Overcast and showers"):
        return "cloud-showers-heavy"

    elif(condition == "Overcast and rain"):
        return "cloud-showers-heavy"

    elif(condition == "Overcast and light snow"):
        return "snowflake"

    elif(condition == "Overcast and snow"):
        return "snowflake"

    elif(condition == "Overcast and snow showers"):
        return "snowflake"

    elif(condition == "Overcast and wet snow"):
        return "snowflake"

    elif(condition == "Overcast and wet snow showers"):
        return "snowflake"

    elif(condition == "Partly cloudy"):
        return "cloud"

    elif(condition == "Partly cloudy and rain"):
        return "cloud-rain"

    elif(condition == "Partly cloudy and showers"):
        return "cloud-showers-heavy"

    elif(condition == "Partly cloudy and light rain"):
        return "cloud-rain"

    elif(condition == "Partly cloudy and light snow"):
        return "snowflake"

    elif(condition == "Cloudy and light rain"):
        return "cloud-rain"

    elif(condition == "Cloudy"):
        return "cloud"

    elif(condition == "Cloudy and showers"):
        return "cloud-rain"

    elif(condition == "Cloudy and light snow"):
        return "snowflake"

    elif(condition == "Cloudy and wet snow"):
        return "snowflake"

    elif(condition == "Cloudy and wet snow showers"):
        return "snowflake"

    elif(condition == "Cloudy and light wet snow"):
        return "snowflake"

    elif(condition == "Cloudy and snow"):
        return "snowflake"

    elif(condition == "Cloudy and snow showers"):
        return "snowflake"

    elif("possible thunderstorms" in condition):
        return "bolt"



@app.route('/date')
def date():
    x = datetime.datetime.now()
    return x

@app.route('/')
def init():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def query():
    arr = []
    link_arr = []
    location = request.form['text']
    url = "https://www.forecast.co.uk/s?l=" + location
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    content = BeautifulSoup(response.content, "html.parser")
    list = content.find("ol")

    if(list is None):
        return render_template('invalid.html')
    try:
        if(len(list.findAll('li')) > 1):
            for i in range(0, len(list.findAll('li')), 1):
                item = list.findAll('li')[i]
                loc = {
                    'location': str(item.text.strip('\n')),
                    'link': str(item.find('a')['href'])
                }
                arr.append(loc)
        elif(len(list.findAll('li')) == 1):
                return index("/" + location + ".html")
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)

    return render_template('results.html', queries = arr)

@app.route('/index')
def index(text):
    weather = {
        'location': location(text),
        'temp': temp(text),
        'condition': condition(text),
        'sunrise': sun(text, 'sunrise'),
        'sunset': sun(text, 'sunset'),
        'wind': wind(text),
        'precipitation': precipitation(text),
        'rain': rain(text),
        'uv': uv(text),
        'cloudiness': cloudiness(text),
        'icon': icon(condition(text)),
        'date': str(date().day) + "/" + str(date().month) + "/" + str(date().year),
        'day': date().strftime("%A")
    }
    return render_template('weather.html', weather=weather)

@app.route('/results', methods=['POST'])
def results():
    return index(request.form.get('weather'))
