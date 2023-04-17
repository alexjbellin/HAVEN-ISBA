
#import scraping function libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import random
import time

#Set base url for bids page with list view of all bids
wdot_url_main = 'https://wsdot.wa.gov/business-wsdot/contracts/search-contracting-opportunities?combine=&field_tags_target_id%5B393%5D=393&field_tags_target_id%5B110%5D=110&field_tags_target_id%5B108%5D=108&field_tags_target_id%5B109%5D=109&field_tags_target_id%5B112%5D=112&field_tags_target_id%5B107%5D=107&field_contract_status_target_id%5B123%5D=123&field_contract_status_target_id%5B119%5D=119&sort_by=field_publication_date_value'

#request html code
wdot_request = requests.get(wdot_url_main)


#html of the whole page - refer back here for each opp url
wdot_soup = BeautifulSoup(wdot_request.text, 'html.parser')

#find all opportunities' urls
wdot_opp_urls = wdot_soup.findAll('div', attrs = {'class': 'col-xl-9 col-lg-9 col-md-9 col-sm-12 col-xs-12 pull-right views-row'})


#collate into a list
ref_url = []

for opp in wdot_opp_urls:
    url = opp.find('a')['href']
    url_full = "https://wsdot.wa.gov" + url
    ref_url.append(url_full)


#initiate all variables
ref_name = []
name = []
description = []
certifications = []
county = []
ref_id = []
industry_codes = []
keywords = []
organization = []
sector_type = []
begin_date = []
end_date = []
is_continuous = []
city = []
state = []
place_of_performance = []
address1 = []
address2 = []
postal_code = []
contact_name = []
contact_phone = []
contact_email = []
contact_name2 = []
contact_phone2 = []
contact_email2 = []
dollar_actual = []
dollar_estimate_min = []
dollar_estimate_max = []
dollar_estimate_avg = []

#big loop to find everything for each opp
for url in ref_url:

    #parse each individual opp url
    opp_request = requests.get(url)
    opp_soup = BeautifulSoup(opp_request.text, 'html.parser')

    #extract the ref_name
    ttl = opp_soup.find('h1', attrs = {'class': 'page-header'})
    ttl_txt = ttl.text.strip()
    ref_name.append(ttl_txt)
    name.append(ttl_txt)

    #extract the description
    desc = opp_soup.find('div', attrs = {'class': 'content-middle-left col-12 col-sm-12 col-md-12 col-lg-8 col-xl-8'})
    desc_txt = desc.find('p').text.strip()
    description.append(desc_txt)

    #extract the counties as a list to accomodate multiple counties
    cnty = desc.find('div', attrs = {'class': 'field field--name-field-county field--type-entity-reference field--label-hidden field--items'})
    wdot_county = cnty.findAll('div', attrs = {'class': "field--item"})
    county_item = []
    for w_cnty in wdot_county:
        county_text = w_cnty.text.strip()
        county_item.append(county_text)
    county.append(county_item)

    #extract ref_id
    r_id = desc.find('div', attrs = {'class': 'field field--name-field-contract-id field--type-string field--label-hidden field--item'})
    #later on, ref_id is appended
    #needs to append at end of code in order to account for missing ref_id, which have a placeholder created from other variables

    #no industry codes for this source
    i_code = None
    industry_codes.append(i_code)

    #Defaults to highway construction, unless it has a Ferries tag
    keyws = desc.find('div', attrs = {'class': 'field field--name-field-tags field--type-entity-reference field--label-hidden field--items'})
    if "Ferries" in keyws.text:
        keywords.append(None)
    else:
        keywords.append("Highway Construction")

    #same for all opps in this source
    org = "Washington Department of Transportation"
    organization.append(org)

    #same for all opps in this source
    sector = "Government Opportunity"
    sector_type.append(sector)

    
    #begin and end date sections
    #difficult to parse out, since no div tags to help
    #ends up creating a list of dates, and using the first two as begin and end
    #should work for every opp at time of creation - 4/16/23
    #There should only be two possible dates in the section it is scraping, and everything has a begin date
    dates = desc.findAll('time')

    b_date = str(dates[0])
    b_datetime_str = b_date.split('"')[1]
    #formatting for the database
    b_datetime_obj = datetime.strptime(b_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    b_datetime_formatted = b_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    begin_date.append(b_datetime_formatted)

    #this determines if there is an end date, if not it puts a null value
    if len(dates) > 1:
        e_date = str(dates[1])
        e_datetime_str = b_date.split('"')[1]
        #formatting for the database
        e_datetime_obj = datetime.strptime(e_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        e_datetime_formatted = e_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        end_date.append(e_datetime_formatted)
    else:
        end_date.append(None)

    cont = False
    is_continuous.append(cont)

    #there are sometimes cities listed in description, but would be impossible to scrape without some sort of ai
    cty = None
    city.append(cty)

    #all in Washington
    stte = "WA"
    state.append(stte)

    #concatenate counties and state to get place of performance
    #multiples counties joined with the word "and"
    p_of_p = " and ".join(county_item)
    p_of_p_full = f"{p_of_p}, Washington"
    place_of_performance.append(p_of_p_full)

    add1 = None
    address1.append(add1)

    add2 = None
    address2.append(add2)

    post_c = None
    postal_code.append(post_c)

    #contact info section
    
    #html for the whole box, refer back for each individual category
    contact_info = opp_soup.find('div', attrs = {'class': 'content-middle-right col-12 col-sm-12 col-md-12 col-lg-4 col-xl-4'})

    #certifications first, from the funding box section
    certs = []
    fund_src = contact_info.find('div', attrs = {'class': 'field field--name-field-funding-source-text field--type-string field--label-above'})
    if fund_src is not None:
        fund_desc = fund_src.find('div', attrs = {'class': 'field--item'})
        if "small business".lower() in fund_desc.text.lower():
            certs.append("SBE")
        if "disadvantaged business enterprise".lower() in fund_desc.text.lower():
            certs.append("DBE")
        if "veteran owned business".lower() in fund_desc.text.lower():
            certs.append("VBE")
        if "veteran-owned business".lower() in fund_desc.text.lower():
            certs.append("VBE")
        if "veteran business".lower() in fund_desc.text.lower():
            certs.append("VBE")
    if len(certs) == 0:
        certs.append("Undefined")
    certifications.append(certs)
    
    
    #names are always in <strong> tags to make them bold
    c_name = contact_info.find('strong')
    #to account for no contact given:
    if c_name is not None:
        contact_name.append(c_name.text.strip())
    else:
        contact_name.append(None)

    c_email = contact_info.find('div', attrs = {'class': 'field field--name-field-email field--type-email field--label-hidden field--item'})
    #to account for no email given:
    if c_email is not None:
        contact_email.append(c_email.text.strip())
    else:
        contact_email.append(None)


    c_phone = contact_info.find('div', attrs = {'class': 'field field--name-field-phone field--type-telephone field--label-hidden field--items'})
    #to account for no phone given (common)
    if c_phone is not None:
        contact_phone.append(c_phone.text.strip())
    else:
        contact_phone.append(None)

    #no instances of multiples contacts as of 4/16/23
    #this can be ammended later if there is a case like that
    c_name2 = None
    contact_name2.append(c_name2)

    c_phone2 = None
    contact_phone2.append(c_phone2) 

    c_email2 = None
    contact_email2.append(c_email2)

    d_act = None
    dollar_actual.append(d_act)

    #Finding price range
    desc_str = str(desc)
    start_index = desc_str.find('$')
    end_index = desc_str.find('<', start_index)
    price = desc_str[start_index:end_index]
    #after the above line, there is a price range in a string if one exists
    if price == '':
        #if there is no price range, set everything to null values
        dol_max_int = None
        dol_min_int = None
        dol_avg = None
    else:
        #if there is at least one dollar value, parse it out
        dol_pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?"

        matches = re.findall(dol_pattern, price)
        if len(matches) == 1:
            #if there is only one dollar value, set it to the minimum
            #there is then no maximum, and also no average calculation
            dol_min = matches[0]
            dol_max_int = None
            dol_mini = dol_min.replace(",", "")
            dol_mini = dol_mini.replace("$", "")
            dol_min_int = int(float(dol_mini))
            #above lines are simply to get $###,###,### form into a simple integer
            dol_avg = None
        elif len(matches) == 2:
            #if there are two values, set min and max accordingly
            dol_min = matches[0]
            dol_max = matches[1]
            #conversion to integers below
            dol_mini = dol_min.replace(",", "")
            dol_mini = dol_mini.replace("$", "")
            dol_min_int = int(float(dol_mini))
            dol_maxi = dol_max.replace(",", "")
            dol_maxi = dol_maxi.replace("$", "")
            dol_max_int = int(float(dol_maxi))

            #calculate average
            dol_avg = (dol_max_int + dol_min_int) // 2

    #append values, regardless of 0, 1, or 2 dollar estimates
    #needs to stay outside if statements to work properly
    dollar_estimate_min.append(dol_min_int)
    dollar_estimate_max.append(dol_max_int)
    dollar_estimate_avg.append(dol_avg)

    #if no ref_id, placeholder is assigned
    if r_id is None or r_id.text == "To be assigned":
        ref_id.append("WDOT" + " " + ttl_txt + b_datetime_formatted)
    else:
        ref_id.append(r_id.text)

    #sleep function to delay each get request, so that the code is not banned from operating
    time.sleep(random.randint(3,10))


#The following puts all the collected lists into a dataframe
#type is missing from the list
wdot_df = pd.DataFrame({'refId': ref_id, 'refUrl': ref_url, 'name': name, 'refName': ref_name, 'certifications': certifications, 'industrycodes': industry_codes, 'keywords': keywords, 'organization': organization, 'sectorType': sector_type, 'beginDate': begin_date, 'endDate': end_date, 'isContinuous': is_continuous, 'city': city, 'county': county, 'placeOfPerformance': place_of_performance, 'state': state, 'address1': address1, 'address2': address2, 'postalCode': postal_code, 'contactName': contact_name, 'contactPhone': contact_phone, 'contactEmail': contact_email, 'contactName2': contact_name2, 'dollarActual': dollar_actual, 'dollarEstimateAvg': dollar_estimate_avg, 'dollarEstimateMax': dollar_estimate_max, 'dollarEstimateMin': dollar_estimate_min, 'description': description})


#This gives an output in JSON, with each source separated out from each other
now = datetime.now()
date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

#This gives a unique file name by adding a timestamp
wdot_df.to_json(f"wdot_source_data_{date_string}", orient = 'records')