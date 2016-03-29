#!/usr/bin/env python

#############################################################
#                                                           #
# bandcamp-sniffer                                          #
# writen by - Ricardo Silva (github.com/Ricardo-Silva91)    #
#                                                           #
#############################################################


import argparse
import random
import time

import json
from pprint import pprint

import os
import getpass
import re

import lxml.html as lh
import requests
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.phantomjs.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from . import __version__


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
                'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
                'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5')





def get_parser():
    parser = argparse.ArgumentParser(description='bandcamp sniffer')

    parser.add_argument('file', metavar='FILE', type=str, nargs='?',
                         help='absolute path to json file to sniff to')
    parser.add_argument('-b', '--browser', type=str,
                         help='enter chrome or firefox, defaults to firefox')
    parser.add_argument('-d', '--display', type=int,
                         help='show display, 0-no 1-yes , defaul=0')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    return parser


def get_driver(browser, display):

    dricve=1
    
    if display==0:
        display = Display(visible=0, size=(800, 600))
        display.start()
    

    if browser and 'chrome' in browser.lower():
        options = webdriver.ChromeOptions()
        #prefs = {"download.default_directory" : folder}
        options.add_argument('--user-agent={}'.format(random.choice(USER_AGENTS)))
        options.add_experimental_option("prefs",prefs)


        if dricve == 1:
            return webdriver.Chrome(chrome_options=options)
        else:
            return webdriver.PhantomJS()#
    else:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', random.choice(USER_AGENTS))
        #profile.set_preference("browser.download.folderList",2);
        #profile.set_preference("browser.download.manager.showWhenStarting",false);
        #profile.set_preference("browser.download.dir",folder);
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        return webdriver.Firefox(profile)


def check_if_exists(data, username):

    exists = False

    #1st check waiting list
    for xpto in data["bc-get"]:
        if xpto["id"] == username:
            return True

    #2nd check used list
    for xpto in data["used"]:
        if xpto["id"] == username:
            return True


    return exists
    

            

            
            

def sniff(browser, display, data, data_file, args_file):

    seed_url = 'https://bandcamp.com/'
    driver = get_driver(browser, display)
    driver.implicitly_wait(1)

    driver.get(seed_url)

    must_go_on = True
    running_one_lap = True
    free_counter = 0

    while must_go_on:

        while running_one_lap:
            try:
                #id_element_row = driver.find_elements_by_xpath('//span[@class="item-over"]')[free_counter]
                id_element_row = driver.find_elements_by_xpath('//a[@class="item-inner"]')[free_counter]
                #id_element_row = driver.find_element_by_xpath('(//a[@class="item-inner"])[' + free_counter+1 + ']')
                #print('element found, counter: {}'.format(free_counter))
                #print('id_element_row: {}'.format(id_element_row))
                #print('element string: {}'.format(id_element_row.get_attribute('textContent')))

                #print(id_element_row.get_attribute('href'))
                #print((id_element_row.get_attribute('href').split('/',5)[2]).split('.',3)[0])

                try:
                    id_element_green = id_element_row.find_element_by_xpath('.//span[@class="item-over"]')
                    green_price = int(re.search(r'\d+', id_element_green.get_attribute('textContent')).group())
                    #print('value over: {}'.format(int(re.search(r'\d+', id_element_green.get_attribute('textContent')).group())))

                    id_element_title = id_element_row.find_element_by_xpath('.//h5[@class="item-title"]')
                    
                    #print('element title: {}'.format(id_element_title.get_attribute('textContent')))

                    id_element_black = id_element_row.find_element_by_xpath('.//span[@class="item-price"]')
                    black_price = int(re.search(r'\d+', id_element_black.get_attribute('textContent')).group())
                    #print('element value: {}'.format(int(re.search(r'\d+', id_element_black.get_attribute('textContent')).group())))

                    if (black_price - green_price == 0):
                        user = (id_element_row.get_attribute('href').split('/',5)[2]).split('.',3)[0]
                        print("it's a buy!! {}".format(user))
                        
                        if not check_if_exists(data, user):

                            #data['id'] = user
                            a_dict = {"id":  user }

                            bc = data['bc-get']

                            print("pass0")
                            print(bc)


                            #bc.update(a_dict)
                            bc.append(a_dict) # + ',' + a_dict + ']'

                            print("pass1")
                            print(bc)

                            #data.update(bc)
                            data['bc-get'] = bc

                            print("pass2")
                            print(data)

                            with open(args_file, 'w') as f:
                                json.dump(data, f)

                            print("pass3")
                            print(data)


                except Exception:
                    print("cheap fucks!")


                
                #id_element_green = driver.find_elements_by_xpath('//span[@class="item-price"]')[0]
                #print('id_element_green: {}'.format(id_element_green))
            
                free_counter+=1

            except Exception:
                print("reached end of feed row")
                free_counter=0
                break        
        
        time.sleep(5)

        pass
    






def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if not args['file'] == 'None':
    

        if args['version']:
            print(__version__)
            return

        if not args['display']:
            args['display'] = 0


        try:
            with open(args['file'], 'r') as data_file:    
                data = json.load(data_file)
        except Exception:
            print('please insert working json file path')
            return

        sniff(args['browser'], args['display'], data, data_file, args['file'])

    else:
        pass

if __name__ == '__main__':
    command_line_runner()
