import optparse
import sys
import MySQLdb
import datetime
import collections
import re
import simulateGPS
import time
from environment import environment
from logger import log
def makeJson(x):
    import json
    return json.dumps(x)


def makeEncoded (x):
    line = ""
    for i in x :
        line += "%s=%s&" % (i,x[i])

    return line
class HEADER(object):
    json_headers = {'content-type': "application/json"
                    }
    url_encoded = { 'content-type': "application/x-www-form-urlencoded"
                    }

# Globals



def getRandomIds(type, Path='./Ids.txt'):
    if type == None:
        raise KeyError('No argument passed')

    FH = open(Path, 'r')
    for line in FH:
        if type in line:
            drivers = line.split('=')[-1]
            drivers = drivers.replace('\s', '')
            drivers = drivers.split(',')
            drivers = map(lambda x: int(x), drivers)
    FH.close()
    from random import randint
    return drivers[randint(0, len(drivers))]



def DriverTripAllocation(driverId, routeId, time,env,eta=None):

    # Set Env
    env = environment.getEnv(env)

    # 0. Delete any existing trip on this driver and route combination

    from redis.sentinel import Sentinel
    import redis

    log.info( env.redisIp)
    log.info( env.redisPort)
    log.info( "Environment : %s " % env)
    if str(env).lower() == 'environment.docker' :
        redisIp = '172.31.16.88'
        redisPort = '32772'
    else :
        r = redis.StrictRedis(host=env.redisIp, port=env.redisPort, db=0)
        redisIp = r.sentinel_master('mymaster')['ip']
        redisPort = r.sentinel_master('mymaster')['port']

    log.info(redisIp)
    log.info( redisPort)
    POOL = redis.ConnectionPool(host=redisIp
                                , port=redisPort, db=0)
    my_server = redis.Redis(connection_pool=POOL)
    my_server.delete('running_driver__%s' % driverId)
    my_server.delete('eta_driver_%s' % driverId)

    db = MySQLdb.connect(host=env.dbIp, user=env.dbUser,
                         passwd=env.dbPassword, db='shuttl')
    cursor = db.cursor()
    cursor.execute("set autocommit = 1")
    cursor.execute('''delete from Trip where driverid = %s;''' % driverId)
    # 1. Check the session of the driver from service portal and assign the routeId to the driver if not already assigned

    import requests
    import json
    log.info( "Fetching Driver Info from DriverBackend")
    response = requests.post(env.vmsServer+'findDriverById', data="{\"id\":%s}" % driverId,
                             headers=HEADER.json_headers).json()
    routes = response["data"]["allowedRoutes"].split(',')
    routes = map(lambda x: int(x), routes)
    routeId = int(routeId)
    log.info( "Routes connected to Driverid %s : %s" % (driverId,routes))
    log.info( "Route on which trip needs to run : %s" % routeId)
    if routeId in routes:
        log.info( "Driver already connected to this route, moving ahead")
    else:
        log.info( "Route not assigned to driver assigning the route")
        routes.append(routeId)
        routes = map(lambda x: str(x), routes)
        payload = {"drivers": [{"id": driverId, "allowedRoute": ",".join(routes)}], "userName": "Himani"}
        payload = makeJson(payload)
        response = requests.post(env.vmsServer+'/updateDriverByAdmin', data=payload,
                                 headers=HEADER.json_headers).json()
        log.info( "Route %s is now connected to DriverId : %s " % (routeId,driverId))

    # 2. Check the session time of the driver and set it according to the trip

    # Checking the driver_reporting_times to check the number of sessions for this driver id

    log.info( "Connecting to DriverBackEnd database")
    db = MySQLdb.connect(host=env.dbIp, user=env.dbUser,
                         passwd=env.dbPassword, db='shuttl')
    cursor = db.cursor()
    log.info( "Finding Driver vehicle and session details")
    cursor.execute('''select identifies from vehicles where driverid = %s;''' % driverId)
    vehicle = cursor.fetchone()[0]
    cursor.execute('''select id from driver_report_times where vehiclenum = '%s';''' % vehicle)
    ids = cursor.fetchmany(20)
    log.info( "Vehicle number: %s " % (vehicle))
    log.info( "Number of sessions : %s" % len(ids))
    temp = []

    for i in ids:
        temp.append(i[0])
    ids = temp[:]
    db = MySQLdb.connect(host=env.rmsDB, user=env.dbUser,
                         passwd=env.dbPassword, db='RMS')
    cursor = db.cursor()
    cursor.execute('''SELECT ID FROM LANDMARKS WHERE ID IN (SELECT LANDMARK_ID FROM ROUTE_STOP_MAPPINGS WHERE ROUTE_ID=%s AND DELETED=0);'''% routeId)
    landmark = cursor.fetchone()[0]

    cursor.execute('''SELECT LATITUDE,LONGITUDE FROM LANDMARKS WHERE ID IN(SELECT LANDMARK_ID FROM ROUTE_STOP_MAPPINGS
        WHERE ROUTE_ID = %s AND DELETED = 0 );''' % routeId)
    lat,lng = cursor.fetchone()
    log.info('lat : %s' % lat)
    log.info('lng : %s' % lng)
    log.info( "First DropPoint for selected route LandmarkId : %s " % landmark)
    # Building the API to set session timings
    payload = []
    counter = -1
    log.info( "Setting session Timings for Driver now")
    for i in sorted(ids):
        counter += 1
        currentTime = datetime.datetime.now()
        currentTime = currentTime.replace(second=0, microsecond=0)
        log.info( "current Time : ")
        log.info(currentTime)
        fromTime = currentTime + datetime.timedelta(minutes=time) - datetime.timedelta(minutes=45) +datetime.timedelta(hours=(0 + 4*counter)) #- datetime.timedelta(hours=5,minutes=30)
        toTime = currentTime +datetime.timedelta(minutes=time)+ datetime.timedelta(minutes=0, hours=3) + datetime.timedelta(hours=(0 + 4*counter)) #- datetime.timedelta(hours=5,minutes=30)
        reportTime = currentTime +datetime.timedelta(minutes=time)+ datetime.timedelta(minutes=(time-2), hours=0) + datetime.timedelta(hours=(0 + 2*counter)) #- datetime.timedelta(hours=5,minutes=30)
        reportTime = str(reportTime)
        payload.append({
            "id": i,
            "from": "%s.000" % str(fromTime).replace(' ','T'),
            "to": "%s.000" % str(toTime).replace(' ','T'),
            "locationId": "%s" % landmark,
            "routeId": "%s" % routeId,
            "reportedTime": "%s.000" % reportTime.replace(' ','T')
        })
        log.info( "Session : %s " % (counter+1))
        log.info( "\tFrom : %s " % str(fromTime).split('.')[0])
        log.info( "\tTo : %s" % str(toTime).split('.')[0])
        log.info( "\tReportTime : %s " % reportTime)
    payload_temp = payload[:]
    payload = {
        "reportTimeDetails" : payload_temp,
        "userName": "Himani"
        }
    log.info( payload)
    payload = makeJson(payload)
    result = requests.post(env.vmsServer+'updateReportingSession', data=payload, headers = HEADER.json_headers).json()
    log.info( result)
    # Add trip to the produced data now - Final Step

    log.info( "Adding Trip")
    url = env.vmsServer+'addTrip'
    startTime = datetime.datetime.now() + datetime.timedelta(minutes=time)
    startTime = startTime.strftime('%s')
    startTime = str(startTime).split('.')[0]
    payload = {"tripId":"0","routeId":routeId,"driverId":driverId,"startTime":startTime,"type":"Extra Trip","bookable":"true"}
    log.info( payload)
    payload = makeJson(payload)
    result = requests.post(url,data= payload,headers = HEADER.json_headers).json()
    log.info( result)
    db = MySQLdb.connect(host=env.dbIp, user=env.dbUser,
                         passwd=env.dbPassword, db='shuttl')
    cursor = db.cursor()
    cursor.execute(
        '''SELECT ID FROM Trip where driverid='%s';''' % driverId)
    tripid = cursor.fetchone()[0]
    # Reselt the reporting flag ( Just in case )

    # Set GPS location to 1st pickup point


    requests.get(env.driverServer+'/updateReportingFlag?driverIds=%s' % driverId)

    payload = "driver_id=%s&lng=%s&accuracy=56.0&provider=gps&lat=%s&language=en" % (driverId,lng,lat)
    response = requests.post(env.driverServer + 'publishGps', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info("Publish GPS response : %s " % response)

    key = my_server.get("eta_driver_%s" % driverId)
    log.info("ETA Driver for %s : %s " % (driverId,key))
    import time as T1
    if eta :
        log.info("ETA creation is enabled. Creating static ETA for trip : %s" % tripid)
        key =  []
        key.append(int(driverId))
        key.append(lat)
        key.append(lng)
        key.append(0)
        now_now_time = int(T1.time())+time*60
        key.append(now_now_time)
        D1 = collections.OrderedDict()
        db = MySQLdb.connect(host=env.rmsDB, user=env.dbUser,
                             passwd=env.dbPassword, db='RMS')
        cursor = db.cursor()
        cursor.execute('''SELECT ID,LATITUDE,LONGITUDE FROM LANDMARKS WHERE ID IN(SELECT LANDMARK_ID FROM ROUTE_STOP_MAPPINGS
                WHERE ROUTE_ID = %s AND DELETED = 0 );''' % routeId)
        all_data = cursor.fetchmany(50000)
        COUNTER = 0
        for id,lat,lng in all_data:
        #    if not COUNTER:
        #        COUNTER += 1
        #    else :
                D1[id] = now_now_time + COUNTER*5
                COUNTER+=1
        key.append(D1)
        key.append(0)
        key.append({})
        key = makeJson(key)
        key = "%s" % key
        key = key.replace(' ','')
        log.info( "Made eta Key : %s" % key)
        my_server.set("eta_driver_%s" % driverId,key)


    return tripid







def optionParser():
    # This will parse the options

    parse = optparse.OptionParser()
    parse.add_option("-t", "--testSuit", dest="type",
                     help="Give the type of simulation to run. DriverTripAllocation|DriverTripAllocationAndSimulation")
    parse.add_option("-d", '--driverId', dest='driver',
                     help='Optional Flag to give a specific driver id')
    parse.add_option('-r', '--route', dest='route',
                     help='Optional Flag to give a specific route id')
    parse.add_option("-t", '--time', dest='time',
                     help='Time in sec(s). The trip will be created for a currentTime with this offset')

    (options, args) = parse.parse_args()

    if not parse.type:
        print "Type of simulation requred"
        parse.print_help()
        sys.exit(127)


    else:
        if 'DriverTripAllocationAndSimulation' in parse.type:
            log.info("Under Construction. Comming soon in version 2.0 :)")
            sys.exit(0)
        if not parse.time:
            print "Mandatory field time missing. Please enter time offset"
            parse.print_help()
            sys.exit(127)

    return (parse.type, parse.driver, parse.route, parse.time)


def main():
    (type, driverId, routeId, time) = optionParser()

    if None in (driverId, routeId, time):
        if driverId == None:
            log.info("No Driver Id specified. Using random driver Id ")
            drivers = getRandomIds('driver')
        elif routeId == None:
            log.info("No Route Id specified. Using random Route Id ")
            route = getRandomIds('route')

    if type.lower() == 'DriverTripAllocation'.lower():
        DriverTripAllocation(driverId, routeId, int(time))



def startSimulation(driverId,routeId,tripId,time,env,oldTrip=None,random=False,frequency=None,thread=None):

    # Set Env
    env = environment.getEnv(env)




    # Find imei SIM details :
    db = MySQLdb.connect(host=env.dbIp, user=env.dbUser,
                         passwd=env.dbPassword, db='shuttl')
    cursor = db.cursor()
    cursor.execute(
        '''SELECT pnumber FROM drivers where id='%s';''' % driverId)
    phone_number = cursor.fetchone()[0]
    cursor.execute('''select sim_no,id from sims where number is NULL limit 1;''')
    simNo, simId = cursor.fetchone()
    # simId = cursor.fetchone()[0]
    log.info("simNo : %s" % simNo)
    cursor.execute('''select imei,model_no from devices where simid = %s;''' % simId)
    imei, modelNo = cursor.fetchone()

    # Sign in the driver
    import requests

    payload = {'driver_id':driverId, 'language':'en', 'appVersion':344}
    payload = makeEncoded(payload)
    response = requests.post(env.driverServer+'getDriverVehiclesDetails',data = payload,headers = HEADER.url_encoded).json()
    log.info("List of Vehicles enlisted :")
    for item in response['data']['vehicleList']:
        log.info('\t%s' % item['vehiclePlateNumber'])
    log.info(response)
    vehicleId = response['data']['vehicleList'][0]['vehicleId']
    driverName = response['data']['name'].split(' ')[0]
    log.info("VehicleId : %s\nDriverName : %s " % ( vehicleId,driverName))
    #print response
    payload = {
        "driverId":driverId,
        "locationId":1006,
        "pingCutOffTime":86
    }
    payload = makeJson(payload)
    response = requests.post(env.driverServer+'getVehicleLocationAndDistance',data=payload,headers = HEADER.json_headers).json()
    log.info("TTTTTTTT : %s " % response)
    log.info("Current Location : %s,%s" %(response['data']['vehicleLocation']['lat'],response['data']['vehicleLocation']['lng']))

    payload = "driver_id=%s&language=en&appVersion=351&" \
              "name=%s&vehicleId=%s&ivrCall=1&imei=%s" %(driverId,driverName,vehicleId,imei)
    response = requests.post(env.driverServer+'driverConfirmationCall',data=payload,headers = HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351&routeId=%s" %(driverId,routeId)
    response = requests.post(env.driverServer + 'getDriverPersonalDetails', data=payload,
                             headers=HEADER.url_encoded).json()

    log.info(response)

    payload = "driver_id=%s&language=en" % driverId
    response = requests.post(env.driverServer + 'getSchedule', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351" % driverId
    response = requests.post(env.driverServer + 'getReportDetails', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351" % driverId
    response = requests.post(env.driverServer + 'reachByCallOfDriver', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)
    payload = "driver_id=%s" % driverId
    response = requests.post(env.driverServer + 'getRouteInformation', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351&routeId=%s" % (driverId,routeId)
    response = requests.post(env.driverServer + 'getAllPickUpPointsForRouteId', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&tripId=%s&appVersion=351" % (driverId,tripId)
    response = requests.post(env.driverServer + 'allowBoarding', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)



    payload = "driver_id=%s&language=en&appVersion=351&routeId=%s" % ( driverId,routeId)
    response = requests.post(env.driverServer + 'getRoutePointsForRoute', data=payload,
                             headers=HEADER.url_encoded).json()

    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351&tripId=%s&routeId=%s" % ( driverId,tripId,routeId)
    response = requests.post(env.driverServer + 'getBookingsForTrip', data=payload,
                             headers=HEADER.url_encoded).json()
    log.info(response)

    payload = "driver_id=%s&language=en&appVersion=351&tripId=%s&startedTime=0&startedLat=0&startedLng=0&="\
              % ( driverId,tripId)
    response = requests.post(env.driverServer + 'storeDriverStartTripTime', data=payload,
                             headers=HEADER.url_encoded).json()


    # Publish GPS to set locations now

    if oldTrip :
        s1 = simulateGPS.simulatorClass('old',routeId,driverId,tripId,env=env,tripId=oldTrip,thread=thread)
        endLat,endLng = s1.startTrip()
    else :
        s1 = simulateGPS.simulatorClass('new',routeId,driverId,tripId,env=env,variation=random,frequency=frequency,thread=thread)
        endLat,endLng = s1.startTrip()
    '''
    endTime = str(datetime.datetime.now()).split('.')[0]
    import time
    endTime = int(time.mktime(time.strptime(endTime, "%Y-%m-%d %H:%M:%S")))
    payload = "driver_id=%s&language=en&appVersion=351&endedTime=%s&tripId=%s" \
              % ( driverId,endTime,tripId)
    response = requests.post(env.driverServer + 'storeDriverEndTripTime', data=payload,
                             headers=HEADER.url_encoded).json()
    print endLat,endLng
    print response
    '''





#startSimulation(1, 86,4256992,15,'QA')
