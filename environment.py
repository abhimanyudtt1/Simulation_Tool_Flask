class environment(object):
    class qa :
        dbIp = '52.76.84.56'
        dbUser = 'stage'
        dbPassword = 'shuttl'
        redisIp = '172.31.21.237'
        redisPort = 5000
        rmsDB = '52.76.84.56'
        vmsServer='http://52.221.226.192:8080/service/vms/'
        driverServer='http://qa-driverapi.goplus.in/shuttl/'

    class docker :
        dbIp = '172.31.16.88'
        dbUser = 'stage'
        dbPassword = 'shuttl'
        redisIp = '172.31.16.88'
        redisPort = '32805'
        rmsDB = '52.76.84.56'
        vmsServer = 'http://172.31.16.88:32773/service/vms/'
        driverServer = 'http://172.31.16.88:32789/shuttl/'

    class prod :
        dbIp = '172.31.31.17'
        dbUser = 'ad1214IU'
        dbPassword = 'm0WJFjUXxK7vDA=='
        redisIp = '172.31.21.237'
        rmsDB = '172.31.31.17'
        redisPort = 5000
        vmsServer = 'http://52.221.226.192:8080/service/vms/'
        driverServer = 'http://qa-driverapi.goplus.in/shuttl/'

    def getEnv(self,env):
        return getattr(self,str(env).lower())



environment = environment()
