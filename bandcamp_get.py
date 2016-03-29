#############################################################
#                                                           #
# bandcamp-get - automated music downloading via selenium   #
# original written by Hunter Hammond (huntrar@gmail.com)    #
# current version: RicardoSilva (github.com/Ricardo-Silva91)#
#                                                           #
#############################################################


import argparse
import os
import random
import time

import lxml.html as lh
import requests
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
               'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5')


def get_parser():
    parser = argparse.ArgumentParser(description='automated music downloading via selenium')
    parser.add_argument('user', metavar='USER', type=str, nargs='?',
                        help='bandcamp user to download from')
    parser.add_argument('-b', '--browser', type=str,
                        help='enter chrome or firefox, defaults to firefox')
    parser.add_argument('-d', '--display', type=int,
                        help='show display, 0-no 1-yes , default=0')
    parser.add_argument('-e', '--email', type=str,
                        help='use your own email instead of a throwaway')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-f', '--folder', type=str,
                        help='choose folder to download (absolute path) (default: /home/$user/Downloads)')
    parser.add_argument('-js', '--json_file',
                        help='load a list of artists from json folder (replace USER with path to file)',
                        action='store_true')
    return parser


def get_driver(browser, folder, display):
    dricve = 1

    if display == 0:
        display = Display(visible=0, size=(800, 600))
        display.start()

    if browser and 'chrome' in browser.lower():
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": folder}
        options.add_argument('--user-agent={}'.format(random.choice(USER_AGENTS)))
        options.add_experimental_option("prefs", prefs)

        if dricve == 1:
            return webdriver.Chrome(chrome_options=options)
        else:
            return webdriver.PhantomJS()  #
    else:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', random.choice(USER_AGENTS))
        profile.set_preference("browser.download.folderList", 2)
        # profile.set_preference("browser.download.manager.showWhenStarting",false);
        profile.set_preference("browser.download.dir", folder)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        return webdriver.Firefox(profile)


def get_album_links(args):
    seed_url = 'https://{}.bandcamp.com'.format(args['user'])

    # print (seed_url)

    headers = {'User-Agent': random.choice(USER_AGENTS)}
    r = requests.get(seed_url, headers=headers)
    l = lh.fromstring(r.text)
    all_links = l.xpath('//li/a[@href]/@href')
    all_links = all_links + l.xpath('//a[@href]/@href')
    album_links = []

    # print (seed_url)

    # print (all_links)
    # input("Press Enter to continue...")

    for link in all_links:
        if '/album/' in link and '/feed/' not in link:
            t = False
            xpto = seed_url + link
            for xalink in album_links:
                if xpto == xalink:
                    t = True
                    break
            if not t:
                album_links.append(seed_url + link)
    print('collected links:\n{}'.format(album_links))
    # input("Press Enter to continue...")
    return album_links


def auto_download(args):
    print('opening guerrilla window')

    e_driver = get_driver(args['browser'], args['folder'], args['display'])  # Email driver
    # e_driver.implicitly_wait(1)
    print('going to guerrilla')
    e_driver.get('https://www.guerrillamail.com/')
    args['email'] = e_driver.find_element_by_xpath('//span[@id="email-widget"]').text
    mail_cache = set()
    download(args)
    # time.sleep(3)

    while e_driver.find_element_by_xpath('//span[@id="tick"]').text != 'Done.':
        pass

    # input("Press Enter to continue...")

    check_email(e_driver, mail_cache)

    # check again in case of stragglers, will ignore duplicates
    e_driver.get('https://www.guerrillamail.com/')

    while e_driver.find_element_by_xpath('//span[@id="tick"]').text != 'Done.':
        pass

    check_email(e_driver, mail_cache)
    # input("Press Enter to continue...")
    try:
        print('fake mail page')
        # input("Press Enter to continue...")

        if len(os.listdir(args['folder'])) > 0:

            can_move_on = False

            # wait for downloads to finish
            while not can_move_on:

                time.sleep(1)

                for file in os.listdir(args['folder']):
                    # print ('file endswith: ')

                    # for file in os.listdir('/home/rofler/Downloads'):
                    # print ('file endswith: {}', file_extension)
                    if file.endswith(".crdownload") | file.endswith(".zip.part"):
                        can_move_on = False
                        break
                    else:
                        can_move_on = True

            time.sleep(1)

            remove_duplicate(args)

        print('closing guerrilla window')
        e_driver.close()
        args['email'] = ''
    except Exception:
        print('trouble waiting for download to finish')
        time.sleep(1)
        e_driver.close()
        args['email'] = ''


def check_email(e_driver, mail_cache):
    emails = e_driver.find_elements_by_xpath('//tbody[@id="email_list"]/tr')

    for mail in emails:
        download_mail_link(e_driver, mail_cache, mail)


def download_mail_link(e_driver, mail_cache, mail):
    mail_window = e_driver.window_handles[0]
    try:
        mail.click()
        try:
            dl_element = e_driver.find_element_by_xpath('//div[@class="email_body"]/div//a[@target="_blank"]')
            if dl_element.text not in mail_cache:
                mail_cache.add(dl_element.text)
                dl_element.click()
                dl_window = e_driver.window_handles[1]
                e_driver.switch_to_window(dl_window)

                # print('Downloading {}'.format(link))

                # e_driver.find_element_by_xpath('//a[@class="downloadGo"]').click()

                e_driver.find_element_by_xpath('//a[@class="menuLink"]').click()
                # print ('mp3 320')
                id_element = e_driver.find_elements_by_xpath('//a[@class="indent ui-corner-all"]')[1]
                # print (id_element)

                # input("Press Enter to continue...")

                id_element.click()

                time_counter = 1
                can_move_on = False

                while time_counter < 20 and not can_move_on:

                    try:
                        e_driver.find_element_by_xpath('//a[@class="downloadGo"]').click()
                        can_move_on = True
                    except Exception:
                        time.sleep(1)
                        time_counter += 1

                e_driver.close()

                e_driver.switch_to_window(mail_window)
                e_driver.find_element_by_xpath('//a[@id="back_to_inbox_link"]').click()
        except Exception:
            e_driver.switch_to_window(mail_window)
            e_driver.find_element_by_xpath('//a[@id="back_to_inbox_link"]').click()
    except Exception:
        print('jogos')
        pass


def download(args):
    driver = get_driver(args['browser'], args['folder'], args['display'])
    driver.implicitly_wait(1)

    # print (args['album_links'])

    for link in args['album_links']:
        if not download_link(args, driver, link):
            break
    try:
        print('now we wait')
        # input("Press Enter to continue...")

        if len(os.listdir(args['folder'])) > 0:

            # if(len(os.listdir('/home/rofler/Downloads'))>0):
            can_move_on = False

            while not can_move_on:

                time.sleep(1)
                # print (os.listdir(args['folder']))

                for file in os.listdir(args['folder']):
                    # print ('file endswith: ')

                    # for file in os.listdir('/home/rofler/Downloads'):
                    # print ('file endswith: {}', file_extension)
                    if file.endswith(".crdownload") | file.endswith(".zip.part"):
                        can_move_on = False
                        break
                    else:
                        can_move_on = True

            time.sleep(1)

            remove_duplicate(args)

        print('closing download driver')
        driver.close()
    except Exception:
        print('trouble waiting for download to finish')
        time.sleep(1)
        driver.close()


def download_link(args, driver, link):
    try:
        # print (link)
        driver.get(link)
        try:
            test_element = driver.find_element_by_xpath("//span[@class='buyItemExtra buyItemNyp secondaryText']")

            # print (test_element.text)
            # input("Press Enter to continue...")
            # if (test_element.text != ' name your price'):
            if test_element.text != ' name your price':  # or test_element.text == 'or more'):
                print('the album {} is not free'.format(link))
                return True

        except Exception:
            try:
                print('the album {} is not free'.format(link))
                return True
            except Exception:
                pass

            pass

        driver.find_element_by_xpath("//button[@class='download-link buy-link']").click()

    except Exception:
        print('the album {} cannot be downloaded'.format(link))
        return True

    print('Downloading {}'.format(link))
    try:
        element = driver.find_element_by_xpath('//input[@id="userPrice"]')
        element.send_keys('0')
        element.send_keys(Keys.RETURN)

        print('passed without email')

    except Exception:
        print('fuck without email')
        pass

    try:
        element = driver.find_element_by_xpath('//input[@id="fan_email_address"]')
        # print (element)
        element.send_keys(args['email'])

        element = driver.find_element_by_id('fan_email_postalcode')
        element.send_keys(args['zip_code'])
        element.send_keys(Keys.RETURN)
    except Exception:
        print('fuck up on email')
        pass

    try:
        print('final page')
        print(driver.current_url)
        driver.find_element_by_xpath('//a[@class="menuLink"]').click()
        print('change bitrate')
        # print ('mp3 320')
        id_element = driver.find_elements_by_xpath('//a[@class="indent ui-corner-all"]')[1]
        # print (id_element)
        print('bitrate set')

        # input("Press Enter to continue...")

        id_element.click()
        print('bitrate')

        time_counter = 1
        can_move_on = False

        while time_counter < 20 and not can_move_on:

            try:
                driver.find_element_by_xpath('//a[@class="downloadGo"]').click()
                can_move_on = True
            except Exception:
                time.sleep(1)
                time_counter += 1

        # input("Press Enter to continue...")

        time.sleep(1)
    except Exception:
        print('fuck up on {}'.format(link))
        # input("Press Enter to continue...")
        pass

    return True


def remove_duplicate(args):
    print('Removing duplicates')

    for file in os.listdir(args['folder']):
        if file.endswith("(1).zip"):
            os.remove(args['folder'] + '/' + file)


def bandcamp_get_for_import(user, folder, display):
    # parser = get_parser()
    # args = vars(parser.parse_args())

    args = vars()

    args['display'] = display
    args['user'] = user
    args['folder'] = folder + '/' + args['user']
    args['browser'] = 'firefox'
    args['display'] = display

    args['zip_code'] = random.randint(10000, 99999)

    print('only one artist/band')

    args['album_links'] = get_album_links(args)

    if len(args['album_links']) > 0:
        auto_download(args)


