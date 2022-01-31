# used for parsing the websites for easier navigation and finding information with regex
from bs4 import BeautifulSoup
# used for getting the website htmls and sending post request
import requests
# used for finding information on a page
import re
# used for writing csv file
import csv
# used for getting dates
import datetime
# used for log file
import logging

# used for getting requests and posts to page enable to get log file and detailed log in console
# try:
#     import http.client as http_client
# except ImportError:
#     import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1
#
# logging.basicConfig(filename="page_log.log", level=logging.DEBUG)
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = False

# date configuration
# today's date
today = datetime.date.today()
# date ten days from today
ten_days_from_now = today + datetime.timedelta(days=10)
# date twenty days from today
twenty_days_from_now = today + datetime.timedelta(days=20)
# date seven days from ten days from today
seven_days_from_ten = ten_days_from_now + datetime.timedelta(days=7)
# date seven days from twenty days from today
seven_days_from_twenty = twenty_days_from_now + datetime.timedelta(days=7)

# post page where the payload is posted, to gather data
post_page = "https://www.fly540.com/flights/index.php?option=com_travel"

# patterns for regex to find information and add to payload
# regex to find request id
pattern_request_ids = re.compile(r'([0-9]{6})(.*?)([0-9]{6})')
# regex to find cheapest flight code
pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data-cabin-class="0")')

# websites for ten and twenty days from today
website_ten = requests.get(
    f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
    f'{ten_days_from_now.strftime("%a")}%2C+{ten_days_from_now.strftime("%#d")}+{ten_days_from_now.strftime("%b")}+'
    f'{ten_days_from_now.strftime("%Y")}&date_to={seven_days_from_ten.strftime("%a")}%2C+'
    f'{seven_days_from_ten.strftime("%#d")}+{seven_days_from_ten.strftime("%b")}+{seven_days_from_ten.strftime("%Y")}'
    f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text

website_twenty = requests.get(
    f'https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from='
    f'{twenty_days_from_now.strftime("%a")}%2C+{twenty_days_from_now.strftime("%#d")}+'
    f'{twenty_days_from_now.strftime("%b")}+{twenty_days_from_now.strftime("%Y")}&date_to='
    f'{seven_days_from_twenty.strftime("%a")}%2C+{seven_days_from_twenty.strftime("%#d")}+'
    f'{seven_days_from_twenty.strftime("%b")}+{seven_days_from_twenty.strftime("%Y")}'
    f'&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=').text

# website list to iterate trough them both
websites = [website_ten, website_twenty]

# creates initial flight list file and adds header
with open('flight_list.csv', mode='w', newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=';')

    writer.writerow(['outbound_departure_airport', 'outbound_arrival_airport', 'outbound_departure_time',
                     'outbound_arrival_time', 'inbound_departure_airport', 'inbound_arrival_airport',
                     'inbound_departure_time', 'inbound_arrival_time', 'total_price', 'taxes'])


# function to get info from flight round trip detail page
def payload_info(website):
    # lists for info to add to payload
    outbound_solution_ids = []
    outbound_solution_cabin_class = []
    inbound_solution_ids = []
    inbound_solution_cabin_class = []

    # flight page for flights on the selected date configuration
    flight_page = BeautifulSoup(website, 'html.parser')
    # find departure details
    departure_block = flight_page.find('div', class_='fly5-flights fly5-depart th')
    # find arrival details
    return_block = flight_page.find('div', class_='fly5-flights fly5-return th')
    # all outbound flights
    results_outbound = departure_block.find_all("div", class_="fly5-result")
    # all inbound flights
    results_inbound = return_block.find_all("div", class_="fly5-result")
    # pattern for regex to find the cheapest flight code
    pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data-cabin-class="0")')

    for result_outbound in results_outbound:  # iterate over outbound flight results
        try:
            outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
            outbound_solution_cabin_class.append("0")
        except AttributeError:  # if it doesn't find the cheapest flight option, changes to the next cheapest one
            pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data-cabin-class="1")')
            outbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_outbound)).group(1))
            outbound_solution_cabin_class.append("1")
    for result_inbound in results_inbound:  # iterate over inbound flight results
        try:
            inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
            inbound_solution_cabin_class.append("0")
        except AttributeError:  # if it doesn't find the cheapest, changes to the next cheapest one
            pattern_cheapest_flight_code = re.compile(r'([a-zA-Z0-9]{31}[=]).+(data-cabin-class="1")')
            inbound_solution_ids.append(pattern_cheapest_flight_code.search(str(result_inbound)).group(1))
            inbound_solution_cabin_class.append("1")

    # returns info to add to the payload
    return outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, inbound_solution_cabin_class


# function to gather data from the flight details page
def flight_information(page):
    # lists for flight information storing
    outbound_departure_airport = []
    outbound_arrival_airport = []
    outbound_departure_time = []
    outbound_arrival_time = []
    inbound_departure_airport = []
    inbound_arrival_airport = []
    inbound_departure_time = []
    inbound_arrival_time = []
    flight_price = []
    flight_tax = []

    # tax variable for storing the tax for the ticket
    tax_final = 0

    # passes the post page trough html.parser for easier navigation
    page_html = BeautifulSoup(page, 'html.parser')
    # regex to find time and airport code
    pattern_time_airport_code = re.compile(r'([A-z]{3}\s[0-9]+[,]\s[A-z]{3}).*?(\d+[:]\d+\w{2}).*?([A-z]{3}\s[0-9]+'
                                           r'[,]\s[A-z]{3}).*?(\d+[:]\d+\w{2}).*?[frshort"> ]([A-Z]{3}).*?[toshort"> ]'
                                           r'([A-Z]{3})')
    # regex to find overall price for flight
    pattern_flight_price = re.compile(r'(\d+[.]\d+)')
    # find outbound flight detail block in html
    block_outbound_details = page_html.find('div', class_='fly5-fldet fly5-fout')
    # find inbound flight detail block in html
    block_inbound_details = page_html.find('div', class_='fly5-fldet fly5-fin')
    # find flight price block in html
    block_flight_price = page_html.find('span', class_='fly5-price')

    # outbound details
    # adds the outbound information to their lists
    outbound_departure_time.append(pattern_time_airport_code.search(block_outbound_details.text).group(2) + " "
                                   + (pattern_time_airport_code.search(block_outbound_details.text).group(1)))
    outbound_arrival_airport.append(pattern_time_airport_code.search(block_outbound_details.text).group(6))
    outbound_departure_airport.append(pattern_time_airport_code.search(block_outbound_details.text).group(5))
    outbound_arrival_time.append(pattern_time_airport_code.search(block_outbound_details.text).group(4) + " "
                                 + (pattern_time_airport_code.search(block_outbound_details.text).group(3)))

    # inbound details
    # adds the inbound information to their lists
    inbound_departure_time.append(pattern_time_airport_code.search(block_inbound_details.text).group(2) + " "
                                  + (pattern_time_airport_code.search(block_inbound_details.text).group(1)))
    inbound_arrival_airport.append(pattern_time_airport_code.search(block_inbound_details.text).group(6))
    inbound_departure_airport.append(pattern_time_airport_code.search(block_inbound_details.text).group(5))
    inbound_arrival_time.append(pattern_time_airport_code.search(block_inbound_details.text).group(4) + " "
                                + (pattern_time_airport_code.search(block_inbound_details.text).group(3)))

    # flight price
    # adds the flight price to its list
    flight_price.append(pattern_flight_price.search(block_flight_price.text).group(1))

    # flight taxes
    # find tax block in html
    block_taxes = page_html.find_all('div', class_="fly5-bkdown")
    # pattern for regex to find taxes in block_taxes
    pattern_tax = re.compile(r'Tax.*?(\d+[.]\d+)')

    # find all taxes for flight
    taxes = re.findall(pattern_tax, str(block_taxes))

    # iterates over taxes adds them up and adds the final tax to its list
    for tax in taxes:
        tax_final += float(tax)
    flight_tax.append(tax_final)

    # returns all flight information to add to the csv file
    return outbound_departure_airport, outbound_arrival_airport, outbound_departure_time, outbound_arrival_time, \
           inbound_departure_airport, inbound_arrival_airport, inbound_departure_time, inbound_arrival_time, \
           flight_price, flight_tax


# iterates over both websites ten days from now and twenty and writes them to the csv file
for website in websites:
    # main website page to gather some of the information and add it to the payload
    flight_page = BeautifulSoup(website, 'html.parser')
    # finds website form details
    website_post_form = flight_page.find('form', id="book-form")
    # finds flight query info
    block_flight_query = flight_page.find('div', class_="col-md-4 cl-2")
    # finds outbound and inbound request ids
    block_request_ids = website_post_form.find('input', id="outbound_request_id")
    # pattern for regex to find the date for flights
    pattern_flight_date = re.compile(r'[A-z]{3}\s[0-9]+[,]\s[A-z]{3}\s([0-9]+)'
                                     r'.*?[A-z]{3}\s[0-9]+[,]\s[A-z]{3}\s([0-9]+)')
    # Assign returned lists from payload_info function
    outbound_solution_ids, outbound_solution_cabin_class, inbound_solution_ids, \
        inbound_solution_cabin_class = payload_info(website)

    # payload that is sent to the post_page to gather information on the flight
    payload = {'option': 'com_travel', 'task': 'airbook.addPassengers',
               'outbound_request_id': pattern_request_ids.search(str(block_request_ids)).group(1),
               'inbound_request_id': pattern_request_ids.search(str(block_request_ids)).group(3),
               'outbound_solution_id': '', 'outbound_cabin_class': '', 'inbound_solution_id': '',
               'inbound_cabin_class': '', 'adults': '1', 'children': '0', 'infants': '0', 'change_flight': ''}

    # iteration for adding the corresponding cabin class to its solution id
    iteration_outbound = 0

    # assigns outbound solution id and inbound solution id, their cabin classes to the payload
    for outbound_solution in outbound_solution_ids:
        payload['outbound_solution_id'] = outbound_solution
        payload['outbound_cabin_class'] = outbound_solution_cabin_class[iteration_outbound]
        iteration_inbound = 0
        for inbound_solution in inbound_solution_ids:
            payload['inbound_solution_id'] = inbound_solution
            payload['inbound_cabin_class'] = inbound_solution_cabin_class[iteration_inbound]
            # sends the payload to the post_page and gets the flight detail page
            flight_detail_page = requests.post(post_page, data=payload).text
            # Assign returned lists
            outbound_departure_airport, outbound_arrival_airport, outbound_departure_time, outbound_arrival_time, \
                inbound_departure_airport, inbound_arrival_airport, inbound_departure_time, inbound_arrival_time, \
                flight_price, flight_tax = flight_information(flight_detail_page)

            # removes commas in time lists
            outbound_departure_time = [comma.replace(',', '') for comma in
                                       outbound_departure_time]
            outbound_arrival_time = [comma.replace(',', '') for comma in
                                     outbound_arrival_time]
            inbound_departure_time = [comma.replace(',', '') for comma in
                                      inbound_departure_time]
            inbound_arrival_time = [comma.replace(',', '') for comma in
                                    inbound_arrival_time]

            # adds the year to the time lists
            for date in block_flight_query:
                outbound_departure_time = [time + " " + pattern_flight_date.search(str(date)).group(1) for time in
                                           outbound_departure_time]
                outbound_arrival_time = [time + " " + pattern_flight_date.search(str(date)).group(1) for time in
                                         outbound_arrival_time]
                inbound_departure_time = [time + " " + pattern_flight_date.search(str(date)).group(2) for time in
                                          inbound_departure_time]
                inbound_arrival_time = [time + " " + pattern_flight_date.search(str(date)).group(2) for time in
                                        inbound_arrival_time]

            # ,,zips'' the lists together into tuples for writing into csv file
            rows = zip(outbound_departure_airport, outbound_arrival_airport, outbound_departure_time,
                       outbound_arrival_time,
                       inbound_departure_airport, inbound_arrival_airport, inbound_departure_time, inbound_arrival_time,
                       flight_price, flight_tax)

            # writes all of the information into a csv file
            with open('flight_list.csv', mode='a', newline='', encoding="utf-8") as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                data = list(rows)
                for row in data:
                    row = list(row)
                    spamwriter.writerow(row)

            iteration_inbound += 1
        iteration_outbound += 1
