# Simulation_Tool_Flask
A customised simulator tool for simulating certain events in a web service system 
Use Gunicorn to run a flask app using : /usr/bin/python /usr/bin/gunicorn GUI:app --bind 0.0.0.0:5000 --daemon --log-file simulator.logi --workers 3 --timeout 900 --pid=./pid --log-level=DEBUG

here GUI is the GUI.py file and app is the flask application 

