from dbconnector import getDBCursor
import datetime
from selenium import webdriver
import sys

import weatherscrape as scrape

dexterPwsId = 'KAKNOME1'

# helpers for adding data to db
addWeather = (
    "INSERT IGNORE INTO weather "
    "(date, location, temp, dewpoint, humidity, wind, speed, gust, pressure, "
    "precip_rate, precip_accum) "
    "VALUES (%(date)s, %(location)s, %(temp)s, %(dewpoint)s, %(humidity)s, "
    "%(wind)s, %(speed)s, %(gust)s, %(pressure)s, %(precip_rate)s, %(precip_accum)s)"
)

def add_month(year, month, startDay=1):
    conn, db = getDBCursor()
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    # driver.minimize_window()
    day = datetime.date(year, month, startDay)

    while day.month == month:
        success = False
        while not success:
            success = True
            try:
                data = scrape.pws_daily(day, dexterPwsId, driver)
                for datapoint in data:
                    db.execute(addWeather, datapoint)
            except:
                e = sys.exc_info()
                print e
                print 'Trouble scraping & inputting day: {0} for {1}, trying again...'.format(day, dexterPwsId)
                success = False
                conn.rollback()
                driver.quit()
                driver = webdriver.Chrome()
                driver.implicitly_wait(30)
        day = day + datetime.timedelta(days=1)
        conn.commit()

    driver.quit()
    db.close()
    conn.close()

# add_month(2012, 2, 6)

yearsNeeded = [2013, 2014, 2015]
monthsNeeded = [1, 2]
for year in yearsNeeded:
    for month in monthsNeeded:
        add_month(year, month)
