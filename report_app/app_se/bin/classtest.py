import os
import configparser
import subprocess
import time
import argparse, sys
import operator
import psutil
import datetime
import lxml.html
import csv
import getpass
import gc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from lxml.cssselect import CSSSelector
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from PIL import Image

class Driver(object):	

	def __del__(self):

		print("Del in driver")
		print("status: " + str(self.status).lower())
		
		self.driver.quit()
		self.display.stop()

	def GetSelf(self):

		return str(self)

	def FindKids(self):

		# Useless func since it will always find only one kid of object within the runtime.
		# Almost impossible for it to find more than one only if additional object invoked directly

		self.KidCount = 0
		
		for obj in gc.get_objects():
				
			if isinstance(obj, Driver):
		
				self.Log("Instance check: " + str(obj))
				self.KidCount+=1

	def ProcessKiller(self):

		# Kills other processes with names given
		# Currently disabled by _FindKids since Time is also running..
		# Need to find a way to manage the processes better

		self.names = ['Xephyr','chrome','chromedriver','xvfb']
		#self.ress = []

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
				self.Log("Killed: {0}".format(pid))
				global ress
				
		def killer(f, name):
			
			ress = f(name)

			if not ress:
				
				self.Log("Killing done")
				return 0
			
			else:
				
				pid = ress.pop(0)
				kill(pid)
				time.sleep(0.5)
				return killer(f, name) 

		for name in self.names:
			
			killer(search, name)

	def ReadConfig(self):

		self.Config = configparser.RawConfigParser()
		self.Config.optionxform = str 

		self.MyLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		self.Config.read(os.path.join(self.MyLocation, 'config'))
		self.ConfigDict = {}

		self.Debug = getattr(self, 'Debug', self.Config['Misc']['Debug'] if self.LookUpProperty('Debug') else False )

		for section in self.Config.sections():		
			
			self.ConfigDict[section] = {}
			
			for item in list(self.Config[section].items()):
				
				self.ConfigDict[section][item[0]] = item[1]
		
	def LookUpProperty(self, property):

		res = False
		
		for section in self.Config.sections():	
			res = True if property in self.Config[section] else 0
		return res

	def ReadArgs(self):

		self.args = self.input_args
		self.Debug = self.input_args.Debug
		print("Debug: " + str(self.Debug))
		self.Log("Arguments: "  + str(self.args))

	def SetAttrs(self):


		self.MyLocationRoot = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
		self.WebRoot		= os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..' , '..', 'web'))
		self.DirName 		= 'res'

		self.OptionsList = []
		
		for secton in self.Config.sections():
		
			for key in dict(self.Config.items(secton)):
				
				self.OptionsList.append(key)

		self.Log("Options: " + str(self.OptionsList))

		for option in self.OptionsList:
			
			self.Log("----- " + str(option) + " -----")
			
			try:
				res  = getattr(getattr(self, 'args') , option)
				
				if res is not None:
					self.Log("[&&]: " + str(res))
					setattr(self, option, getattr(getattr(self, 'args') , option))
				else:

					self.Log("[&&]: None in args")
					raise AttributeError


			except AttributeError as e:
				
				self.Log("[**]: Config lookup")

				try:

					for section in self.ConfigDict:

						if option in self.ConfigDict[section]:

							self.Log("[++]: " + str(section))
							setattr(self, option, self.ConfigDict[section][option])
						
						else:

							self.Log("[--]: " + str(section))
						
				except KeyError as e:

					print("This should never happen: " + str(option) + " " + str(section))
					quit()

	def StartDriver(self):

		self.options = Options()
		self.options.add_argument('--disable-dev-shm-usage')
		self.options.add_argument('--no-sandbox')
		self.options.add_argument('--disable-gpu')	
		self.options.add_argument('--disable-extensions')
		
		self.Log("User: " + str(getpass.getuser()))
		self.ShowEnv()

		try:

			self.display = Display(visible=int(self.EnableDisplay), size=(self.XSize, self.YSize))
			time.sleep(0.5)

			self.display.start()
			self.driver = webdriver.Chrome(chrome_options=self.options)
		
			self.driver.set_window_position(self.XPos, self.YPos)
			self.driver.set_window_size(self.XSize,self.YSize)
		
			time.sleep(0.5)
			
			self.driver.implicitly_wait(5)
			self.driver.get('http://google.com')
		
		except Exception as e:

			print("----- Unable to start driver ----")
			print("Err: " + str(e))
			self.status = "FAILED"
			self.__del__()

	def Log(self,input):

		# Some values will be not displayed as there is still no self-Debug,
		# it appears after readconfig

		try:

			if self.Debug:

				out = str("[" + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "] " + str(input))
				print(out)

			else:
				
				pass

		except AttributeError as e:
			
			pass

		except ValueError as e:

			pass
	
	def ShowEnv(self):
		
		self.Log("Effective group id: " + str(os.getegid()))
		self.Log("Effective user id: " + str(os.geteuid()))
		self.Log("Real group id: " + str(os.getgid()))
		self.Log("List of supplemental group ids: " + str(os.getgroups()))

		for param in os.environ.keys():
			self.Log ("%20s %s" % (param,os.environ[param]))

	def CleanUp(self):

		# TO DO: Automate with logic of removing everything not related to needed opts

		del self.args
		del self.Config
		del self.ConfigDict
		del self.OptionsList
		del self.options
		
		if hasattr(self, 'names'):
			del self.names		

	def __init__(self,input_args):

		self.status = 'STARTED'
		self.input_args = input_args

		try:

			# Reading config
			self.Log("Reading config")
			self.ReadConfig()

			# Kill kill kill
			self.Log("Killing")

			self.FindKids()
			
			if self.KidCount > 1:
				# To do something like task handler..?
				pass
				self.Log('Kill : Kids > 1')
				self.ProcessKiller()

			else:

				self.Log("Mercy")
			
			self.Log("Reading Args")
			# Read args
			self.ReadArgs()

			self.Log("Setting Attrs")
			# Set attributes
			self.SetAttrs()

			# Start browser
			self.Log("Starting browser")
			self.StartDriver()
			
			self.Log("PIDs: " + 
				str([[p.name(), p.pid] for p in psutil.Process(self.driver.service.process.pid).children(recursive = True)]))
			
			# Cleanup values
			self.Log("Clean up")
			self.CleanUp()

			self.status = 'SUCCESS'

		except Exception as e:
			
			print("------ Main Exception Handler ------")
			
			print("Error: "  + str(e))

			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			
			print("Where: ", exc_type, fname, exc_tb.tb_lineno)
			self.status = 'FAILED'

			#self.__del__()
			
			print("------ Main Exception Handler ------")

class OktaReport(Driver):
	
	def Log(self, input):
		
		super(OktaReport, self).Log(input)

	def GetToday(self):
		
		return str(datetime.date.today().strftime('%m/%d/%Y').replace("/0", "/"))

	def GetAuthCode(self):

			self.Log("Getting AuthCode")
			
			try:

				p = subprocess.run(['oathtool','--base32','--totp', self.SecretKey,'-d 6'], stdout=subprocess.PIPE)
				self.AuthCode = p.stdout.decode().rstrip()

			except subprocess.CalledProcessError as e:
				
				print("Oath error: " + str(e))
				self.__del__()
	
	def LoginToOkta(self):

			self.driver.get("https://esri.okta.com/")	
			time.sleep(5)

			# User-password
			self.Log("Logging in as: " + str(self.OktaLogin))
			self.driver.find_element_by_id("okta-signin-username").clear()
			self.driver.find_element_by_id("okta-signin-username").send_keys(self.OktaLogin)
			self.driver.find_element_by_id("okta-signin-password").clear()
			self.driver.find_element_by_id("okta-signin-password").send_keys(self.OktaPassword)
			self.driver.find_element_by_id("okta-signin-submit").click()

			## WinAuth
			time.sleep(4)
			elems = self.driver.find_elements_by_css_selector('[id^="input"]')
			elems[0].send_keys(self.AuthCode)

			# Verify button
			# Hidden in div so loop and click all
			buttons = self.driver.find_elements_by_class_name("o-form-button-bar")
			
			time.sleep(1)
			for button in buttons:
				button.click()

			print("Login successful")

	def SwitchFromLighting(self):

		time.sleep(5)
		profilepic  = self.driver.find_element_by_xpath('//*[@id="oneHeader"]/div[2]/span/ul/li[9]/button/div/span[1]/div')
		profilepic.click()
		time.sleep(1.5)
		self.driver.find_element_by_css_selector('div.profile-card-footer > a').click()
		self.driver.get(self.ReportUrl)
		self.lighting = True

	def SwitchToLighting(self):
		
		time.sleep(1)
		self.driver.find_element_by_xpath('//*[@id="phHeader"]/tbody/tr/td[3]/div/div[3]/div/a[1]').click()

	def LookUpReport(self):

		self.Log("Starting second tab...")
		
		self.driver.execute_script('window.open(" ", "tab2");')
		self.driver.switch_to.window("tab2")
		self.driver.get(self.ReportUrl)
		time.sleep(5)
		self.Log("Title: " + str(self.driver.title))

		try:
		
			light = self.driver.find_element_by_xpath('//*[@id="oneHeader"]/div[3]/div/div[1]/div[1]/div/span')
			self.Log(light.text)
			self.Log("Got header, switching from Lighting")
			self.SwitchFromLighting()
			time.sleep(2)
		
		except Exception  as e:
			
			self.Log("Not lighting")
			pass
		
		self.driver.find_element_by_xpath('//*[@id="ext-comp-1013"]').click()
		time.sleep(2)
		
		self.driver.find_element_by_xpath('//*[@id="ext-comp-1013"]').send_keys(str(self.ReportName))
		time.sleep(2)
		
		reports = self.driver.find_elements_by_xpath("//*[substring(@id,string-length(@id) - 4) = '_NAME']/div[2]/a")
		names   = self.driver.find_elements_by_xpath("//*[substring(@id,string-length(@id) - 4) = '_NAME']/div[2]/a/span")
		self.ReportsList =[]


		if len(reports) == len(names):
			
			for incr in range(0,len(reports)):
				
				self.ReportsList.insert(incr, {'name':str(names[incr].text), 'report':reports[incr]})
		
		else:

			print("Parsing failed!")
			self.__del__()

		self.Log("Reports list: " + str(self.ReportsList))

		print("Parsing successful!")

	def RunReport(self):
		
		'''
		Runs report by name from incoming reports list
		'''
		
		# Waiting is safety 
		time.sleep(1)

		# Looking for and clicking on report
		self.Log("Run report input: " + str(len(self.ReportsList)) + " elements")
		
		for report in self.ReportsList:
			
			self.Log("---")
			self.Log(str(self.ReportsList.index(report)) + "." + str(report['name']))
			self.Log("---")

			if self.ReportName == report['name']:

				self.Log("Target found: " + str(report['name']) + ". Opening")

				time.sleep(0.1)
				report['report'].click()
				time.sleep(1)

				self.Log("Closing Lighting AD")
				
				click_close_layers = self.driver.find_elements_by_class_name("dialogClose")
				self.Log("Found: " + str( len(click_close_layers)) + " elements")

				for layer in click_close_layers:
					self.Log("Clicling: " + str(layer.get_attribute("id")))
					layer.click()
					self.Log("AD closed") if (len(click_close_layers) > 0) else 0
					time.sleep(1)

			else:
				print("Target NOT found: " + str(self.ReportName))
				self.__del__()

		try:

			if self.ReportStartDate is not None:

				self.driver.find_element_by_xpath("//*[@id='sd']").click()
				self.driver.find_element_by_xpath("//*[@id='sd']").clear()
				self.driver.find_element_by_xpath("//*[@id='sd']").send_keys(self.ReportStartDate)
				time.sleep(1)

			if self.ReportFinishDate is not None or self.LastDayToday is not None:

				self.driver.find_element_by_xpath("//*[@id='ed']").click()
				self.driver.find_element_by_xpath("//*[@id='ed']").clear()
				time.sleep(1)

				if self.ReportFinishDate is not None:
					self.Log("Setting finish date")
					self.driver.find_element_by_xpath('//*[@id="ed"]').clear()
					self.driver.find_element_by_xpath('//*[@id="ed"]').send_keys(self.ReportFinishDate)
					time.sleep(1)

				self.Log("HEY")
				self.Log(str(type(self.LastDayToday)))

				self.Log("LastDay: " + str(self.LastDayToday)  +" t: " + str(type(self.LastDayToday)))
				self.Log("HEY")

				if self.LastDayToday == True:

					self.Log("LastDayToday: " + str(self.LastDayToday))
					self.Log("Setting today date!")
					self.driver.find_element_by_xpath("//*[@id='ed']").click()
					self.driver.find_element_by_xpath('//*[@id="ed"]').clear()
					self.driver.find_element_by_xpath('//*[@id="ed"]').send_keys(self.GetToday())	
					time.sleep(1)
		
		except AttributeError as e:

			if str(e) == "'OktaReport' object has no attribute 'LastDayToday'":
			
				self.Log("Aliswel")	
			
			else:
			
				print("Cant find dates!")
				print("Err: " + str(e))

			pass

		# Run
		self.driver.find_element_by_xpath('//*[@id="runMutton"]').click()
		time.sleep(2)

		#Getting source
		sel = CSSSelector('#fchArea > table')
		match = sel(lxml.html.fromstring(self.driver.page_source))[0]
		
		report_status = CSSSelector('#status')(lxml.html.fromstring(self.driver.page_source))[0].text
		self.Log("Report status: " + str(report_status))
		
		self.ReportTable = lxml.html.tostring(match).decode('utf-8')
		self.Log("Looking up finished")

	def SaveToHtml(self,htmlinput,filename):

		self.HtmlOutFileName = filename #"report.html"

		'''
		Saves report from incoming saved hmtl to html
		'''

		dirname = 'res'

		try:

			fh = open(os.path.join(self.MyLocationRoot, self.DirName, self.HtmlOutFileName) , "w+")
			res = fh.write(htmlinput)
			fh2 = open(os.path.join(self.WebRoot, self.DirName, self.HtmlOutFileName) , "w+")
			res2 = fh2.write(htmlinput)

		except IOError as e:

			print("Error saving HTML: " + str(e))
			self.__del__()

		print("HTML written")
		return 0

	def SaveToCsv(self,htmlinput,filename):
		
		'''
		Saves report from incoming saved hmtl to csv
		'''
		self.CsvOutFileName = filename #"report.csv"

		try:

			outfile = open(os.path.join(self.MyLocationRoot, self.DirName , self.CsvOutFileName),"w" , encoding='utf-8-sig')
			outfile2 = open(os.path.join(self.WebRoot, self.DirName , self.CsvOutFileName), "w", encoding='utf-8-sig')
			
			writer = csv.writer(outfile)
			writer2 = csv.writer(outfile2)
			
			tree = BeautifulSoup(htmlinput,"lxml")
			table_tag = tree.select("table")[0]

			tab_data = [[item.text for item in row_data.select("th,td")] for row_data in table_tag.select("tr")]

			for data in tab_data:

				for subdata in data:
					subdata = str(subdata)


			for data in tab_data:
				
				writer.writerow(data)
				writer2.writerow(data)
		
		except IOError as e:

			print("Error writing CSV: "  + str(e))
			self.__del__()

		print("CSV written")

	def CleanUpFinal(self):

		# Get lighting back if we had it...
		if self.lighting == True:
			self.SwitchToLighting()

		del self.ReportTable
		del self.ReportsList

	def __init__(self, input_args):
		
		try:
			print("OktaReport init started")
			super().__init__(input_args)

			self.lighting 		= False
			
			self.Log("Init OktaReport with: " + str(self.__dict__))
			
			self.GetAuthCode()
			self.LoginToOkta()
			self.LookUpReport()
			self.RunReport()
			self.SaveToHtml(self.ReportTable, 'report.html')
			self.SaveToCsv(self.ReportTable, 'report.csv')
			self.CleanUpFinal()
			self.status = "SUCCESS"
		
		except AttributeError as e:
			
			print('--------attribute error------')
			print("Error: " + str(e))
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Where: ", exc_type, fname, exc_tb.tb_lineno)
			print("self: " + str(self))

			print("super: " + str(super().__dict__))

			
			print('--------attribute error end------')

		except Exception as e:

			print("OktaReport Error: " + str(e))
			
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Where", exc_type, fname, exc_tb.tb_lineno)

			print("State: " + str(self.__dict__))

			self.status = "FAILED"
			self.__del__()

class GetWorldTime(Driver):

	def GetTimeTable(self):

		self.TimeTable = self.driver.find_element_by_xpath("/html/body/table[7]")
		print("TimeTable done")

	def SaveToImage(self,inputelement):
		#self.driver.execute_script("arguments[0].scrollIntoView()", inputelement )

		time.sleep(1)

		location = inputelement.location_once_scrolled_into_view
		size = inputelement.size;

		print(location)
		print(size)

		self.driver.save_screenshot(os.path.join(self.WebRoot, self.DirName, 'image_full.png'));

		x = location['x'];
		y = location['y'];
		width = location['x']+size['width'];
		height = location['y']+size['height'];

		height-=13;

		
		print('x : {}, y: {}, width: {}, height: {}'.format(x,y,width,height))

		im = Image.open(os.path.join(self.WebRoot, self.DirName, 'image_full.png'))
		im = im.crop((int(x), int(y), int(width), int(height)))

		size = 4950,2630

		resized = im.resize(size, Image.ANTIALIAS)
		time.sleep(1)

		resized.save(os.path.join(self.WebRoot, self.DirName, 'image.png'))

		print("Image saved")

	def __init__(self,input_args):

		try:
			
			#super(GetWorldTime, self).__init__()
			Driver.__init__(self,input_args)
			
			self.Log("Init GetWorldTime args: " + str(self.__dict__))
			
			self.driver.get('https://www.worldtimezone.com/')
			self.GetTimeTable()
			self.SaveToImage(self.TimeTable)
			self.status = "SUCCESS"

		except Exception as e:

			print("GetWorldTime Error"  + str(e))

			print(str(self.__dict__))

			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

			self.status = "FAILED"

			self.__del__()

class GetLicenceNumber(Driver):

	# IN DEV

	def CheckPing(self):

		hostname = "customersadmin.esri.com"
		response = os.system("ping -c 1 " + hostname)
		# and then check the response...
		print(response)

		if response == 0:
	
			self.pingstatus = True
	
		else:
			self.pingstatus = False

		return self.pingstatus

	def ConnectPulse(self):

			try:

				cmd = os.path.join(self.MyLocation, 'connect_pulse')
				print(cmd)
	
			except subprocess.CalledProcessError as e:

				print("VPN error: " + str(e))
				exit()

	def __init__(self,input_args):

		try:
		
			#super(GetLicenceNumber, self).__init__()
			Driver.__init__(self,input_args)
			self.Log("Init GetLicenceNumber args: " + str(self.__dict__))

			#self.__CheckPing()
			#print(self.pingstatus)

			#self.__ConnectPulse()

			#self.__CheckPing()
			#print(self.pingstatus)

		except Exception as e:
		
			print("GetLicense Error: " + str(e))
			print(str(self.__dict__))
			self.status = "FAILED"
			self.__del__()





def add_bool_arg(parser, name, default=False):
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true')
    group.add_argument('--no-' + name, dest=name, action='store_false')
    parser.set_defaults(**{name:default})

		
extparser=argparse.ArgumentParser()

extparser.add_argument('--Fname' , type=str, help='Okta|Time|Lic')
# OktaFunctions
extparser.add_argument('--ReportName' , type=str, help='Report name')
extparser.add_argument('--ReportStartDate', help='Report start_date: dd/mm/yyyy')
extparser.add_argument('--ReportFinishDate', help='Report finish_date: dd/mm/yyyy')
extparser.add_argument('--LastDayToday', default=False, type=lambda x: (str(x).lower() == 'true'))
extparser.add_argument('--EnableDisplay', default=False, type=lambda x: (str(x).lower() == 'true'))
extparser.add_argument('--Debug', default=False, type=lambda x: (str(x).lower() == 'true'))
#extparser.add_argument('--Debug', type=bool, help='Debug: 1 or 0')

extargs = extparser.parse_args()

print("Args: " + str(extargs))

if extargs.Fname == 'Okta':

	a = OktaReport(extargs)

if extargs.Fname == 'Time':
	pass
	#b = GetWorldTime(extargs)

if extargs.Fname == 'Lic':
	pass
	#c = GetLicenceNumber(extargs)

if extparser.parse_args().Fname not in ['Time','Okta','Lic']:
	print("Fname not defined : {}".format(extparser.parse_args().Fname))