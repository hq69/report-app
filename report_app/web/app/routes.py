from app import app
import os
from os.path import exists
from flask import send_from_directory, render_template, request, url_for, Flask, make_response, current_app  
import datetime
import sys
from shelljob import proc
from flask import Response
import subprocess
from flask import Response
import time
from flask import jsonify
from flask_cors import cross_origin
from datetime import timedelta  
from functools import update_wrapper
import time


# UTULITARY
filename 		   = 'report.csv'
csv_dir_location   = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'res'))
full_file_path     = os.path.join(csv_dir_location,filename)
APP_ROOT 		   = os.path.dirname(os.path.abspath(__file__))
templates_folder   = "templates"

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@app.route('/')

@app.route('/lastrun')
def lastrun():
	with open(os.path.join(APP_ROOT, 'lastrun')) as f:
		res = f.read()
	FINAL_INDEX = "<html><b>{0}</b> <p> Refresh: /refresh </p> <p> Get report html: /get_report </p> <p> Get report csv: /get_report_csv </p> </html".format(res)
	return "{0}".format(res) #FINAL_INDEX

@app.route('/get_report')
def get_report():
	date = datetime.datetime.now().strftime("%Y-%m-%d")
	print(str(date), file=sys.stderr)
	print(csv_dir_location, file=sys.stderr)
	print(full_file_path, file=sys.stderr)
	return send_from_directory(csv_dir_location, 'report.html')

@app.route('/get_report_csv')
def get_csv_report():
	date = datetime.datetime.now().strftime("%Y-%m-%d") 
	print(str(date), file=sys.stderr)
	print(csv_dir_location, file=sys.stderr)
	print(full_file_path, file=sys.stderr)
	return send_from_directory(csv_dir_location, 'report.csv',as_attachment=True,attachment_filename=date+'.csv')

@app.route('/refresh')
def refresh(jsonenabled=False):
	
	ReportName = request.args.get('ReportName')
	ReportStartDate = request.args.get('ReportStartDate')
	ReportFinishDate = request.args.get('ReportFinishDate')
	LastDayToday = request.args.get('LastDayToday')
	EnableDisplay = request.args.get('EnableDisplay')
	Debug = request.args.get('Debug')
	Fname = request.args.get('Fname')
	print("Routes.py Fname: {}".format(Fname))
	print("Routes.py Debug: {}".format(Debug)) 
	
	indirect_launch = 0
	indirect_launch = request.args.get('indirect_launch')

	cmd = ['python3' , '/home/user/report_app/app_se/bin/classtest.py']
	
	if ReportName  not in [None,'null']:
		cmd.append('--ReportName={0}'.format(ReportName.rstrip()))

	if ReportStartDate  not in [None,'null']:
		yyyy,mm,dd = ReportStartDate.split('-')
		ReportStartDate = "{0}/{1}/{2}".format(dd,mm,yyyy)
		cmd.append('--ReportStartDate={0}'.format(ReportStartDate.rstrip()))

	if ReportFinishDate not in [None,'null']:
		yyyy,mm,dd = ReportFinishDate.split('-')
		ReportFinishDate = "{0}/{1}/{2}".format(dd,mm,yyyy)
		cmd.append('--ReportFinishDate={0}'.format(ReportFinishDate.rstrip()))

	cmd.append('--Fname={}'.format(Fname))
	cmd.append('--Debug={}'.format("True")) if Debug == "True" else 0
	cmd.append('--LastDayToday={0}'.format(LastDayToday.rstrip())) if LastDayToday else 0
	cmd.append('--EnableDisplay={0}'.format(EnableDisplay.rstrip())) if EnableDisplay else 0
		
	print("Routes.py final cmd: " + str(cmd))

	g = proc.Group()
	p = g.run(cmd)
	
	def read_process():
		while g.is_pending():
			lines = g.readlines()
			for proc, line in lines:
				yield line.decode()
		resp = Response(read_process(), mimetype= 'text/plain')
		print(resp)
		return resp

	resp = list(read_process())
	print("Routes.py response: " + str(resp))
	
	if jsonenabled:

		return jsonify(output = "{0}".format(str(resp)))


	for element in resp:
		
		resp[resp.index(element)] = element.replace('\n','<br />')
	
	css_url = url_for('static', filename='refresh.css')
	return Response(stream_template('refresh.html', resp=resp, css_url = css_url, indirect_launch = indirect_launch))

@app.route('/background_process')
def background_process():
	
	try:
		lang = request.args.get('proglang', 0, type=str)
		if lang.lower() == 'python':
			resp = jsonify(result='You are wise')
			return resp
		else:
			resp  = jsonify(result='Try again.') 
			return resp
	except Exception as e:
		return str(e)

@app.route('/interactive/')
def interactive():
	css_url = url_for('static', filename='main.css')
	print("CSS: " + str(css_url))
	return render_template('interactive.html',css_url = css_url)

#### JSON FUNCTIONS 
@app.route('/lastrun_json')
def lastrun_json():
	with open(os.path.join(APP_ROOT, 'lastrun')) as f:
		res = f.read()
	FINAL_INDEX = "<html><b>{0}</b> <p> Refresh: /refresh </p> <p> Get report html: /get_report </p> <p> Get report csv: /get_report_csv </p> </html".format(res)
	return jsonify(last_run = "{0}".format(res)) #FINAL_INDEX

@app.route('/refresh_json')
def refresh_json():

	return refresh(jsonenabled=True)