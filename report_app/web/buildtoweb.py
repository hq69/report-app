#! /usr/bin/python3

import subprocess
import datetime
import pprint

import os
import shutil

def log(data):

	pp = pprint.PrettyPrinter(indent=4)
	now = str(datetime.datetime.now())
	data = pp.pformat(str(data))
	fh = open("/home/user/report_app/web/build.log", "a")
	fh.writelines(now + " : " + data + "\n")
	fh.close()

def get_ip():

	cmd = "ip -4 addr | grep -oP '(?<=inet\s)\d+(\.\d+){3}'"
	get_ip = subprocess.Popen( cmd, stdin=subprocess.PIPE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	res = get_ip.communicate()
	arr = []

	for item in res:
		try:
			arr.append(res[res.index(item)].decode('utf-8'))
		except AttributeError:
			pass

	arr2 = arr[0].split()
	api_ip = arr2[2]

	mystring = "export const API_URL = 'http://%s:81';" % api_ip
	mystring2 = "export const GET_REPORT_URL  = 'http://%s:81';" % api_ip

	fh = open("/home/user/report_app/web/frontend/src/app/env.ts", "w")
	fh.writelines(mystring)
	fh.writelines(mystring2)
	fh.close()
	log("String written: " + mystring)
	log("String written: " + mystring2)

def compileweb():

	cmd = "pushd /home/user/report_app/web/frontend && ng build --output-path=/home/user/report_app/web/nginx/frontend && popd"
	c = subprocess.Popen( cmd, stdin=subprocess.PIPE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash" )
	
#	html_file_dummy = os.path.join('/home/user/report_app/web/nginx/','index.html')
#	shutil.move("/home/user/report_app/web/building.jpg", "/home/user/report_app/web/nginx/building.jpg")

#	html_string_dummy = """

#	<p> I am building... </p>
#        <img src="build.jpg" >
#	"""
#	dummy_handle = open(html_file_dummy, "w")
#	dummy_handle.write(html_string_dummy)


	res2 = c.communicate()
	res2 = list(res2)

	for item in res2:
		try:
			res2[res2.index(item)] = item.decode('utf-8')
		except AttributeError:
			pass

	log(" "  + str(res2))

log("--- STARTED ---")
get_ip()
compileweb()
log("--- DONE ---")
