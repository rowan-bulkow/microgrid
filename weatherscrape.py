from bs4 import BeautifulSoup
import requests
import re
import datetime
import string
from selenium import webdriver
from dateutil.parser import parse
import time

months = {
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}
nome_airport_code = 'PAOM'
dexter_pws_id = 'KAKNOME1'
keys = ['date', 'location', 'temp', 'dewpoint', 'humidity', 'wind', 'speed',
    'gust', 'pressure', 'precip_rate', 'precip_accum']


# Example wunderground personal weather station daily history url:
# https://www.wunderground.com/personal-weather-station/dashboard?ID=KAKNOME1#history/s20150104/e20150104/mdaily
def get_pws_daily_url(year, month, day, id):
    datestring = '{0:d}{1:02d}{2:02d}'.format(year, month, day)
    return 'https://www.wunderground.com/personal-weather-station/dashboard?ID={0}#history/s{1}/e{1}/mdaily'\
        .format(id, datestring)

# YET Another version of this scraper, this time for the personal weather station page,
# which required a bit more finagling(spelling?) because the values are loaded via js, so
# requests wasn't handling it well
# Time	Temperature	Dew Point	Humidity	Wind	Speed	Gust	Pressure	Precip. Rate.	Precip. Accum.
# 12:00 AM	5.4 F	0.6 F	80 %	SE	2 mph	3 mph	30.37 in	0 in	0 in
def pws_daily(day, pwsid, driver=None):
    url = get_pws_daily_url(day.year, day.month, day.day, pwsid)
    if driver is None:
        driver = webdriver.Chrome()
    driver.get(url)

    history_html = driver.find_element_by_id('history_table').get_attribute('innerHTML')
    history_table = BeautifulSoup(history_html, 'html.parser')

    data = []
    for row in history_table.tbody.find_all('tr'):
        # this is a little jenky - right now it's just filtering out rows that
        # have any definition for the 'class' attribute, because checking for the
        # class='column-header' value was being troublesome
        if 'class' in row.attrs:
            continue
        datarow = []
        for td in row.find_all('td'):
            if td.span is not None:
                td.span.extract()
            if td.string is None:
                td.string = ''
            # the data is in unicode with a bunch of whitespace, so extract it
            datafield = td.string.encode('ascii', 'ignore')
            datafield = datafield.strip(string.whitespace)
            datafield = datafield.strip('%')
            if datafield == '--' or datafield == 'N/A':
                datafield = ''
            if len(datarow) == 0:
                datestr = day.isoformat()+' '+datafield
                datafield = parse(datestr)
            datarow.append(datafield)
        datarow.insert(1, pwsid)
        data.append(dict(zip(keys,datarow)))

    return data


# Example wunderground daily history url:
# https://www.wunderground.com/history/airport/PAOM/2017/4/15/DailyHistory.html
def get_daily_history_url(year, month, day, airportCode):
    return 'https://www.wunderground.com/history/airport/{0}/{1}/{2}/{3}/DailyHistory.html'\
        .format(airportCode, year, month, day)

# wunderground daily history table format:
# Time (AKDT)	Temp.	Windchill	Dew Point	Humidity	Pressure	Visibility	Wind Dir	Wind Speed	Gust Speed	Precip	Events	Conditions
# 12:53 AM	    26.1 F	    -	     25.0 F	     96%	    29.96 in	10.0 mi	      Calm	       Calm	          -	    N/A	 	        Scattered Clouds
def weather_by_day(day):
    html = requests.get(get_daily_history_url(day.year, day.month, day.day, nome_airport_code)).content
    soup = BeautifulSoup(html, 'html.parser')
    obsTable = soup.select('#obsTable')[0]

    data = []
    for row in obsTable.find_all(class_='no-metars'):
        datarow = []
        datarow.append(day)
        for td in row('td'):
            if td.string is None:
                td = td.span.find(class_='wx-value')
            if td.string is None:
                td.string = ''
            # the data is in unicode with a bunch of whitespace, so extract it
            datafield = td.string.encode('ascii', 'ignore')
            datafield = datafield.strip(string.whitespace)
            datafield = datafield.strip('%')
            if datafield == '-' or datafield == 'N/A':
                datafield = ''
            datarow.append(datafield)
        data.append(datarow)

    return data


# Example wunderground url:
# https://www.wunderground.com/history/airport/PAOM/2017/01/01/CustomHistory.html?dayend=01&monthend=02&yearend=2017
# takes 2 arrays of 3 elements each: day, month, year
# returns the wunderground custom history page that corresponds
# to the given date range
def get_url(begin_date, end_date):
    return 'https://www.wunderground.com/history/airport/PAOM/{0}/{1}/{2}/'\
        'CustomHistory.html?dayend={3}&monthend={4}&yearend={5}'\
        .format(begin_date[2], begin_date[1], begin_date[0],
            end_date[0], end_date[1], end_date[2])

# 'Deprecated' - this gets data from the 'custom history' page, which only gives data per day,
# not per minute or hour like we want
def get_weather_data(begin, end):
    html = requests.get(get_url(begin, end)).content
    soup = BeautifulSoup(html, 'html.parser')
    obsTable = soup.select('#obsTable')[0]

    startYear = begin[2]
    currYear = 0
    currYearIndex = 0
    prevYear = 0
    currMonth = 0
    currMonthIndex = 0
    currDay = 0
    currDayIndex = 0
    newMonth = False

    # wunderground pulls in the form:
    # 2017  Temp  Dew Point  Humidity  Sea Level  Visibility  Wind  Precip  Events
    # Jan {high avg low}, {high avg low}, ...(for wind? ->)high avg high, sum

    # data[year][month][day] = [day, temp_low, temp_avg, ... , events]
    data = []
    datanames = ['day', 'temp_low', 'temp_avg', 'temp_high',
        'dew_low', 'dew_avg', 'dev_high',
        'humid_low', 'humid_avg', 'humid_high',
        'sea_low', 'sea_avg', 'sea_high',
        'vis_low', 'vis_avg', 'vis_high',
        'wind_low', 'wind_avg', 'wind_high',
        'precipitation', 'events']

    for child in obsTable.children:
        # There are apparently some ghost children? not sure why
        if child.name == 'None':
            continue
        elif child.name == 'thead':
            # we're on a new month, get the year
            newMonth = True
            prevYear = currYear
            currYear = int(child.th.string)
            currYearIndex = currYear - startYear
            # if we're on a new year, append a new list
            if prevYear != currYear:
                data.append([])
        elif child.name == 'tbody':
            # each month has essentially two header rows - one is thead and
            # one tbody. all we need from this second is the month
            if newMonth:
                currMonth = months[child.td.string]
                currMonthIndex = currMonth - 1
                currDayIndex = 0
                newMonth = False
                data[currYearIndex].append([])
                continue
            # append a new list for each day
            data[currYearIndex][currMonthIndex].append([])
            col = 0
            for td in child.find_all('td'):
                if td.string is None:
                    td = td.span
                # the data is in unicode with a bunch of whitespace, so extract it
                datafield = td.string.encode('ascii', 'ignore').strip()
                pattern = re.compile(r'\s+')
                datafield = re.sub(pattern, '', datafield)
                # if it isn't the last column, try to parse it to a float
                if col != 20 and datafield is not None:
                    # this isn't awesome, because it's just catching all
                    # exceptions rather than preventing them
                    try:
                        datafield = float(datafield)
                    except:
                        datafield = None
                data[currYearIndex][currMonthIndex][currDayIndex].append(datafield)
                col += 1
            currDayIndex += 1

    return data

# TODO make these dynamic - take them as arguments?
# begin = [1, 1, 2017]
# end = [1, 2, 2017]
# wdata = pws_daily(datetime.date(2017, 1, 1), dexter_pws_id)
# print wdata
