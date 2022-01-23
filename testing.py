from bs4 import BeautifulSoup
import requests
import re
import csv
import datetime
import time
import logging

# print(len("NjFlYzA0NmI0YjAzYTE2NDI4NTc1Nzk="))
# print(len("NjFlOTU0MGNlOGZiNzE2NDI2ODEzNTY="))
# print(len("NjFlOTU0MGU4NzdhZTE2NDI2ODEzNTg="))

# outbound_solution_ids = ['1', '2']
# inbound_solution_ids = ['1', '2', '3']


# for outbound_solution in outbound_solution_ids:
#     payload['outbound_solution_id'] = outbound_solution
#     for inbound_solution in inbound_solution_ids:
#         payload['inbound_solution_id'] = inbound_solution
#         print(payload)


# pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"0\")')

today = datetime.date.today()
ten_days_from_now = today + datetime.timedelta(days=10)
twenty_days_from_now = today + datetime.timedelta(days=20)
seven_days_from_ten = ten_days_from_now + datetime.timedelta(days=7)
seven_days_from_twenty = twenty_days_from_now + datetime.timedelta(days=7)
print(twenty_days_from_now)
print(seven_days_from_twenty)

# website = requests.get(
#     f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
#     f'{twenty_days_from_now.strftime("%a")}%2C+{twenty_days_from_now.strftime("%#d")}+{twenty_days_from_now.strftime("%b")}+'
#     f'{twenty_days_from_now.strftime("%Y")}&date_to={seven_days_from_twenty.strftime("%a")}%2C+{seven_days_from_twenty.strftime("%#d")}'
#     f'+{seven_days_from_twenty.strftime("%b")}+{seven_days_from_twenty.strftime("%Y")}'
#     f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text
#
# flight_page = BeautifulSoup(website, 'html.parser')
# departure_block = flight_page.find('div', class_='fly5-flights fly5-depart th')  # find departure details
# return_block = flight_page.find('div', class_='fly5-flights fly5-return th')  # find arrival details
# results_outbound = departure_block.find_all("div", class_="fly5-result")
# results_inbound = return_block.find_all("div", class_="fly5-result")
# website_ten = requests.get(
#     f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
#     f'{ten_days_from_now.strftime("%a")}%2C+{ten_days_from_now.strftime("%#d")}+{ten_days_from_now.strftime("%b")}+'
#     f'{ten_days_from_now.strftime("%Y")}&date_to={seven_days_from_ten.strftime("%a")}%2C+{seven_days_from_ten.strftime("%#d")}'
#     f'+{seven_days_from_ten.strftime("%b")}+{seven_days_from_ten.strftime("%Y")}'
#     f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text
#
# website_twenty = requests.get(
#     f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
#     f'{twenty_days_from_now.strftime("%a")}%2C+{twenty_days_from_now.strftime("%#d")}+{twenty_days_from_now.strftime("%b")}+'
#     f'{twenty_days_from_now.strftime("%Y")}&date_to={seven_days_from_twenty.strftime("%a")}%2C+{seven_days_from_twenty.strftime("%#d")}'
#     f'+{seven_days_from_twenty.strftime("%b")}+{seven_days_from_twenty.strftime("%Y")}'
#     f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text
#
# websites = [website_ten, website_twenty]
#
#
# def payload_info(website):  # function to get info from flight round trip detail page
#     outbound_solution_ids = []
#     outbound_solution_cabin_class = []
#     inbound_solution_ids = []
#     inbound_solution_cabin_class = []
#
#     flight_page = BeautifulSoup(website, 'html.parser')
#     departure_block = flight_page.find('div', class_='fly5-flights fly5-depart th')  # find departure details
#     return_block = flight_page.find('div', class_='fly5-flights fly5-return th')  # find arrival details
#     results_outbound = departure_block.find_all("div", class_="fly5-result")
#     results_inbound = return_block.find_all("div", class_="fly5-result")
#     pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"0\")')
#     for result_outbound in results_outbound:  # iterate over outbound results
#         try:
#             # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
#             # payload['outbound_cabin_class'] = "0"
#             outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
#             outbound_solution_cabin_class.append("0")
#         except AttributeError:  # if there it doesn't find the cheapest, changes to the next cheapest one
#             pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"1\")')
#             # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
#             # payload['outbound_cabin_class'] = "1"
#             outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
#             outbound_solution_cabin_class.append("1")
#     for result_inbound in results_inbound:  # iterate over inbound results
#         try:
#             # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
#             # payload['outbound_cabin_class'] = "0"
#             inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
#             inbound_solution_cabin_class.append("0")
#         except AttributeError:  # if it doesn't find the cheapest, changes to the next cheapest one
#             pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"1\")')
#             # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
#             # payload['outbound_cabin_class'] = "1"
#             inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
#             inbound_solution_cabin_class.append("1")
#
#     return outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, inbound_solution_cabin_class
#
# for website in websites:
#     outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, inbound_solution_cabin_class = payload_info(website) # Assign returned lists
#
#     payload = {'option': 'com_travel',
#                'task': 'airbook.addPassengers',
#                'outbound_request_id': '',
#                'inbound_request_id': '',
#                'outbound_solution_id': '',
#                'outbound_cabin_class': '',
#                'inbound_solution_id': '',
#                'inbound_cabin_class': '',
#                'adults': '1',
#                'children': '0',
#                'infants': '0',
#                'change_flight': ''}
#
#     iteration = 0
#
#     for outbound_solution in outbound_solution_ids:
#         payload['outbound_solution_id'] = outbound_solution
#         payload['outbound_cabin_class'] = outbound_solution_cabin_class[iteration]
#         for inbound_solution in inbound_solution_ids:
#             payload['inbound_solution_id'] = inbound_solution
#             payload['inbound_cabin_class'] = inbound_solution_cabin_class[iteration]
#             print(payload)
#         iteration += 1

website_ten = requests.get(
    f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
    f'{ten_days_from_now.strftime("%a")}%2C+{ten_days_from_now.strftime("%#d")}+{ten_days_from_now.strftime("%b")}+'
    f'{ten_days_from_now.strftime("%Y")}&date_to={seven_days_from_ten.strftime("%a")}%2C+{seven_days_from_ten.strftime("%#d")}'
    f'+{seven_days_from_ten.strftime("%b")}+{seven_days_from_ten.strftime("%Y")}'
    f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text

print(type(website_ten))
print(website_ten)

flight_page = BeautifulSoup(website_ten, 'html.parser')

print(type(flight_page))
print(flight_page)