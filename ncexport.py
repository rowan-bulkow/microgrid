import mysql.connector
from mysql.connector import errorcode
from netCDF4 import Dataset
from dateutil.parser import parse

class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)

def getDBCursor():
    # connection details must be changed to specify new dabases
    dbuser = 'root'
    dbpass = 'password'
    dbhost = 'localhost'
    dbdb = 'microgriddb'
    try:
        conn = mysql.connector.connect(user=dbuser, password=dbpass, host=dbhost, database=dbdb)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
          print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
          print("Database does not exist")
        else:
          print(err)
        sys.exit()

    conn.set_converter_class(NumpyMySQLConverter)
    return conn, conn.cursor()

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

    ncData = Dataset(path + filename)

    # Read Source/Header data and create db record
    sourceData = readHeaderData(filename, ncData)
    db.execute(addSource, sourceData)

    # Get id of source record just created
    sourceId = db.lastrowid

    # for each time/value record, read and create db entry
    numTime = len(ncData.dimensions['time'])
    for i in range(0, numTime):
        timeValueData = readTimeValue(sourceId, ncData, i)
        db.execute(addTimeValue, timeValueData)

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

readPowerDataFile()
