from dateutil.parser import parse
from dbconnector import getDBCursor

powerConn, powerCursor = getDBCursor()
weatherConn, weatherCursor = getDBCursor()
updateConn, updateCursor = getDBCursor()

powerCursor.execute('select FROM_UNIXTIME(time), value from power_time_values where FROM_UNIXTIME(time)>\'2015-02-28 15:00:00\'')
weatherCursor.execute('select * from nome_city_feeder where date>\'2015-02-28 15:00:00\'')

wRows = weatherCursor.fetchall()
weatherCount = weatherCursor.rowcount
weatherConn.close()
wIndex = 0
sumPower = 0.0
numPower = 0.0
while wIndex < weatherCount:
    powerRows = powerCursor.fetchmany(1000)
    for row in powerRows:
        sumPower += row[1]
        numPower += 1
        if wRows[wIndex][0] < row[0]:
            avg = sumPower / numPower
            updateCursor.execute('update nome_city_feeder set amps={:.02f} where date=\'{}\''.format(avg, wRows[wIndex][0]))
            updateConn.commit()
            sumPower = 0.0
            numPower = 0.0
            print 'Updated day {} out of {}'.format(wIndex, weatherCount)
            wIndex += 1

powerConn.close()
updateConn.close()
