# -*- coding: utf-8 -*-
import os
import signal
import time
import datetime
import subprocess
import lxml.html
import csv
import argparse, sys
import re

from selenium import 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from lxml.cssselect import CSSSelector
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display

######## CORE

def init_main():

	read_agrs()
	chrome_killer()
	
	if DISPLAY == 0:
		display = Display(visible=0, size=(x_size, y_size))
		display.start()

	global driver
	driver = webdriver.Chrome(options=options)
	driver.set_window_position(x_pos, y_pos)
	driver.implicitly_wait(5)
	print("Start_date: " + str(report_start_date))
	print("Finish date: " + str(report_finish_date))
	print("today_checked: " + str(today_checked))
	save_last_run()
	return 0

def set_salesforce_interface(interface):
	global CURRENT_INTERFACE
	CURRENT_INTERFACE = interface
	return CURRENT_INTERFACE

def read_agrs():
	parser=argparse.ArgumentParser()
	parser.add_argument('--start_date', help='report start_date')
	parser.add_argument('--finish_date', help='report finish_date')
	parser.add_argument('--today_checked', type=int, choices=range(0, 2), help='today_checked')
	parser.add_argument('--display', type=int, choices=range(0,2), help='disable display: 1')
	parser.add_argument('--report_name' , type=str, help='report name')
	
	args=parser.parse_args()

	global report_start_date
	report_start_date = args.start_date
	
	global report_finish_date
	report_finish_date = args.finish_date
	
	global today_checked
	today_checked = args.today_checked
	
	
	global DISPLAY
	if args.display is None:
		DISPLAY = 0 
	if args.display == 1:
		DISPLAY = 1

	if args.report_name is not None:
		global report_name
		report_name = args.report_name
		print("Name: " + str(report_name))
	else:
		print("No report name specified. Default: <mytest>")
		report_name = "mytest"
		print("Name: " + str(report_name))

	date_regex = re.compile('^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$')

	if report_start_date is not None:
		if bool(date_regex.match(report_start_date)) is not True:
			print("Start date incorrect: " + str(report_start_date)+".")
			exit()
			if report_finish_date is not None:
				if bool(date_regex.match(report_finish_date)) is not True:
					print("Finish date incorrect")
					exit()
	return 0

def chrome_killer():

	'''
	KIlls all Chrome instances before we launch
	the new test
	HAVE TO HAVE SUDO!!
	'''

	name = 'chrome'
	ress = []

	def search(name):

		p = subprocess.Popen(['pgrep', '-l' , name], stdout=subprocess.PIPE)
		out, err = p.communicate()

		res = []

		for line in out.splitlines():

			line = bytes.decode(line)
			pid = str(int(line.split(None, 1)[0]))
			res.append(pid)
		return res

	def check_if_exists():
		return search(name)

	def kill(pid):
		if (pid.isdigit()):
			cmd = "sudo kill {0}".format(pid)        
			os.system(cmd)
			print("Killed: {0}".format(pid))
			global ress
			
	def killer(f):
		
		ress = f(name)

		if not ress:
			print("Killing done")
			return 0
		else:
			pid = ress.pop(0)
			kill(pid)
			time.sleep(0.5)
			return killer(f) 

	killer(search)

def today():

	'''
	Today separated by slashes 
	'''
	return str(datetime.date.today().strftime('%m/%d/%Y').replace("/0", "/"))

def file_len(fname):

	len_list = 0

	try:
		with open(fname) as f:
			
			for i, l in enumerate(f):
				len_list = len(list(f))
				pass
			
			if len_list > 0:
				print("Len : " + str(len_list + 1))
				return len_list
			else:
				print("Len 0")
				return 0
	except FileNotFoundError as e:
		print("No lastrun file")
		pass

def save_last_run():

	'''
	Saves last run to a file
	'''

	status = RUN_STATUS
	dirname = 'app'

	if file_len(os.path.join(flask_location, dirname, 'lastrun')) > 3:
		fh  = open(os.path.join(flask_location, dirname, 'lastrun') , "w").close()

	try:
		fh  = open(os.path.join(flask_location, dirname, 'lastrun') , "a+")
		res = fh.write(str(datetime.datetime.now().replace(microsecond=0)) + "/" + str(status) + "#\n")
	except IOError as e:
		print(e)
	return 0

def launch_winauth():

	'''
	Launches WinAuth as a subprocess via AutoIt script for Windows
	'''

	print("Launching WinAuth...")
	try:
		subprocess.call(os.path.join(my_location , "open-win_auth.exe"))
		print("Success")
	except subprocess.CalledProcessError as e:
		print("Error launching Winauth..exiting")
		print(e)
		exit()

def read_winauth_code():

	'''
	Reads a code from wiauth_code.txt
	'''

	dirname = 'tmp'
	print("Gettind code")
	try:
		fh = open(os.path.join(my_location_root, dirname, "winauth_code.txt") , "r")
		res = fh.read()
		print("Got code: " + str(res))
		return res
	except FileNotFoundError as e:
		print(e)
		print("No code using fake one...")
		return "123456"

def process_winauth_linux():

	try:

		result = subprocess.run(['oathtool','--base32','--totp', secret_key,'-d 6'], stdout=subprocess.PIPE)
		print("CODE: " + str(result.stdout.decode()).rstrip())
		return str(result.stdout.decode()).rstrip()

	except subprocess.CalledProcessError as e:
		print("Error running oath")
		print(e)
		exit()

def login_to_okta():

	'''

	Logging to OKTA

	'''

	# WinAuth
	if PLATFORM == "WIN":
		launch_winauth()
		winauth_code = read_winauth_code()
	elif PLATFORM == "UNIX":
		winauth_code = process_winauth_linux()
	else:
		print("Error reading auth code..exiting")
		RUN_STATUS = "FAILED"

	# Logging in
	driver.get("https://esri.okta.com/")	
	time.sleep(3)

	# User-password
	print("Logging in as: " + str(okta_login))
	driver.find_element_by_id("okta-signin-username").clear()
	driver.find_element_by_id("okta-signin-username").send_keys(okta_login)
	driver.find_element_by_id("okta-signin-password").clear()
	driver.find_element_by_id("okta-signin-password").send_keys(okta_password)
	driver.find_element_by_id("okta-signin-submit").click()

	## WinAuth
	time.sleep(4)
	elems = driver.find_elements_by_css_selector('[id^="input"]')
	elems[0].send_keys(winauth_code)

	# Verify button
	# Hidden in div so loop and click all
	buttons = driver.find_elements_by_class_name("o-form-button-bar")
	for button in buttons:
		button.click()

	print("Login successful")
	return 0

def parse_okla_buttons():

	'''
	Gets all buttons on OKTA
	'''

	#Replace with EC WAIT! lazy
	time.sleep(10)
	print("Slept.looking for buttons")

	#Finding all buttons and their names on the page
	buttons = driver.find_elements_by_xpath('//*[@id="main-content"]/div/div[2]/ul[2]/li[*]/a')
	names = driver.find_elements_by_xpath('//*[@id="main-content"]/div/div[2]/ul[2]/li[*]/p')	
	
	# Forming array with all buttons on OKLA
	if len(buttons) == len(names):
		res =[]
		for incr in range(0,len(buttons)):
			res.insert(incr, {'name':str(names[incr].get_attribute("oldtitle")), 'button':buttons[incr]})
	else:
		print("Parsing buttons failed. Check Salesforce layout or pray to creator")

	return res if res else 0

def click_okta_button_by_name(buttons, name):

	'''
	Clicks button by a name

	'''

	for button in buttons:
		print("Open: " + str(button['name']))
		if name == button['name']:
			print("Found")
			button['button'].click()

	'''

	for i in range(0,len(buttons)):
		if ('name' == buttons[i]['name'] and i<1):
			buttons[i]['buttton'].click()
			i+=1
		else:
			print("Could not click button: " + str(name))

	'''

def sf_search_report_by_name(name):

	''' 
	Looks up for a report on a salesforce by a name.
	Opens second tab in Chrome using reports_link

	Fills search box with a name we are looking for
	May return more than one report.

	WARNING WORKS WITH OLD INTERFACE

	'''
	
	# Wait a little 
	time.sleep(5)

	
	# Get a new tab with a reports page
	print("Starting second tab...")
	driver.execute_script('window.open(" ", "tab2");')
	driver.switch_to.window("tab2")
	driver.set_window_position(x_pos, y_pos)
	driver.get(reports_link)

	# Looking for a reports and waiting for results to load
	time.sleep(1)

	if CURRENT_INTERFACE == INTERFACE_TYPES[0]:
		time.sleep(0.2)
		driver.find_element_by_xpath('//*[@id="ext-comp-1013"]').click()
		time.sleep(0.2)
		driver.find_element_by_xpath('//*[@id="ext-comp-1013"]').send_keys(str(name))
		time.sleep(1.5)
		reports = driver.find_elements_by_xpath("//*[substring(@id,string-length(@id) - 4) = '_NAME']/div[2]/a")
		names   = driver.find_elements_by_xpath("//*[substring(@id,string-length(@id) - 4) = '_NAME']/div[2]/a/span")

	if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

		time.sleep(5)
		driver.find_element_by_xpath("//*[starts-with(@id, '67:')]").send_keys(str(name))
		time.sleep(3)
		reports = driver.find_elements_by_xpath("//*[@id='split-left']/div/div/div/div[2]/div/div[2]/lightning-datatable/div[2]/div/div/div/table")
		names   = driver.find_elements_by_xpath("//*[@id='split-left']/div/div/div/div[2]/div/div[2]/lightning-datatable/div[2]/div/div/div/table/tbody/tr/th/lightning-primitive-cell-wrapper/div/slot/lightning-primitive-cell-types/lightning-formatted-url/a/span[2]")


	if len(reports) == len(names):

		res =[]
		for incr in range(0,len(reports)):
			res.insert(incr, {'name':str(names[incr].text), 'report':reports[incr]})
	else:

		print("Parsing reports failed. Check Salesforce layout or pray to creator")
		print("Reports list: \n " + "---\n" + str(res) + "\n --- \n")
			
	print("Reports list: \n " + "---\n" + str(res) + "\n --- \n")
	if res != []:
		return res
	else:
		print("No reports found! Quitting.")
		driver.quit()
		quit()

def sf_run_report_by_name(reports, name):
	
	'''
	Runs report by name from incoming reports list
	'''
	
	# Waiting is safety 
	time.sleep(1)

	# Looking for and clicking on report
	print("Run report input: " + str(len(reports)) + " elements")
	
	for report in reports:
		print("---")
		print(str(reports.index(report)) + "." + str(report['name']))
		print("---")

		if name == report['name']:

			print("Target found: " + str(report['name']) + ". Opening")

			if CURRENT_INTERFACE == INTERFACE_TYPES[0]:
				time.sleep(0.1)
				report['report'].click()
				time.sleep(1)

				print("Closing Lighting AD")
				click_close_layers = driver.find_elements_by_class_name("dialogClose")
				print ("Found: " + str( len(click_close_layers)) + " elements")
				for layer in click_close_layers:
					print("Clicling: " + str(layer.get_attribute("id")))
					layer.click()
					print("AD closed") if (len(click_close_layers) > 0) else 0
					time.sleep(1)

			if CURRENT_INTERFACE == INTERFACE_TYPES[1]:
				name_link = report['report'].find_elements_by_xpath("//*[@id='split-left']/div/div/div/div[2]/div/div[2]/lightning-datatable/div[2]/div/div/div/table/tbody/tr/th/lightning-primitive-cell-wrapper/div/slot/lightning-primitive-cell-types/lightning-formatted-url/a/span[2]")
				print("len nm: " + str(len(name_link)))
				for name in name_link:
					print("name: " + str(name))
					name.click()
					print("clicked")

		else:
			print("Target NOT found: " + str(name))
	

	# START DATES
	# TO DO: Add dates for lighing
	if  report_start_date is not None:

		if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

			driver.find_element_by_xpath("//*[contains(@id,'sd')]").click()
			driver.find_element_by_xpath("//*[contains(@id,'sd')]").clear()
			time.sleep(0.5)
			driver.find_element_by_xpath("//*[contains(@id,'sd')]").send_keys(report_start_date)
		
		if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

			pass


	if report_finish_date is not None or today_checked is not None:

		if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

			driver.find_element_by_xpath("//*[contains(@id,'ed')]").click()
			driver.find_element_by_xpath("//*[contains(@id,'ed')]").clear()
			time.sleep(0.5)

			if report_finish_date is not None:

				driver.find_element_by_xpath('//*[@id="ed"]').send_keys(report_finish_date)

			if today_checked is not None:

				driver.find_element_by_xpath('//*[@id="ed"]').clear()
				driver.find_element_by_xpath('//*[@id="ed"]').send_keys(today())	

		if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

			pass
		
	if (report_start_date is not None or report_finish_date is not None or today_checked is not None):

		if CURRENT_INTERFACE == INTERFACE_TYPES[0]:
		
			try:
				driver.find_element_by_xpath('//*[@id="ext-gen66"]').click()
				time.sleep(2)
			except:

				pass

	# Run
	print("Running report:  " +  str(name) + "...")

	if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

		driver.find_element_by_xpath('//*[@id="runMuttonLabel"]').click()
		time.sleep(2)

	if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

		driver.find_element_by_xpath('//*[substring(@id, string-length(@id) - string-length(":0") +1) = ":0"]/div[2]/div/div[2]/div[1]/button[4]').click()

	#Getting source
	result_html = driver.page_source
	tree = lxml.html.fromstring(result_html)
	
	if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

		sel = CSSSelector('#fchArea > table')
		report_res = sel(tree)
		print(str(report_res))

	if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

		table_id = tree.find_class('reportsReportPage')[0].get('id')
		print("Table id: " + str(table_id))
		myxpath = '//*[@id="%s"]/div[3]/div[1]/div/span[2]/table' % table_id
		print(myxpath)
		report_res = tree.xpath(myxpath)
		print(report_res)

	if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

		match = report_res[0]
		report_status = CSSSelector('#status')(tree)[0].text
		print("STATUS : " + str(report_status))
		print("Saving result")
		sf_save_report_to_html((lxml.html.tostring(match)).decode('utf-8'))
		sf_save_report_to_csv((lxml.html.tostring(match)).decode('utf-8'))
		print("Process finished. Results saved.")

	if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

		match = report_res[0]
		sf_save_report_to_html((lxml.html.tostring(match)).decode('utf-8'))
		sf_save_report_to_csv((lxml.html.tostring(match)).decode('utf-8'))
		
		print("Process finished. Results saved.")

def sf_save_report_to_html(result):

	'''
	Saves report from incoming saved hmtl to html
	'''

	dirname = 'res'

	try:

		fh = open(os.path.join(my_location_root, dirname, html_outfile_name) , "w+")
		res = fh.write(result)
		fh2 = open(os.path.join(flask_location, dirname, html_outfile_name) , "w+")
		res2 = fh2.write(result)
		global RUN_STATUS
		RUN_STATUS = "SUCCESS"

	except IOError as e:

		print(e)
		RUN_STATUS = "FAILED"
		exit()

	print("HTML written")
	return 0

def sf_save_report_to_csv(html):

	'''
	Saves report from incoming saved hmtl to csv
	'''

	dirname = 'res'

	try:

		outfile = open(os.path.join(my_location_root, dirname, csv_outfile_name),"w" , encoding='utf-8-sig')
		outfile2 = open(os.path.join(flask_location, dirname, csv_outfile_name), "w", encoding='utf-8-sig')
		
		writer = csv.writer(outfile)
		writer2 = csv.writer(outfile2)
		global RUN_STATUS
		RUN_STATUS = "SUCCESS"
		tree = BeautifulSoup(html,"lxml")
		table_tag = tree.select("table")[0]

		tab_data = [[item.text for item in row_data.select("th,td")] for row_data in table_tag.select("tr")]


		for data in tab_data:

			for subdata in data:
				subdata = str(subdata)#.decode('utf-8')
				print(str(type(subdata)) + str(subdata))
			#tab_data[0][tab_data[0].index(data)] = str(data).decode('utf-8')

		print(tab_data)

		for data in tab_data:
			print('-----')
			print(str(type(data)) + str(data))
		
			writer.writerow(data)
			writer2.writerow(data)
	
	except IOError as e:

		print(e)
		RUN_STATUS = "FAILED"
		exit()

	print("CSV written")

	return 0


# TO DO: read from file
#### CREDS
okta_login = "den96560"
okta_password = "esridenys123!"
secret_key = "GEIMZJOXAS3OZCFK"
####

#### REPORT NAME AND DATES
report_name = None
report_start_date = None
report_finish_date = None
DISPLAY = None

#### UTILITARY
# Chatter : classic, esrisupport classic, lighting - not classic
# Do NOT change the order below

INTERFACE_TYPES = ['chatter', 'lighting', 'esrisupport'] 
CURRENT_INTERFACE = None
set_salesforce_interface(INTERFACE_TYPES[0])
print("Interface :" + str(CURRENT_INTERFACE))


if CURRENT_INTERFACE == INTERFACE_TYPES[0]:

	reports_link = "https://esri.my.salesforce.com/00O/o"

if CURRENT_INTERFACE == INTERFACE_TYPES[1]:

	reports_link = "https://esri.lightning.force.com/lightning/o/Report/home?queryScope=mru"

if CURRENT_INTERFACE == None:

	print("Error: no interface defined")
	quit()

print("Reports_link: " + str(reports_link))


my_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
my_location_root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
flask_location   = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..' , '..', 'web'))
csv_outfile_name = "report.csv"
html_outfile_name = "report.html"
RUN_STATUS = "STARTED"
PLATFORM = "UNIX" # WIN | UNIX
driver = None
nwin_auth_file_name = "winauth_code.txt"

### Chrome options
x_pos = 0 #-32000
y_pos = 0 #-32000 
x_size = 1024
y_size = 768
options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=%d,%d".format(x_size,y_size))
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")


### Init...
init_main()
login_to_okta()
sf_run_report_by_name(sf_search_report_by_name(report_name), report_name)
save_last_run()
driver.quit()
####



