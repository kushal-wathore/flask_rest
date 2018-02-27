"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request, send_file
import tensorflow#from azure.storage.table import TableService, Entity
import os
import json
#from random import shuffle
import pprint
import os.path
import sys
import os
sys.path.insert(0,'../')
sys.path.insert(1, '../object_detection/')
from object_detection import try_1
from flask_rest import app
import subprocess
import time
import urllib

#IMAGE_DIR = "/usr/src/app/object_detection/test_images/"
IMAGE_DIR = "/home/mahadev/application/models/research/object_detection/test_images/"
def run_command(cmd):
    """given shell command, returns communication tuple of stdout and stderr"""
    return subprocess.Popen(cmd,shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).communicate()
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/v1/upload_image_test", methods=["POST"])
def v1_upload_imagei_():
    pprint.pprint(request.files)
    """
    file = request.files['image1']
    pprint.pprint(file)
    f = os.path.join(os.getcwd(), file.filename )
    file.save(f)
    file = request.files['image2']
    pprint.pprint(file)
    f = os.path.join(os.getcwd(), file.filename )
    file.save(f)
    """
    files = request.files.getlist('images')
    pprint.pprint(files)
    for image in files:
        #print("{}".format( image))
        #f = os.path.join(os.getcwd(), image.filename )
        f = os.path.join(IMAGE_DIR, image.filename )
        image.save(f)
        #newpath =  os.path.join(IMAGE_DIR, image.filename)
	#if not os.path.exists(newpath):
	#	os.makedirs(newpath)
	#	f = os.path.join(os.getcwd(), image.filename )
	#f = os.path.join()
    
    #json = request.form.get('json')

    return "Hello World"
    #return json

@app.route("/v1/CreateContainer", methods=["POST"])
def v1_create_container():
	pprint.pprint(request.data)
	pprint.pprint(request.json)
	container_cmd = 'docker run -d --name ' + str(request.json['ContainerName']) + ' ' +  str(request.json['ImageName'])
	pprint.pprint(container_cmd)
	stdout,stderr = run_command(container_cmd)
	pprint.pprint(stdout)
	return jsonify(status=True)

@app.route("/v1/CreateDockerFile", methods=["POST"])
def v1_create_docker_file():
	pprint.pprint(request.json)
	app_path = str(request.json['AppPath'])
	docker_contents = request.json['DockerContents']
	docker_file_path = "Dockerfile"
	path = os.path.dirname(app_path)+'/'+docker_file_path
	path = '/home/mahadev/application/models/research/object_detection/Dockerfile'
	pprint.pprint(path)
	time.sleep(2)
	file = os.path.isfile(path)
	if file:
		
                return jsonify(path="FROM python:3.6 RUN pip install tensorflow==1.4.0 RUN pip install flask RUN pip install matplotlib RUN pip install pillow COPY ./MlFlask /usr/src/app COPY ./object_detection /usr/src/app WORKDIR /usr/src/app/MlFlask/")
		
	"""
	with open(path, 'w') as f:
        	f.write('FROM '+ docker_contents['image']['name'] + ':' + docker_contents['image']['version'] + '\n')
	        if docker_contents.get('copy'):
                	for cpy_num in range (0, len(docker_contents['copy'])):
                        	cpy = docker_contents['copy'][cpy_num]
                        	f.write('COPY ' + cpy['src'] + ' ' + cpy['dst'] + '\n')
        	if docker_contents.get('workdir'):
                	f.write('WORKDIR ' + docker_contents['workdir'] + '\n')
	        if docker_contents.get('run'):
        	        for run_num in range (0, len(docker_contents['run'])):
                	        run = docker_contents['run'][run_num]
                        	if run.get('args'):
                                	f.write('RUN ' + '[' + str(run['command']) + ',' + ','.join(run['args']) + ']' + '\n')
	                        else:
        	                        f.write('RUN ' + '[' + str(run['command']) +  ']' + '\n')
	        if docker_contents.get('env'):
        	        for env_num in range (0, len(docker_contents['env'])):
                	        env = docker_contents['env'][env_num]
                        	f.write('ENV ' + env['envname'] + '=' + env['envvalue'] + '\n')
	        if docker_contents.get('expose'):
        	        for expose_port in docker_contents.get('expose'):
                	        f.write('EXPOSE ' + str(expose_port) + '\n')
	        if docker_contents.get('cmd'):
        	        f.write('CMD ' + '[' + docker_contents['cmd']['command'] + ',' + ','.join(docker_contents['cmd']['args']) + ']' + '\n')

        	f.close()
	"""
	return jsonify(path=path)

@app.route("/v1/CreateImage", methods=["POST"])
def v1_create_image():
	pprint.pprint(request.data)
	pprint.pprint(request.json)
	app_path = str(request.json['AppPath'])
	docker_image_cmd = 'docker build -t ' + str(request.json['ImageName']) + ' ' + os.path.dirname(app_path)
	pprint.pprint(docker_image_cmd)
	stdout, stderr = run_command(docker_image_cmd)
	if not stderr:
		return jsonify(status=True)
		print("Docker image created successfully, You can check with \"docker images\" command.")
		return "Docker image created successfully, You can check with \"docker images\" command."

	pprint.pprint(stdout)
	return jsonify(status=True)
	return "Image Creation Failed"

@app.route("/v1/UploadApp", methods=["POST"])
def v1_uploa_app():
	time.sleep(2)
	return jsonify(status=True)	

@app.route("/v1/UploadImage", methods=["POST"])
def v1_upload_image():
        pprint.pprint(request.files)
        files = request.files.getlist('image')
        pprint.pprint(files)
        for image in files:
                pprint.pprint(image)
                pprint.pprint(image.filename)
                pprint.pprint(IMAGE_DIR)
                #f = os.path.join(os.getcwd(), image.filename )
                f = os.path.join(IMAGE_DIR, image.filename )
                image.save(f)

        return str(image.filename) + " Uploaded on Path: " + str(IMAGE_DIR)

@app.route("/v1/GetMlResponse", methods=["GET"])
def v1_get_ml_response():
        cur_dir = os.getcwd()
        object_detection = {}
        os.chdir('../object_detection/')
        object_detection = try_1.object_detection_function()
        os.chdir(cur_dir)
        pprint.pprint(object_detection)

        return jsonify(object_detection)

@app.route("/v1/GetMlResponseImage", methods=["GET"])
def v1_get_ml_image_response():
        file_path = IMAGE_DIR + 'parking1.jpg-obj.png'
        for file in os.listdir(IMAGE_DIR):
                if file.endswith('obj.png'):
                        file_path = os.path.join(IMAGE_DIR, file)
        return send_file(file_path, mimetype='image/gif')

