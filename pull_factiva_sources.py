#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 15:48:02 2019

@author: jmr
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from random import randrange
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import pandas as pd
import string
import glob

## stting things up
output_repo_country = '/home/jmr/Dropbox/datasets_general/factiva_sources/data/by_country' 

#### Get data by country
## query function
def source_query(keyword = '',
               country_n = '274'):
    
    ## base url
    url = "http://factiva.com/sources/factivasearch/index_cs.aspx"
    ## start the webdriver
    ua = UserAgent()
    userAgent = ua.random
    # change download dir and add some more options
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--profile-directory=Default')
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--disable-plugins-discovery");
    chromeOptions.add_argument("--start-maximized")
    
    ## fire up the driver
    driver = webdriver.Chrome(chrome_options=chromeOptions)
    driver.implicitly_wait(21)
    driver.maximize_window()
    driver.delete_all_cookies()
    driver.get(url)
    ## create the xpath
    xpath_static = '//*[@id="lstReg"]/option['
    xpath = xpath_static + str(country_n) + "]"
    ## find webelement for country
    cur_option = driver.find_element_by_xpath(xpath)
    country = cur_option.text
    print("\nscraping " + country)
    
    ## find webelement for source
    # newspapers all and Broadcasts:
    driver.find_element_by_xpath('//*[@id="lstType"]/option[86]').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="lstType"]/option[54]').click()
    
    ## keyword input
    kw_input = driver.find_element_by_css_selector('#query')
    kw_input.send_keys(keyword)
    time.sleep(randrange(1,2))
    ## click it
    cur_option.click()
    
    ## make the query
    driver.find_element_by_css_selector('#btnRunSearch').click()
    time.sleep(randrange(3,6))
    ## check if there is any result
    no_results = False
    is_limited = False
    try:
        no_res = driver.find_element_by_css_selector('#SearchGrid > tbody > tr > td').text
        if "any results" in no_res:
            no_results = True
    except:
        no_results = False
        
    if no_results == False:
        ## check if multi-page
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#SearchGrid > tbody > tr.cssPager")))
            is_multi_page = True
        except:
            is_multi_page = False
        ## check if limit was exceeded
        try:
            results_n_raw = driver.find_element_by_css_selector('#lblFooter').text
            results_n = int(re.search('(?<=of\s{1})[0-9]+|[0-9]+\s+(?=sources)', results_n_raw)[0])
            if results_n > 100:
                is_limited = True
            else:
                is_limited = False
        except:
            is_limited = False
    else:
        is_multi_page = False
        is_limited = False
    ## return the relevant results
    return [driver, country, no_results, is_multi_page, is_limited] 

### parsing function
def parse_source(driver = None):
    ## get the urls
    source_urls = driver.find_elements_by_xpath("//*[contains(@id, '_HyperLink2')]")
    ## container
    df_cont = []
    ## source parser loop
    for source in source_urls:
        url = source.get_attribute('href')
        print(url)
        ## start the webdriver
        ua = UserAgent()
        userAgent = ua.random
        # change download dir and add some more options
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument(f'user-agent={userAgent}')
        chromeOptions.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])
        chromeOptions.add_argument('--disable-extensions')
        chromeOptions.add_argument('--profile-directory=Default')
        chromeOptions.add_argument("--incognito")
        chromeOptions.add_argument("--disable-plugins-discovery");
        chromeOptions.add_argument("--start-maximized")
        
        ## fire up the driver
        driver2 = webdriver.Chrome(chrome_options=chromeOptions)
        driver2.implicitly_wait(21)
        driver2.maximize_window()
        driver2.delete_all_cookies()
        driver2.get(url)
        
        WebDriverWait(driver2, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[1]/td')))
        metadata = driver2.find_elements_by_xpath('/html/body/table/tbody/tr[1]/td')
        cols = []
        cur_values = []
        cols = []
        cur_values = []
        for x in re.split("\n\n|(?<=\\'),", metadata[0].text):
            obs = x.split(":")
            print(obs)
            if len(obs) > 2:
                cols.append(obs[0])
                cur_values.append(obs[1] + ": " + obs[2])
            else:
                cols.append(obs[0])
                cur_values.append(obs[1])
        cur_df = pd.DataFrame([cur_values], columns = cols, index = [0])
        df_cont.append(cur_df)
        # close the tab
        driver2.close()
    ret = pd.concat(df_cont)
    return ret

#### The loop
## identify the number of countries
url = "http://factiva.com/sources/factivasearch/index_cs.aspx"
## randomize the user agent
ua = UserAgent()
userAgent = ua.random
# change download dir and add some more options
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument(f'user-agent={userAgent}')
chromeOptions.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])
chromeOptions.add_argument('--disable-extensions')
chromeOptions.add_argument('--profile-directory=Default')
chromeOptions.add_argument("--incognito")
chromeOptions.add_argument("--disable-plugins-discovery");
chromeOptions.add_argument("--start-maximized")

## fire up the driver
driver = webdriver.Chrome(chrome_options=chromeOptions)
driver.implicitly_wait(21)
driver.maximize_window()
driver.delete_all_cookies()

## go to the hamburg uni database page, and click on the nexis link
driver.get(url)

## geographic entities
geo_options = driver.find_elements_by_xpath('//*[@id="lstReg"]/option')
n_options = len(geo_options)
countries = []
for geo in geo_options:
    countries.append(geo.text)
driver.quit()

### the loop
for i in range(1, n_options):
    
    ## name component of the filename
    country = countries[i - 1]
    country2 = re.sub("\s+","_", country)
    country3 = re.sub("/|\.|,","", country2)
    filename_base = output_repo_country + "/" + country3 + ".csv"
    
    ### First, check if there were results
    if os.path.isfile(filename_base) == True or os.path.isfile(output_repo_country + "/" + country3 + "_z" + ".csv") == True :
        print("\ndone\n")
    
    else:
        ## make the country query
        driver_list = source_query(keyword = '',
                              country_n = i)
        driver = driver_list[0]
        country = driver_list[1]
        no_results = driver_list[2]
        is_multi_page = driver_list[3]
        is_limited = driver_list[4]
        
        ## check if there are not results
        if no_results == True:
            # save a no results df
            no_results_df = pd.DataFrame([{"no_results": "yes"}])
            no_results_df.to_csv(filename_base)
            driver.quit()
        # check if single page
        elif is_multi_page == False and is_limited == False:
            # just parse and save
            #parse it
            page_df = parse_source(driver = driver)
            page_df['is_limited'] = is_limited
            page_df['countryOrgeo'] = country
            page_df.to_csv(filename_base)
            driver.quit()
            
        ## multipage but not limited 
        elif is_multi_page == True and is_limited == False:
            ## loop across each result at current page and get 
            pages = len(driver.find_elements_by_xpath('//*[@id="SearchGrid"]/tbody/tr[21]/td/table/tbody/tr/td/a'))
            query_cont = []
            for page_n in range(1, pages + 1):
                page_df = parse_source(driver = driver)
                page_df['is_limited'] = is_limited
                page_df['countryOrgeo'] = country
                query_cont.append(page_df)
                driver.execute_script("__doPostBack('SearchGrid','Page${}')".format(page_n + 1))
                time.sleep(randrange(3,6))
                    
            query_df = pd.concat(query_cont)
            query_df.to_csv(filename_base)
            driver.quit()
        else:
            ## limit of results displayed. Repeat the query making inserting a letter of the dictionary to limit the results
            # alphabet
            alpha = list(string.ascii_lowercase)
            
            # close the web-driver
            driver.quit()
            # loop
            for letter in alpha:
                filename_letter = output_repo_country + "/" + country3 + "_" + letter + ".csv"
                # check if existing
                if os.path.isfile(filename_letter) == False:
                    # not there, go on..
                    ## make the country query
                    driver_list = source_query(keyword = letter,
                                          country_n = i)
                    # the relevant parameters
                    driver = driver_list[0]
                    country = driver_list[1]
                    no_results = driver_list[2]
                    is_multi_page = driver_list[3]
                    is_limited = driver_list[4]
                    if no_results == False:
                        ## loop across each result at current page and get 
                        pages = len(driver.find_elements_by_xpath('//*[@id="SearchGrid"]/tbody/tr[21]/td/table/tbody/tr/td/a'))
                        query_cont = []
                        if is_multi_page == True:
                            for page_n in range(1, pages + 1):
                                page_df = parse_source(driver = driver)
                                page_df['is_limited'] = is_limited
                                page_df['countryOrgeo'] = country
                                query_cont.append(page_df)
                                time.sleep(randrange(1,6))
                                driver.execute_script("__doPostBack('SearchGrid','Page${}')".format(page_n+1))
                            query_df = pd.concat(query_cont)
                            driver.quit()
                            query_df.to_csv(filename_letter)
                        else:
                            page_df = parse_source(driver = driver)
                            page_df['is_limited'] = is_limited
                            page_df['countryOrgeo'] = country
                            query_cont.append(page_df)
                            time.sleep(randrange(1,3))
                            query_df = pd.concat(query_cont)
                            driver.quit()
                            query_df.to_csv(filename_letter)
                            
                    else:
                        no_results_df = pd.DataFrame([{"no_results": "yes"}])
                        no_results_df.to_csv(filename_letter)
                        driver.quit()

### Put them all together (remove the ones without results)
all_files = glob.glob(output_repo_country + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    if "no_results" not in df.columns:
        li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)                        

## drop duplicates by country
df = frame.drop_duplicates(['Source Code', 'Source Name', 'countryOrgeo'])

df = df.sort_values(by = 'countryOrgeo')

df.to_csv("/home/jmr/Dropbox/datasets_general/factiva_sources/data/factiva_sources_news&broadcast_all.csv")
 