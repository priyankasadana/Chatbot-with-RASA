from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet,AllSlotsReset
import zomatopy
import DataForValidation
import json
import smtplib
import time
import os
import json
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import Message

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"4a60e18c65349da0fcad6f844878a4cd"}
		zomato = zomatopy.initialize_app(config)
		try:
			loc = tracker.get_slot('location')
			print("loc ",loc)
			cuisine = tracker.get_slot('cuisine')
			print("cuisine ",cuisine)
			print("price", tracker.get_slot('price'))

			if tracker.get_slot('price').lower() == "cheap":
				print("inside less than 300")
				price_range_min = 0;
				price_range_max = 300
			elif tracker.get_slot('price').lower() == "mid" :
				print("inside between 300 to 700")
				price_range_min = 301;
				price_range_max = 700
			elif tracker.get_slot('price').lower() == "fine dining" :
				print("greater 700")
				price_range_min = 701
				price_range_max = 10000
			else:
				print("You had to enter from the above three options")
			
			print("price_range_min", price_range_min)
			print("price_range_max", price_range_max)
			
			if str(loc) not in DataForValidation.Tier1 and str(loc) not in DataForValidation.Tier2:
				response = "We do not operate in that area yet"
			else:
				location_detail=zomato.get_location(loc, 1)
				d1 = json.loads(location_detail)
				lat=d1["location_suggestions"][0]["latitude"]
				lon=d1["location_suggestions"][0]["longitude"]
				cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'north indian':50,'south indian':85,'American': 1, 'Mexican': 73}
				results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 100)
				try:
					d = json.loads(results)
				except Exception:
					print ("Exception in loads hence, going with encode")
					result = results.encode('utf8')
					d = json.loads(result)
				response=""
				print("response from zomato", d)
				if d['results_found'] == 0:
					response= "No restaurents found matching given criteria"
				else:
					count = 0
					for restaurant in d['restaurants']:
						if ((restaurant['restaurant']['average_cost_for_two']) >= price_range_min and (restaurant['restaurant']['average_cost_for_two']  <=  price_range_max) and count < 10): 
							count = count + 1;
							response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating'] +"\n"

			dispatcher.utter_message("-----"+response)
			os.environ["EMAIL_CONTENT"] =  str(response)
			return [SlotSet('location',loc)]
			#return [AllSlotsReset()]
		except Exception as e:
			print ("Exception is : ", e)
	
class SendMail(Action):
	def name(self):
		return 'send_mail'

	def run(self, dispatcher, tracker, domain):
		try:
			emailid = tracker.get_slot('emailid')
			print("sending mail to ", emailid)

			smtp = smtplib.SMTP('smtp.gmail.com:587')
			smtp.ehlo()
			smtp.starttls()
			print(smtp.login("tekwanikapil1124", "kapil9tekwani@#$"))

			#Send the mail
			smtp.sendmail("tekwanikapil1124@gmail.com", emailid, os.environ["EMAIL_CONTENT"])
			time.sleep(5)
			print("mail sent")

			return [AllSlotsReset()]
		except Exception as e:
			print ("Exception is : ", e)

class ActionRestarted(Action):
	def name(self):
		return 'action_restarted'
	
	def run(self, dispatcher, tracker, domain):
		return [AllSlotsReset()]

