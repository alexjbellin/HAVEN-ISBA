#Gather Source Code

#import scraping function libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

#Set base url for bids page with list view of all bids
glenn_url_main = 'https://www.countyofglenn.net/govt/bids'

#request html code
glenn_request = requests.get(glenn_url_main)

#html of the whole page - refer back here for each element
glenn_soup = BeautifulSoup(glenn_request.text, 'html.parser')


#Create Title List

#Scrape Titles
#example of the first title below
'''<td class="views-field views-field-title views-align-left view-resources-by-term view-filters views-exposed-widgets views-widget-filter-field_department_tid">
            REQUEST FOR PROPOSAL - Hydrogeologic Consultant
<br>
<br>
<div class="field-department"><a href="/departments/planning-community-development-services" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">Planning &amp; Community Development Services</a></div>          </td>
'''

#Scrape title text, set to variable
glenn_opp_titles = glenn_soup.findAll('td', attrs = {'class': 'views-field views-field-title views-align-left view-resources-by-term view-filters views-exposed-widgets views-widget-filter-field_department_tid'})

#Organization and Title

#create organization list
organization = []


for title in glenn_opp_titles:
    #Search out the org in the title column under the <a> html tag
    org = title.find('a')
    
    #condition if there is no organization
    if org != None:
        organization.append(org.text.strip())
    else:
        organization.append(None)


#create ref_name list
ref_name = []


for title in glenn_opp_titles:

    #Remove the work category and associated link, scraped in earlier segment
    category = title.find('a')
    if category != None:
        category.clear()
    
    #strip everything but the opportunity name, add to list (this mostly removes spaces and indents)
    clean_title_string = title.text.strip()
    ref_name.append(clean_title_string)


#Posted Date

#Scrape begin_date from the description

#begin_date example below
'''<td class="views-field views-field-field-bid-description views-align-left">
<i>Posted Dec 21, 2022 | 7:18am</i>          </td>'''

#gather all description text
#will be useful for this and the description section
glenn_full_descriptions = glenn_soup.findAll('td', attrs = {'class': 'views-field views-field-field-bid-description views-align-left'})

#create list of begin_dates
begin_date = []

for item in glenn_full_descriptions:
    post_date = item.findAll('i')
    #post date is always the last part of the description
    #sometimes there are other <i> tags, so this part removes them
    post_date = post_date[-1].text
    
    #Format into useable datetime object
    post_date_obj = datetime.strptime(post_date, 'Posted %b %d, %Y | %I:%M%p')
    formatted_begin_date = post_date_obj.strftime('%Y-%m-%d %H:%M:%S')
    begin_date.append(formatted_begin_date)
    
#Not in UTC, just local

#Descriptions

#create list of descriptions
description = []

#use full descriptions from earlier section
for item in glenn_full_descriptions:
    #multiple paragraphs per description, so need a list to collate
    opp_description = []
    paragraphs = item.findAll('p')
    for paragraph in paragraphs:
        opp_description.append(paragraph.text)
    
    #Join the list together into one seamless description
    opp_desc_string = "".join(opp_description)
    description.append(opp_desc_string)


#Certifications

#create list of certifications
certifications = []
for desc in description:
    
    #Using a list here allows for other certifications to be added over time
    cert_items = []
    if "PLHA" in desc:
        cert_items.append("DBE")
    else:
        cert_items.append("Undefined")
        
    certifications.append(cert_items)


#REGEXP searches

#create lists for contact_phone and contact_email
contact_email = []
contact_phone = []

for desc in description:
    
    #set the email form criteria to search for in the descriptions
    email_pattern = r"\b\w+@countyofglenn\.net\b"
    #search for the email format in the description, set the first one it finds to a variable
    email_match = re.search(email_pattern, desc)

    #set the phone form criteria to search for in the descriptions
    phone_pattern = r"\(\d{3}\) \d{3}-\d{4}"
    #search for the phone format in the description, set the first one it finds to a variable
    phone_match = re.search(phone_pattern, desc)
    
    #may not be a match, if not need to add a null value to the list
    if email_match:
        email = email_match.group()
    else:
        email = None
    
    if phone_match:
        phone = phone_match.group()
    else:
        phone = None
    
    contact_email.append(email)
    contact_phone.append(phone)


#Close Date

#end_date code below
'''<td class="views-field views-field-field-deadline-date">
            <span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2023-02-09T15:00:00-08:00">Thursday, February 9, 2023 3:00pm</span>          </td>'''
#find all examples of end_date code
glenn_close_dates = glenn_soup.findAll('td', attrs = {'class': 'views-field views-field-field-deadline-date'})

#create a list for end_dates
end_date = []

for date in glenn_close_dates:
    #Search for the span tag content identifier i.e. <span content = "">
    close_date = date.find('span')['content']
    #Format the date to match Haven database
    close_date_obj = datetime.fromisoformat(close_date)
    formatted_date = close_date_obj.strftime('%Y-%m-%d %H:%M:%S')
    #Add end date to list
    end_date.append(formatted_date)
    
#Not in UTC time, local only

#Sames and Nulls

#The next several variables are all identical for all opps, some of them being nulls

#ref_url is identical for every opp, just the main page
ref_url = []
for opp_num in range(len(ref_name)):
    url = glenn_url_main
    ref_url.append(url)

#Glenn county does not use industry codes
industrycodes = []
for opp_num in range(len(ref_name)):
    code = None
    industrycodes.append(code)

#Keywords not assigned yet
keywords = []
for opp_num in range(len(ref_name)):
    kw = None
    keywords.append(kw)

#All opps on this list are government opps
sector_type = []
for opp_num in range(len(ref_name)):
    sector = "Government Opportunity"
    sector_type.append(sector)

is_continuous = []
for opp_num in range(len(ref_name)):
    cont = False
    is_continuous.append(cont)

#These are county-wide and do not list a city
city = []
for opp_num in range(len(ref_name)):
    cty = None
    city.append(cty)

#Single county source, so all opps are from Glenn county
county = []
for opp_num in range(len(ref_name)):
    cnty = "Glenn County"
    county.append(cnty)

place_of_performance = []
for opp_num in range(len(ref_name)):
    place = "Glenn County, California"
    place_of_performance.append(place)

#Glenn county is only in CA, so states are all the same
state = []
for opp_num in range(len(ref_name)):
    st = "CA"
    state.append(st)

#No way yet to scrape addresses, since Glenn county is not consistent with it
address1 = []
for opp_num in range(len(ref_name)):
    address = None
    address1.append(address)

address2 = []
for opp_num in range(len(ref_name)):
    address = None
    address2.append(address)

postal_code = []
for opp_num in range(len(ref_name)):
    pcode = None
    postal_code.append(pcode)

#No consistency in how Glenn county presents contact names, so cannot scrape for it
contact_name = []
for opp_num in range(len(ref_name)):
    cname = None
    contact_name.append(cname)

contact_name2 = []
for opp_num in range(len(ref_name)):
    cname = None
    contact_name2.append(cname)

#No dollar values given at all
dollar_actual = []
for opp_num in range(len(ref_name)):
    dollars = None
    dollar_actual.append(dollars)

dollar_estimate_avg = []
for opp_num in range(len(ref_name)):
    dollars = None
    dollar_estimate_avg.append(dollars)

dollar_estimate_min = []
for opp_num in range(len(ref_name)):
    dollars = None
    dollar_estimate_min.append(dollars)

dollar_estimate_max = []
for opp_num in range(len(ref_name)):
    dollars = None
    dollar_estimate_max.append(dollars)

#Put it all together

#ref_id is generated here for Glenn county, since they do not have a system of their own
#format is ref_name-county-state-organization-begin_date
#names have been identical in the past, and begin dates can be as well; having both ensures a unique primary key
ref_id = []

for opp_num in range(len(ref_name)):
    r_id = f"{ref_name[opp_num]}-{county[opp_num]}-{state[opp_num]}-{organization[opp_num]}-{begin_date[opp_num]}"
    ref_id.append(r_id)

#This field is 100% identical to ref_name for this source
name = []

for n in range(len(ref_name)):
    name.append(ref_name[n])

#The following puts all the collected lists into a dataframe
#type is missing from the dataframe
glenn_df = pd.DataFrame({'refId': ref_id, 'refUrl': ref_url, 'name': name, 'refName': ref_name, 'certifications': certifications, 'industrycodes': industrycodes, 'keywords': keywords, 'organization': organization, 'sectorType': sector_type, 'beginDate': begin_date, 'endDate': end_date, 'isContinuous': is_continuous, 'city': city, 'county': county, 'placeOfPerformance': place_of_performance, 'state': state, 'address1': address1, 'address2': address2, 'postalCode': postal_code, 'contactName': contact_name, 'contactPhone': contact_phone, 'contactEmail': contact_email, 'contactName2': contact_name2, 'dollarActual': dollar_actual, 'dollarEstimateAvg': dollar_estimate_avg, 'dollarEstimateMax': dollar_estimate_max, 'dollarEstimateMin': dollar_estimate_min, 'description': description})

#This gives an output in JSON, with each source separated out from each other
now = datetime.now()
date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

#This gives a unique file name by adding a timestamp
glenn_df.to_json(f"glenn_county_source_data_{date_string}", orient = 'records')