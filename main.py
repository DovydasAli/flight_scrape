from bs4 import BeautifulSoup
import requests
import re
import csv
import pandas
# import requests
# import logging
#
# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
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

outbound_departure_airport = []
outbound_arrival_airport = []
outbound_departure_time = []
outbound_arrival_time = []
inbound_departure_airport = []
inbound_arrival_airport = []
inbound_departure_time = []
inbound_arrival_time = []
total_price = []
taxes = []

pattern = re.compile(
    r'(.+)\s(.+),(.+\s)(.+),(.+)')  # regex surasti marke(1), modeli(2), variklio turi(3) ir masinos tipa(4)
pattern_outbound_departure_airport = re.compile(r'\w+')  # regex surasti pagaminimo data
pattern_outbound_arrival_airport = re.compile(r'(\d+)(\w+)')  # regex surasti galia
pattern_outbound_departure_time = re.compile(r'(\d+\s)(\w+)')  # regex surasti rida
pattern_outbound_arrival_time = re.compile(r'\w+')  # regex surasti pagaminimo data
pattern_inbound_departure_airport = re.compile(r'(\d+)(\w+)')  # regex surasti galia
pattern_inbound_arrival_airport = re.compile(r'(\d+\s)(\w+)')  # regex surasti rida
pattern_inbound_departure_time = re.compile(r'(\d+)(\w+)')  # regex surasti galia
pattern_inbound_arrival_time = re.compile(r'(\d+\s)(\w+)')  # regex surasti rida
pattern_total_price = re.compile(r'(\d+\s)(\w+)')  # regex surasti rida
pattern_taxes = re.compile(r'(\d+\s)(\w+)')  # regex surasti rida
puslapis = requests.get(
    "https://www.fly540.com/flights/nairobi-to-mombasa?isoneway=0&depairportcode=NBO&arrvairportcode=MBA&date_from=Wed%2C+26+Jan+2022&date_to=Wed%2C+2+Feb+2022&adult_no=1&children_no=0&infant_no=0&currency=USD&searchFlight=").text  # pavercia duota puslapi i teksta
# print(puslapis)
soup = BeautifulSoup(puslapis, 'html.parser')
print(soup)
# blokas = soup.find_all('div', class_='announcement-title',
#                        title=False)  # nuskaito visus objektus pagal paduota kriteriju title=False del to kad neimtu nuo atro puslapio
# # atsirandancius top 5 pusiulimus
# blokas_pagaminimo_data = soup.find_all('span', title='Pagaminimo data')  # surasti pagaminimo data puslapyje
# blokas_galia = soup.find_all('span', title='Galia')  # surasti automobilio galia puslapyje
# blokas_rida = soup.find_all('span', title='Rida')  # surasti automobilio rida puslapyje
# blokas_kaina = soup.find_all('div', class_='announcement-pricing-info')  # surasti automobilio kaina puslapyje
# for blokai in blokas:  # pagal per regex paduota pattern iesko ir sudeda i atitinkamus listus
#     marke.append(pattern.search(blokai.text).group(1))
#     modelis.append(pattern.search(blokai.text).group(2))
#     variklio_turis.append(pattern.search(blokai.text).group(3))
#     kebulas.append(pattern.search(blokai.text).group(5))
#
# for data in blokas_pagaminimo_data:  # pagal per regex paduota pattern iesko ir sudeda i atitinkamus listus
#     pagaminimo_data.append(pattern_pagaminimo_data.search(data.text).group(0))
#
# for kw in blokas_galia:  # pagal per regex paduota pattern iesko ir sudeda i atitinkamus listus
#     galia.append(pattern_galia.search(kw.text).group(0))
#
# for km in blokas_rida:  # pagal per regex paduota pattern iesko ir sudeda i atitinkamus listus
#     rida.append(pattern_rida.search(km.text).group(0))
#
# for eur in blokas_kaina:
#     kaina.append(pattern_kaina.search(eur.text).group(0))
#
# marke = [tarpai.strip(' ') for tarpai in marke]  # panaikina tarpus listo objektuose
# kebulas = [tarpai.strip(' ') for tarpai in kebulas]  # panaikina tarpus listo objektuose
# galia = [tarpai.strip(' ') for tarpai in galia]  # panaikina tarpus listo objektuose
# rida = [tarpai.replace(" ", "") for tarpai in rida]  # panaikina tarpus listo objektuose
# kaina = [tarpai.replace(" ", "") for tarpai in kaina]  # panaikina tarpus listo objektuose
#
# rows = zip(marke, modelis, variklio_turis, kebulas, pagaminimo_data, galia, rida,
#            kaina)  # istrina paskutine eile reik sutaisyt magiskai susitaise bet gali pasikartot
#
# with open('automobiliu_sarasas_final.csv', mode='w', newline='', encoding="utf-8") as csvfile:
#     spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#
#     data = list(rows)
#     for row in data:
#         row = list(row)
#         spamwriter.writerow(row)