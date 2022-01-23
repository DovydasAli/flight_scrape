from bs4 import BeautifulSoup
import requests
import re
import csv
import datetime
import time
import logging

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1
#
# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig(filename="logfilename.log", level=logging.DEBUG)
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = False

today = datetime.date.today()
ten_days_from_now = today + datetime.timedelta(days=10)
twenty_days_from_now = today + datetime.timedelta(days=20)
seven_days_from_ten = ten_days_from_now + datetime.timedelta(days=7)
seven_days_from_twenty = twenty_days_from_now + datetime.timedelta(days=7)

post_page = "https://www.fly540.com/flights/index.php?option=com_travel"

pattern_request_ids = re.compile(r'([0-9]{6})(.*?)([0-9]{6})')  # regex to find airport code
pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"0\")')

# print(ten_days_from_now)
# print(seven_days_from_ten)
# print(twenty_days_from_now)
# print(seven_days_from_twenty)

website_ten = requests.get(
    f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
    f'{ten_days_from_now.strftime("%a")}%2C+{ten_days_from_now.strftime("%#d")}+{ten_days_from_now.strftime("%b")}+'
    f'{ten_days_from_now.strftime("%Y")}&date_to={seven_days_from_ten.strftime("%a")}%2C+{seven_days_from_ten.strftime("%#d")}'
    f'+{seven_days_from_ten.strftime("%b")}+{seven_days_from_ten.strftime("%Y")}'
    f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text

website_twenty = requests.get(
    f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
    f'{twenty_days_from_now.strftime("%a")}%2C+{twenty_days_from_now.strftime("%#d")}+{twenty_days_from_now.strftime("%b")}+'
    f'{twenty_days_from_now.strftime("%Y")}&date_to={seven_days_from_twenty.strftime("%a")}%2C+{seven_days_from_twenty.strftime("%#d")}'
    f'+{seven_days_from_twenty.strftime("%b")}+{seven_days_from_twenty.strftime("%Y")}'
    f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text

websites = [website_ten, website_twenty]


def payload_info(website):  # function to get info from flight round trip detail page
    outbound_solution_ids = []
    outbound_solution_cabin_class = []
    inbound_solution_ids = []
    inbound_solution_cabin_class = []

    flight_page = BeautifulSoup(website, 'html.parser')
    departure_block = flight_page.find('div', class_='fly5-flights fly5-depart th')  # find departure details
    return_block = flight_page.find('div', class_='fly5-flights fly5-return th')  # find arrival details
    results_outbound = departure_block.find_all("div", class_="fly5-result")
    results_inbound = return_block.find_all("div", class_="fly5-result")
    pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"0\")')
    for result_outbound in results_outbound:  # iterate over outbound results
        try:
            # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
            # payload['outbound_cabin_class'] = "0"
            outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
            outbound_solution_cabin_class.append("0")
        except AttributeError:  # if there it doesn't find the cheapest, changes to the next cheapest one
            pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"1\")')
            # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
            # payload['outbound_cabin_class'] = "1"
            outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
            outbound_solution_cabin_class.append("1")
    for result_inbound in results_inbound:  # iterate over inbound results
        try:
            # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
            # payload['outbound_cabin_class'] = "0"
            inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
            inbound_solution_cabin_class.append("0")
        except AttributeError:  # if it doesn't find the cheapest, changes to the next cheapest one
            pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data\-cabin\-class\=\"1\")')
            # payload['outbound_solution_id'] = pattern_cheapest_flight_code.search(str(result_outbound)).group(1)
            # payload['outbound_cabin_class'] = "1"
            inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
            inbound_solution_cabin_class.append("1")

    return outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, inbound_solution_cabin_class

def flight_information(page):
    outbound_departure_airport = []
    outbound_arrival_airport = []
    outbound_departure_time = []
    outbound_arrival_time = []

    page_html = BeautifulSoup(page, 'html.parser')
    pattern_airport_code = re.compile(r'([(][A-Z]{3}[)])')  # regex to find airport code
    pattern_time = re.compile(r'(\d+[:]\d+\w{2}).*?(\w{3}\s\d+[,]\s[A-z]+)')  # regex to find time and date of departure or arrival
    website_post_form = flight_page.find('form', id="book-form")  # finds website form details
    request_ids_block = website_post_form.find('input', id="outbound_request_id")  # finds outbound and inbound request ids
    block_departure = flight_page.find('div', class_='fly5-flights fly5-depart th')  # find departure details
    block_return = flight_page.find('div', class_='fly5-flights fly5-return th')  # find arrival details
    outbound_solution = flight_page.find('div', id="flt0417-0")

    results_outbound_departure = block_departure.find_all("div", class_="fly5-result")
    results_inbound_departure = block_return.find_all("div", class_="fly5-result")

    for result in results_outbound_departure:  # iterates over the gotten outbound results
        iteration = 0
        for match in pattern_airport_code.finditer(result.text):
            if (iteration % 2) == 0:
                # extract words
                outbound_departure_airport.append(match.group(1))
            else:
                outbound_arrival_airport.append(match.group(1))
            iteration += 1
        for match in pattern_time.finditer(result.text):
            if (iteration % 2) == 0:
                # extract words
                outbound_departure_time.append(match.group(1) + " " + (match.group(2)))
            else:
                outbound_arrival_time.append(match.group(1) + " " + (match.group(2)))
            iteration += 1
    outbound_departure_airport.append(pattern_airport_code.search(result.text).group(0))
    outbound_arrival_airport.append(pattern_airport_code.search(result.text).group(1))
    print(result)
    outbound_departure_time.append(pattern_time.search(result.text).group(0))
    outbound_arrival_time.append(pattern_time.search(result.text).group(1))

for website in websites:

    flight_page = BeautifulSoup(website, 'html.parser')
    website_post_form = flight_page.find('form', id="book-form")  # finds website form details
    request_ids_block = website_post_form.find('input',
                                               id="outbound_request_id")  # finds outbound and inbound request ids
    outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, inbound_solution_cabin_class = payload_info(
        website)  # Assign returned lists

    payload = {'option': 'com_travel',
               'task': 'airbook.addPassengers',
               'outbound_request_id': '',
               'inbound_request_id': '',
               'outbound_solution_id': '',
               'outbound_cabin_class': '',
               'inbound_solution_id': '',
               'inbound_cabin_class': '',
               'adults': '1',
               'children': '0',
               'infants': '0',
               'change_flight': ''}

    iteration = 0

    payload['outbound_request_id'] = pattern_request_ids.search(str(request_ids_block)).group(1)
    payload['inbound_request_id'] = pattern_request_ids.search(str(request_ids_block)).group(3)

    for outbound_solution in outbound_solution_ids:
        payload['outbound_solution_id'] = outbound_solution
        payload['outbound_cabin_class'] = outbound_solution_cabin_class[iteration]
        for inbound_solution in inbound_solution_ids:
            payload['inbound_solution_id'] = inbound_solution
            payload['inbound_cabin_class'] = inbound_solution_cabin_class[iteration]
            flight_detail_page = requests.post(post_page, data=payload).text
            # flight_information(flight_detail_page)
            print(flight_detail_page)
            break
        iteration += 1






# for x in range(2):
#     flight_page = BeautifulSoup(website, 'html.parser')
#     website_post_form = flight_page.find('form', id="book-form")  # finds website form details
#     request_ids_block = website_post_form.find('input', id="outbound_request_id")  # finds outbound and inbound request ids
#     departure_block = flight_page.find('div', class_='fly5-flights fly5-depart th')  # find departure details
#     return_block = flight_page.find('div', class_='fly5-flights fly5-return th')  # find arrival details
#     outbound_solution = flight_page.find('div', id="flt0417-0")
#     results_outbound_departure = departure_block.find_all("div", class_="fly5-result")
#     results_inbound_departure = return_block.find_all("div", class_="fly5-result")
#
#     print(departure_block)
#     time.sleep(60)
#
#     payload = {'option': 'com_travel',
#                'task': 'airbook.addPassengers',
#                'outbound_request_id': '',
#                'inbound_request_id': '',
#                'outbound_solution_id': 'NjFlOTU0MGNlOGZiNzE2NDI2ODEzNTY=',
#                'outbound_cabin_class': '0',
#                'inbound_solution_id': 'NjFlOTU0MGU4NzdhZTE2NDI2ODEzNTg=',
#                'inbound_cabin_class': '0',
#                'adults': '1',
#                'children': '0',
#                'infants': '0',
#                'change_flight': ''}
#
#     payload['outbound_request_id'] = pattern_request_ids.search(str(request_ids_block)).group(1)
#     payload['inbound_request_id'] = pattern_request_ids.search(str(request_ids_block)).group(3)
#
#     print(payload)
#     # for data in request_ids_block:
#     #     payload['outbound_request_id'] = pattern_request_ids.search(data.text).group(1)
#     #     payload['inbound_request_id'] = pattern_request_ids.search(data.text).group(3)
#     # print(payload)
#     # flight_detail_page = requests.post(post_page, data=payload).text  # turns page into text
#     # soup = BeautifulSoup(flight_detail_page, 'html.parser')
#
#     website = requests.get(
#         f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
#         f'{twenty_days_from_now.strftime("%a")}%2C+{twenty_days_from_now.strftime("%#d")}+{twenty_days_from_now.strftime("%b")}+'
#         f'{twenty_days_from_now.strftime("%Y")}&date_to={seven_days_from_twenty.strftime("%a")}%2C+{seven_days_from_twenty.strftime("%#d")}'
#         f'+{seven_days_from_twenty.strftime("%b")}+{seven_days_from_twenty.strftime("%Y")}'
#         f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text



# pattern_airport_code = re.compile(r'([(][A-Z]{3}[)])')  # regex to find airport code
# pattern_time = re.compile(r'(\d+[:]\d+\w{2}).*?(\w{3}\s\d+[,]\s[A-z]+)')  # regex to find time and date of departure or arrival
# pattern_test = re.compile(r'([(][A-Z]{3}[)])(\d+[:]\d+\w{2}).*?(\w{3}\s\d+[,]\s[A-z]+)')
#

# block_return = soup.find('div', class_='fly5-flights fly5-return th')  # find arrival details
#
# results_outbound_departure = block_departure.find_all("div", class_="fly5-result")
# results_inbound_departure = block_return.find_all("div", class_="fly5-result")

# for result in results_outbound_departure:  # iterates over the gotten outbound results
#     iteration = 0
#     for match in pattern_airport_code.finditer(result.text):
#         if (iteration % 2) == 0:
#             # extract words
#             outbound_departure_airport.append(match.group(1))
#         else:
#             outbound_arrival_airport.append(match.group(1))
#         iteration += 1
#     for match in pattern_time.finditer(result.text):
#         if (iteration % 2) == 0:
#             # extract words
#             outbound_departure_time.append(match.group(1) + " " + (match.group(2)))
#         else:
#             outbound_arrival_time.append(match.group(1) + " " + (match.group(2)))
#         iteration += 1
# outbound_departure_airport.append(pattern_airport_code.search(result.text).group(0))
# outbound_arrival_airport.append(pattern_airport_code.search(result.text).group(1))
# print(result)
# outbound_departure_time.append(pattern_time.search(result.text).group(0))
# outbound_arrival_time.append(pattern_time.search(result.text).group(1))


# print(outbound_departure_airport)
# print(outbound_arrival_airport)
# print(outbound_departure_time)
# print(outbound_arrival_time)


# block_departure_results = soup.find_all('div', class_='fly5-result fly5-result-0')  #find arrival details
# print(block_departure_results)

# block_arrival = block_return.find_all('div', class_='fly5-flights fly5-return th')  #find arrival details

# print(block_departure)

# for block in block_departure:
#     # block_outbound_departure_airport = block_departure.find_all('span', class_='flfrom')  #find outbound departure airport code in page
#     outbound_departure_airport.append(pattern_airport_code.search(block.text))

# block_outbound_departure_airport = soup.find_all('span', class_='flfrom')  #find outbound departure airport code in page

# for airport_code in block_outbound_departure_airport:
#     outbound_departure_airport.append(pattern_airport_code.search(airport_code.text).group(0))

# for x in outbound_departure_airport:
#     print(x)
#
# print(outbound_departure_airport)

# departure_results = ["Numeris1", "Numeris2", "Numeris3"]
# return_results = ["Numeris1_inbound", "Numeris2_inbound", "Numeris3_inbound"]
#
# test = {"numeris1": "Nbo", "numeris2": "MBO"}

# x = {}

# for k, v in test.items():
#     print(v)
#     result_final

# writing to csv file

# outbound_departure_time = [comma.replace(',', '') for comma in outbound_departure_time]  # panaikina tarpus listo objektuose
# outbound_arrival_time = [comma.replace(',', '') for comma in outbound_arrival_time]  # panaikina tarpus listo objektuose
#
# rows = zip(outbound_departure_airport, outbound_arrival_airport, outbound_departure_time, outbound_arrival_time)
#
# with open('list_final.csv', mode='a', newline='', encoding="utf-8") as csvfile:
#     spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#
#     data = list(rows)
#     for row in data:
#         row = list(row)
#         spamwriter.writerow(row)
