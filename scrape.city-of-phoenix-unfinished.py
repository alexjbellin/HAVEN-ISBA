#import scraping function libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import random
import time

#Set base url for bids page with list view of all bids
phx_url_main = 'https://solicitations.phoenix.gov/Solicitations?page=1&pageSize=50&selectedSearchType=searchByNumber&sort=DueDate&sortDirection=Descending'
#May have to expand later with scrolling functionality

#request html code
phx_request = requests.get(phx_url_main)

#html of the whole page - refer back here for each opp url
phx_soup = BeautifulSoup(phx_request.text, 'html.parser')

#search for all table rows
phx_opp_tr = phx_soup.findAll('tr')

ref_url = []

#eliminate the first row, which is the headers
for opp in phx_opp_tr[1:]:
    url = opp.find('a')['href']
    #make sure the url is complete
    url_full = "https://solicitations.phoenix.gov" + url
    if url is not None:
        ref_url.append(url_full)

ref_id = []

for opp in phx_opp_tr[1:]:
    r_id = opp.find('a')
    r_id_txt = r_id.text
    ref_id.append(r_id_txt)


end_date = []

for opp in phx_opp_tr[1:]:
    tds = opp.findAll('td')
    e_date = tds[3].text.strip()
    
    date_obj = datetime.strptime(e_date, '%m/%d/%Y %I:%M %p')
    new_date_string = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    end_date.append(new_date_string)

#initiate all variables
ref_name = [] #done
name = [] #done
description = []
certifications = []
county = []
industry_codes = []
keywords = []
organization = []
sector_type = []
begin_date = [] #done
is_continuous = []
city = []
state = []
place_of_performance = []
address1 = []
address2 = []
postal_code = []
contact_name = [] #done
contact_phone = []
contact_email = [] #done
contact_name2 = []
contact_phone2 = []
contact_email2 = []
dollar_actual = []
dollar_estimate_min = []
dollar_estimate_max = []
dollar_estimate_avg = []


#big loop to find everything for each opp
#for url in ref_url:
url = ref_url[1]

#parse each individual opp url
opp_request = requests.get(url)
opp_soup = BeautifulSoup(opp_request.text, 'html.parser')

#extract the ref_name
ttl = opp_soup.find('h1')
ttl_txt = ttl.text.strip()
ref_name.append(ttl_txt)
name.append(ttl_txt)
    
#extract contact info
body = opp_soup.find('div', attrs = {'class': 'wrapper'})
cont = body.find('a')

#extract contact name
c_name = cont.text.strip()
contact_name.append(c_name)

#convert back to BeautifulSoup object
cont = str(cont)
cont_soup = BeautifulSoup(cont, 'html.parser')

#extract contact email
c_email = cont_soup.a['href'].split(':')[1]
contact_email.append(c_email)

#find updated date, which is closest thing to begin date in this source
updated_date = opp_soup.find('p', attrs = {'class': 'hidden-lg'})
input_string = updated_date.text.strip()
date_string = input_string.split(' ')[2]
time_string = input_string.split(' ')[3] + ' ' + input_string.split(' ')[4]
datetime_string = date_string + ' ' + time_string
datetime_obj = datetime.strptime(datetime_string, '%m/%d/%Y %I:%M %p')
b_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
begin_date.append(b_date)

#sleep function to delay each get request, so that the code is not banned from operating
#time.sleep(random.randint(3,10))
