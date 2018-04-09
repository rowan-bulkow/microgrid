from bs4 import BeautifulSoup
import requests
import re

# takes 2 arrays of 3 elements each: day, month, year
# returns the wunderground custom history page that corresponds
# to the given date range
def get_url(begin_date, end_date):
    return 'https://www.wunderground.com/history/airport/PAOM/{0}/{1}/{2}/'\
        'CustomHistory.html?dayend={3}&monthend={4}&yearend={5}'\
        .format(begin_date[2], begin_date[1], begin_date[0],
            end_date[0], end_date[1], end_date[2])

months = {
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}

def get_month(s):
    if s == 'Jan':
        return 1
    elif s == 'Feb':
        return 2
    elif s == 'Mar':
        return 3
    return -1

# TODO make these dynamic - take them as arguments?
begin = [1, 1, 2017]
end = [1, 2, 2017]

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
            currMonth = get_month(child.td.string)
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
