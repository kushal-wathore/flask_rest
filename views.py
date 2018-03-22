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
from flask_rest import app
import subprocess
import time
import urllib
import zipfile


#IMAGE_DIR = "/usr/src/app/object_detection/test_images/"
#IMAGE_DIR = "/home/mahadev/application/models/research/object_detection/test_images/"
IMAGE_DIR = "/home/mahadev/test/"

def unzip(path):

	with zipfile.ZipFile(path,"r") as zip_ref:
		zip_ref.extractall(IMAGE_DIR)
	
	return "\""+path+"\" was unzipped successfully."


def run_command(cmd, timeout=120):
	"""given shell command, returns communication tuple of stdout and stderr"""
	try:
		stdout = str()
		stderr = str()
		proc = subprocess.Popen(cmd,shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)

		stdout, stderr = proc.communicate(timeout)
	except subprocess.TimeoutExpired:
		proc.kill()
		stdout, stderr = proc.communicate(timeout)
	return stdout, stderr

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/v1/CreateContainer", methods=["POST"])
def v1_create_container():
	pprint.pprint(request.data)
	pprint.pprint(request.json)
	container_cmd = 'docker run -d --name ' + str(request.json['ContainerName']) + ' ' +  str(request.json['ImageName'])
	pprint.pprint(container_cmd)
	stdout,stderr = run_command(container_cmd)
	pprint.pprint(stdout)
	return jsonify(status=True)

def _create_container(container_name, image_name, port ,target_port):
	container_cmd = 'docker run -d  ' + '-p '+ str(target_port) +':' + str(port) +' --name ' + str(container_name) + ' ' +  str(image_name)
	pprint.pprint(container_cmd)
	stdout,stderr = run_command(container_cmd)
	print("stdout",stdout)
	print("stderr",stderr)
	if stderr:
		return False

	return True

def _python_application(app_path, version, workdir, cmd, envs):
	docker_contents = {}
	requirment_flag = False
	pprint.pprint("requirment_flag_flase")
	print(app_path)
	if not os.path.isfile((app_path)+ '/' + 'requirements.txt'):
		python_dependancy_cmd  = 'pipreqs ' + str(app_path)
		stdout,stderr = run_command(python_dependancy_cmd)
		if ("Successfully saved requirements" in str(stderr)) or ("already exists" in str(stderr)):
			requirment_flag = True
			
	if os.path.isfile((app_path)+ '/' + 'requirements.txt') or requirment_flag:
		pprint.pprint("requirment_flag_true")
		docker_contents['image'] = {"name": "python", "version": version}
		docker_contents['copy'] = [{"src": ".", "dst": "/usr/src/app/"}]
		docker_contents['workdir'] = "/usr/src/app/"
		docker_contents['run'] = [{"command": "pip install -r", "args": ["requirements.txt"]},
								  {"command": "workdir","args": ["/usr/src/app/"+ str(workdir)]}]

		docker_contents['cmd'] = [{"command": "python"+str(version),"args": [str(cmd)]}]
		if envs:
			env_list = []
			for env in envs:
				envname = str(env).split(' ')[0]
				envvalue = str(env).split(' ')[1]
				env_list.append({'envname': envname, 'envvalue': envvalue})
				
			docker_contents['env'] = env_list

	pprint.pprint(docker_contents)

	return docker_contents
	
	
@app.route("/v1/CreateDockerFile", methods=["POST"])
def v1_create_docker_file():
	docker_contents = {}
	pprint.pprint(request.json)
	pprint.pprint("Docker file creation.....")
	path = None
	envs = []
	app_name = request.json['AppName']
	app_path = IMAGE_DIR + app_name

	docker_file_path = "Dockerfile"
	if str(request.json['AppPlatform']).lower() == 'python':
		version = request.json['Version']
		workdir = request.json['Workdir']
		if workdir==app_name:
			workdir=str()
		elif '/'in workdir:
			indexOfslash=workdir.index('/')+1
			workdir=workdir[indexOfslash:]
						
		env = request.json['EnvironmentVariables']
		if len(str(env)) != 0:
			envs =  str(env).split(',') 

		cmd = request.json['Command']
		docker_contents = _python_application(app_path, version, workdir, cmd, envs)
		if not bool(docker_contents):
			return jsonify(status=False, path=path)

	path = (app_path)+'/'+docker_file_path
	pprint.pprint(path)
	pprint.pprint(docker_contents)

	if os.path.isfile(path):
		return jsonify(status=True, path=path)
		
	
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
								if not (str(run['command']) == 'workdir'):
									f.write('RUN ' + str(run['command']) + " " + " ".join(run['args']) + '\n')
								else:
									f.write(('WORKDIR ' ) + " ".join(run['args']) + '\n')
						else:
								f.write('RUN ' + str(run['command']) + '\n')
		if docker_contents.get('env'):
				for env_num in range (0, len(docker_contents['env'])):
						env = docker_contents['env'][env_num]
						f.write('ENV ' + env['envname'] + ' ' + env['envvalue'] + '\n')
		if docker_contents.get('expose'):
				for expose_port in docker_contents.get('expose'):
						f.write('EXPOSE ' + str(expose_port) + '\n')
		if docker_contents.get('cmd'):
			for cmd_num in range (0, len(docker_contents['cmd'])):
				cmd = docker_contents['cmd'][cmd_num]
				f.write('CMD ' + str(cmd['command']) + " " + " ".join(cmd['args']) + '\n')
				#f.write('CMD ' + docker_contents['cmd']['command'] + ',' + ','.join(docker_contents['cmd']['args']) + ']' + '\n')

		f.close()

	return jsonify(status=True, path=path)

@app.route("/v1/CreateImage", methods=["POST"])
def v1_create_image():
	pprint.pprint(request.data)
	pprint.pprint(request.json)
	AppName = request.json['AppName']
	#app_path = str(request.json['AppPath'])
	app_path = IMAGE_DIR + AppName
	docker_image_cmd = 'docker build -t ' + str(request.json['ImageName']) + ' ' + app_path
	pprint.pprint(docker_image_cmd)
	stdout, stderr = run_command(docker_image_cmd)
	print("stdout", stdout)
	print("stderr", stderr)
	if not stderr:
		print("Docker image created successfully, You can check with \"docker images\" command.")
		return jsonify(status=True)

	pprint.pprint(stdout)
	return jsonify(status=False)

@app.route("/v1/Run", methods=["POST"])
def v1_run():
	port = str(request.json['Port'])
	if str(request.json['Deployment']).lower() == "docker":
		container_name = str(request.json['ContainerName'])
		image_name = str(request.json['ImageName'])
		target_port = str(request.json['TargetPort'])
		
	status = _create_container(container_name, image_name, port,target_port)
	
	return jsonify(status=status)
		
		

@app.route("/v1/UploadApp", methods=["POST"])
def v1_upload_app():
	app_path = None
	dir_present = False
	files = request.files.getlist('file')
	pprint.pprint(files)
	for file in files:
		save_path = os.path.join(IMAGE_DIR, file.filename)
		pprint.pprint(save_path)
		file.save(save_path)
	pprint.pprint(save_path)
	if not os.path.isfile(save_path): 
		return jsonify(status=False, app_path=app_path)
		
	unzipResult = unzip(save_path)
	pprint.pprint(unzipResult )

	file_name = str(file.filename)
	index_of_dot = file_name.index('.')
	file_name_without_extension = file_name[:index_of_dot]
	
	app_path = os.path.join(IMAGE_DIR, file_name_without_extension)
	print ("app_path")
	print (app_path)
	print ("file_name_without_extension")
	print (file_name_without_extension)
	dir_cmd = 'find ' +  app_path + ' -maxdepth 1 -mindepth 1 -type d'
	print("dir_cmd")
	print(dir_cmd)
	stdout, stderr = run_command(dir_cmd)
	print("stdout", stdout)
	print("stderr", stderr)
	print(len((stdout)))
	if stderr:
		return jsonify(status=False, app_path=app_path)
	if len((stdout)) != 0:
		dir_present = True


	if not dir_present:
		directory = app_path + '/' + file_name_without_extension
		print ("directory")
		print (directory)
		os.mkdir(directory)
		mv_cmd = 'find ' + app_path + ' -type f | xargs -i mv {} ' + directory 
		print("cmd")
		print(mv_cmd)
		stdout, stderr = run_command(mv_cmd)
		print("stdout", stdout)
		print("stderr", stderr)
		if stderr:
			return jsonify(status=False, app_path=app_path)

	return jsonify(status=True, app_path=app_path)

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

