import logging
FORMAT ='%(asctime)s %(message)s'
logging.basicConfig(filename='simulator.log',format=FORMAT)

log = logging.getLogger("simulator.log")
log.setLevel(logging.DEBUG)


