from environment import environment
import datetime
import time
import MySQLdb
import requests
import random
from logger import log

class HEADER(object):
    json_headers = {'content-type': "application/json"
                    }
    url_encoded = { 'content-type': "application/x-www-form-urlencoded"
                    }

env = environment.qa
envp = environment.prod

delay = 15
frequency = 1
route = 277
driverId = 11
tripId = 4256988



class simulatorClass(object):
    def __init__(self,type,route,driverId,TripIdForStoppingTrip,env=None,tripId=None,variation=False,frequency = None,thread=None):
        self._thread = thread
        self._TripIdForStoppingTrip = TripIdForStoppingTrip
        self._env = env
        if str(type).lower() == 'new':
            if frequency:
                self._frequency = frequency
            else :
                self._frequency = 2
            self._route = route
            self._driver = driverId
            self._trip = tripId
            self._variation = variation
        elif str(type).lower() == 'old' :
            self._route = route
            self._driver = driverId
            self._trip = tripId

    def startTrip(self):
        # type: () -> object
        if self._trip :
            x = self.runOldTrip()
            self.stopTrip()
            return x
        else:
            x=  self.runNewTrip()
            self.stopTrip()
            return x

    def stopTrip(self):
        endTime = str(datetime.datetime.now()).split('.')[0]
        import time
        endTime = int(time.mktime(time.strptime(endTime, "%Y-%m-%d %H:%M:%S")))
        payload = "driver_id=%s&language=en&appVersion=351&endedTime=%s&tripId=%s" \
                  % (self._driver, endTime, self._TripIdForStoppingTrip)
        response = requests.post(self._env.driverServer + 'storeDriverEndTripTime', data=payload,
                                 headers=HEADER.url_encoded).json()
        log.info(response)

    def runOldTrip(self):
        log.info("Running Old Trip : %s" % self._trip)
        db = MySQLdb.connect(host=environment.prod.dbIp, user=environment.prod.dbUser,
                             passwd=environment.prod.dbPassword, db='shuttl')
        cursor = db.cursor()
        cursor.execute('''select actualStartTime,endTime,driverid from Trip where id = %s;'''% (self._trip))
        (startTime, endTime,oldTripDriver) = cursor.fetchone()

        cursor.execute('''select lat,lng,created_at from gps_histories
                where driverid = %s and
                created_at between FROM_UNIXTIME(%s) and FROM_UNIXTIME(%s) order by created_at;''' % (oldTripDriver,startTime,endTime) )

        gpsCordinates = cursor.fetchmany(10000)
        totalGPS = len(gpsCordinates)
        FIRST_FLAG = 1
        count = 0
        for lat,lng,timestamp in gpsCordinates:
            if FIRST_FLAG == 1 :
                FIRST_FLAG = 0
                payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (self._driver, lng, lat)
                response = requests.post(env.driverServer + 'publishGps', data=payload,
                                         headers=HEADER.url_encoded).json()
                log.info(response)
                log.info(timestamp)
                oldTime = time.mktime(time.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S"))
            else:
                newTime = time.mktime(time.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S"))
                log.info("Sleeping for %s sec(s)" % (newTime-oldTime))
                time.sleep(newTime-oldTime)
                payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (self._driver, lng, lat)
                response = requests.post(env.driverServer + 'publishGps', data=payload,
                                         headers=HEADER.url_encoded).json()
                log.info(response)
                oldTime = newTime
            count += 1
            FH = open('./Thread_Status/%s' % self._thread, 'w')
            FH.write('%s' % float((float(count)/totalGPS)*100))
            FH.close()
        return lat,lng

    def runNewTrip(self):
        log.info("New Trip Simulation :)")
        log.info("self._variation : %s " % self._variation)
        db = MySQLdb.connect(host=environment.prod.dbIp, user=environment.prod.dbUser,
                             passwd=environment.prod.dbPassword, db='RMS')
        cursor = db.cursor()
        cursor.execute('''select LATITUDE,LONGITUDE from ROUTE_POINTS where ROUTE_ID = %s order by id ;''' % route )
        gpsCordinates = cursor.fetchmany(10000)
        totalGPS = len(gpsCordinates)
        count = 0
        if self._variation == True :
            log.info("This is a random test. TIUoooo TIUoooo ")
            for lat, lng in gpsCordinates:
                maxTime =int(random.random()*10)
                for i in range(maxTime):
                    if int(self._frequency) :
                        time.sleep(self._frequency)
                    payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (
                            self._driver, lng, lat)
                    response = requests.post(env.driverServer + 'publishGps', data=payload,
                                             headers=HEADER.url_encoded).json()
                    log.info(response)
                count += 1
                FH = open('./Thread_Status/%s' % self._thread, 'w')
                FH.write('%s' % float((float(count) / totalGPS) * 100))
                FH.close()
        else :
            for lat, lng in gpsCordinates:
                if int(self._frequency) :
                    time.sleep(self._frequency)
                payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (
                    self._driver, lng, lat)
                response = requests.post(env.driverServer + 'publishGps', data=payload,
                                         headers=HEADER.url_encoded).json()
                log.info(response)
                count += 1
                FH = open('./Thread_Status/%s' % self._thread, 'w')
                FH.write('%s' % float((float(count) / totalGPS) * 100))
                FH.close()
        return lat, lng









#s1 = simulatorClass('old',86,1,4256993)

#s1.startTrip()





'''
db = MySQLdb.connect(host=env.dbIp, user=env.dbUser,
                         passwd=env.dbPassword, db='shuttl')
cursor = db.cursor()
cursor.execute(\'''select actualStartTime,endTime from Trip where id = %s;\'''% driverId)
(startTime,endTime,driverId) = cursor.fetchmany(1)


print x


for lat,lng in x :
    for i in range(delay):
        time.sleep(freequency)
        payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (driverId, lng, lat)
        response = requests.post(env.driverServer + 'publishGps', data=payload,
                                 headers=HEADER.url_encoded).json()
        print response

'''