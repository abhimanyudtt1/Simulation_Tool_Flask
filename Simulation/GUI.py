from flask import Flask,render_template,request,json,redirect,url_for
import time
import thread
from logger import log
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
class importer(object):
    def __init__(self):
        pass
    def setattributes(self,x):
        for i in x :
            setattr(self,i,x[i])

importer = importer()






#GLOBALS

THREAD_ID = 0


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/deploy")
def deploy():
    return render_template('login.html')

@app.route('/checkforlogin',methods= ['POST'])
def a_function():
    log.info( request.form)
    if request.form['username'] == 'Test' and request.form['password'] == 'Test@123':
        return redirect(url_for('deploy2',messages = {'State':'True'}) )
    else :
        return "Invalid Access"

@app.route('/deployonProd',methods= ['POST'])
def deployOnProd():
    component = request.form['Component']
    branch = request.form['branch']
    import subprocess
    (stdout,stderr) = subprocess.Popen('sh ./branch_merge.sh %s %s' % (component,branch),stderr=subprocess.PIPE,stdout=subprocess.PIPE,shell=True).communicate()
    stdout = stdout.split('\n')
    stderr = stderr.split('\n')
    data = {'stdout':stdout,'stderr':stderr}
    return render_template('deploymentResult.html',data=data)


@app.route("/tripSimulationScreen")
def tripSimulationScreen():
    return render_template('tripSimulationScreen.html')



@app.route("/CurrentSimulationStatus")
def CurrentSimulationStatus():
    import subprocess
    data = {}
    (stdout,stderr) = subprocess.Popen('ls ./Thread_Status',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()
    for each in stdout.split('\n'):
        (inner_stdout, inner_stderr) = subprocess.Popen('cat ./Thread_Status/%s'% each, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True).communicate()
        data['%s' % each] = inner_stdout

    return render_template('CurrentSimulationStatus.html',data=data)
@app.route("/tripSimulation",methods = ['POST'])
def tripSimulation():
    importer.setattributes(request.form)
    import simulator
    if not hasattr(importer,'tripId'):
        import simulator
    if not hasattr(importer,'random'):
        setattr(importer,'random',None)
    if not hasattr(importer,'eta'):
        setattr(importer,'eta',None)
    log.info( request.form)
    global THREAD_ID
    log.info( "ASDFFADSFASD : %s " % THREAD_ID)
    THREAD_ID += 1
    tripid = simulator.DriverTripAllocation(importer.driverIds, importer.routeIds, 0,importer.optionsRadios,importer.eta)
    setattr(importer,'tripId',tripid)
    if not hasattr(importer, 'oldTrip'):
        thread.start_new_thread(simulator.startSimulation,(importer.driverIds,importer.routeIds,importer.tripId,importer.time,importer.optionsRadios),
                                {'frequency':importer.frequency,'random':importer.random,'thread':"Driver-%s_Route-%s_Env-%s_%s"
                                                                    % (importer.driverIds, importer.routeIds,importer.optionsRadios,THREAD_ID)})
    else :
        thread.start_new_thread(simulator.startSimulation,(importer.driverIds, importer.routeIds, importer.tripId, 0,
                                  importer.optionsRadios),{'oldTrip':importer.oldTrip,'random':importer.random,
                                                           'thread':"Driver-%s_Route-%s_Env-%s_%s"
                                                                    % (importer.driverIds, importer.routeIds,importer.optionsRadios,THREAD_ID)})
    return redirect('/')


@app.route('/deploy2')
def deploy2():
    if request.args['messages'] :
        return render_template('deploy.html')
    else :
        return "Invalid Access"

@app.route('/SimulateTripCreationForDriver',methods = ['GET','POST'])
def SimulateTripCreateForDriver():
        return render_template('SimulateTripCreationForDriver.html')

@app.route('/runDriverSimulation',methods=['POST'])
def runDriverSimulation():
    driverIds = request.form['driverIds']
    RouteIds = request.form['routeIds']
    time = request.form['Time']
    env = request.form['optionsRadios']
    if not 'eta' in request.form.keys():
        eta = None
    else:
        eta = request.form['eta']
    import simulator
    if True :
        tripid = {}
        driverIds = driverIds.split(',')
        static_time = int(time)
        for driverId in driverIds:
            tripid[driverId] = simulator.DriverTripAllocation(driverId, RouteIds, int(time),env,eta)
            time = int(time) + static_time
        return render_template('result.html', result=[RouteIds, tripid])

    #return "%s" % request.form
    #return render_template('index.html')

if __name__ == "__main__":

    app.run(host = '0.0.0.0',debug=True)