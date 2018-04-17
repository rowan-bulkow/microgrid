import mysql.connector
from mysql.connector import errorcode

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
