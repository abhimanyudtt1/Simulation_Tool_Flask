import MySQLdb
import simulator
db=MySQLdb.connect(host="52.76.84.56", user="stage",
                        passwd="shuttl", db="shuttl")





from datetime import datetime

time = str(datetime.now())

time = time.split('.')[0]

print time


driver = 1
cursor = db.cursor()

cursor.execute('''select identifies from vehicles where driverid = %s;''' % driver)

vehicle =  cursor.fetchone()[0]
print vehicle
cursor.execute('''select id from driver_report_times where vehiclenum = '%s';''' % vehicle)
print cursor.fetchmany(20)


'''
vehicle = r.fetch_row()[0][0]

db.query(select id from driver_report_times where vehiclenum = '%s'; % vehicle)

print db.store_result().fetch_rows()

'''