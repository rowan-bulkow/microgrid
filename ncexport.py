from netCDF4 import Dataset
from dateutil.parser import parse
from dbconnector import getDBCursor

addSource = (
    "INSERT INTO power_sources "
    "(startDate, sourceName, numTime, timeUnits, startTime, numDays, "
    "description, samplingRate, powerUnits, rangeMax, rangeMin, "
    "monthlyMin, monthlyMax, monthlyMean, monthlyStdDev, powerType, "
    "longitude, latitude, placeName, measurementType)"
    "VALUES (%(startDate)s, %(sourceName)s, %(numTime)s, %(timeUnits)s, %(startTime)s, %(numDays)s, "
    "%(description)s, %(samplingRate)s, %(powerUnits)s, %(rangeMax)s, %(rangeMin)s, "
    "%(monthlyMin)s, %(monthlyMax)s, %(monthlyMean)s, %(monthlyStdDev)s, %(powerType)s, "
    "%(longitude)s, %(latitude)s, %(placeName)s, %(measurementType)s)"
)
addTimeValue = (
    "INSERT IGNORE INTO power_time_values "
    "(sourceId, time, value) "
    "VALUES (%(sourceId)s, %(time)s, %(value)s)"
)
addTimeValueBase = 'INSERT IGNORE INTO power_time_values (sourceId, time, value) VALUES '
addDayValue = (
    "INSERT INTO power_day_values "
    "(sourceId, day, dailyMin, dailyMax, dailyMean, dailyStdDev) "
    "VALUES (%(sourceId)s, %(day)s, %(dailyMin)s, %(dailyMax)s, %(dailyMean)s, %(dailyStdDev)s)"
)

def readHeaderData(filename, ncData):
    filenameParts = filename.split('@')
    timeData = ncData.variables['time']
    valueData = ncData.variables['value']
    dailyMinData = ncData.variables['DailyMin']
    dailyMaxData = ncData.variables['DailyMax']
    dailyMeanData = ncData.variables['DailyMean']
    dailyStdDevData = ncData.variables['DailyStdDev']

    sourceData = {
        'startDate': parse(filenameParts[1]),
        'sourceName': filenameParts[0],
        'numTime': len(ncData.dimensions['time']),
        'timeUnits': timeData.units,
        'startTime': valueData.StartTime,
        'numDays': len(ncData.dimensions['days']),
        'description': valueData.description,
        'samplingRate': valueData.SamplingRate,
        'powerUnits': valueData.Units,
        'rangeMax': valueData.RangeMax,
        'rangeMin': valueData.RangeMin,
        'monthlyMin': valueData.MonthlyMin,
        'monthlyMax': valueData.MonthlyMax,
        'monthlyMean': valueData.MonthlyMean,
        'monthlyStdDev': valueData.MonthlyStdDev,
        'powerType': valueData.PowerType,
        'longitude': ncData.Longitude,
        'latitude': ncData.Latitude,
        'placeName': ncData.PlaceName,
        'measurementType': ncData.TypeOfMeasurement
    }
    return sourceData

def readTimeValue(sourceId, ncData, index):
    timeData = ncData.variables['time']
    valueData = ncData.variables['value']

    timeValueData = {
        'sourceId': sourceId,
        'time': timeData[index],
        'value': valueData[index]
    }
    return timeValueData

def readTimeValueRange(sourceId, ncData, index, chunkSize):
    timeData = ncData.variables['time'][index:index+chunkSize]
    valueData = ncData.variables['value'][index:index+chunkSize]

    str = ''
    for i in range(0, len(timeData)):
        str += '({},{},{}),'.format(sourceId, timeData[i], valueData[i])
    return str.strip(',')

def readDayValue(sourceId, ncData, index):
    dailyMinData = ncData.variables['DailyMin']
    dailyMaxData = ncData.variables['DailyMax']
    dailyMeanData = ncData.variables['DailyMean']
    dailyStdDevData = ncData.variables['DailyStdDev']

    dayValueData = {
        'sourceId': sourceId,
        'day': index,
        'dailyMin': dailyMinData[index],
        'dailyMax': dailyMaxData[index],
        'dailyMean': dailyMeanData[index],
        'dailyStdDev': dailyStdDevData[index]
    }
    return dayValueData

def readPowerDataFile(path=None, filename=None):
    if path == None: path = 'data/139_000/'
    if filename == None: filename = 'Nome-RC-FedVab@2014-02-01T000000Z@P1M@PT334F@V0.nc'
    conn, db = getDBCursor()
    chunkSize = 500

    ncData = Dataset(path + filename)

    # Read Source/Header data and create db record
    sourceData = readHeaderData(filename, ncData)
    db.execute(addSource, sourceData)

    # Get id of source record just created
    sourceId = db.lastrowid

    # for each time/value record, read and create db entry
    numTime = len(ncData.dimensions['time'])
    index = 0
    while index < numTime:
        cmd = addTimeValueBase
        cmd += readTimeValueRange(sourceId, ncData, index, chunkSize)
        db.execute(cmd)
        print 'At row {} of {}'.format(index, numTime)
        index += chunkSize

    # for each day record, read and create db entry
    numDays = len(ncData.dimensions['days'])
    for i in range(0, numDays):
        dayValueData = readDayValue(sourceId, ncData, i)
        db.execute(addDayValue, dayValueData)

    # nc file cleanup
    ncData.close()

    # mysql db cleanup
    conn.commit()
    db.close()
    conn.close()

readPowerDataFile('data/', 'Nome-C1-FedIa@2012-02-01T000000Z@P1M@PT424F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2013-01-01T000000Z@P1M@PT374F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2013-02-01T000000Z@P1M@PT395F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2014-01-01T000000Z@P1M@PT968F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2014-02-01T000000Z@P1M@PT667F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2015-01-01T000000Z@P1M@PT671F@V0.nc')
readPowerDataFile('data/', 'Nome-C1-FedIa@2015-02-01T000000Z@P1M@PT665F@V0.nc')
