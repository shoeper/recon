#!/usr/bin/env python

import os, argparse, time, sys
from selenium import webdriver
from importlib import import_module

parser = argparse.ArgumentParser(description='This tool uses Python Selenium to parse through certain sites and retrieve IP addresses, and emails.')
parser.add_argument('-d', '--domain', help="Customer's web domain.", required=True)
parser.add_argument('-n', '--name', help="All of the customer's names.", required=True, nargs='*')
parser.add_argument('-eF', '--emailFile', help="File name of where emails are saved.", required=False)
parser.add_argument('-iF', '--ipFile', help="File name of where IPs are saved.", required=False)
parser.add_argument('-hunter', '--hunterio', help='Turns off hunter.io.', default=True, required=False, action='store_false')
parser.add_argument('-dns', '--dnsdumpster', help='Turns off dnsdumpster.com.', default=True, required=False, action='store_false')
parser.add_argument('-whois', '--whois', help='Turns off whois.arin.net.', default=True, required=False, action='store_false')
parser.add_argument('-mx', '--mxtoolbox', help='Turns off mxtoolbox.com.', default=True, required=False, action='store_false')
parser.add_argument('-he', '--hurricaneelectric', help='Turns off bgp.he.net.', default=True, required=False, action='store_false')
parser.add_argument('-s', '--setting', help='Loads a saved setting file.', required=False)
parser.add_argument('-nS', '--new-setting', help='Creates a new setting file.', required=False)
parser.add_argument('-creds', '--credentials', help='Rewrites the recon.config folder.', default=False, required=False, action='store_true')
args = parser.parse_args()

name1 = args.setting
name2 = args.new_setting
dns_use = args.dnsdumpster
eF = args.emailFile
iF = args.ipFile
hunter_io = args.hunterio
whois_use = args.whois
mx_use = args.mxtoolbox
he_use = args.hurricaneelectric
customer_address = args.domain
customer = args.name
creds = args.credentials

dns_list = []
open_tabs = 0

try:
    input = raw_input
except NameError:
    pass

if iF != None:
    if iF[-4:-1] == '.txt':
        ip = open(iF, 'w')
    elif iF[-4:-1] != '.txt':
        ip = open(iF + '.txt', 'w')
else:
    ip = open('ips.txt', 'w')

if eF != None:
    if eF[-4:-1] == '.txt':
        emails = open(eF, 'w+')
    elif eF[-4:-1] != '.txt':
        emails = open(eF + '.txt', 'w+')
else:
    emails = open('emails.txt', 'w+')

gecko_location = ''
hunter_un = ''
hunter_pw = ''

def writeCreds():
    cred_write = open('recon.config', 'w')
    if hunter_io:
        hunter_un = input('What is your hunter.io email? ')
        hunter_pw = input('What is your hunter.io password? ')
        cred_write.write('Hunter email = ' + hunter_un + '\nHunter password = ' + hunter_pw + '\n')
    gecko_location = input('What is the location of geckodriver.exe? ')
    cred_write.write('Geckodriver Location = ' + gecko_location)
    cred_write.close()

if creds:
    writeCreds()
try:
    cred = open('recon.config', 'r').read().split('\n')
    for item in cred:
        item = item.split(' = ')
        if item[0] == ('Geckodriver Location'):
            gecko_location = item[1]
        elif item[0] == ('Hunter email'):
            hunter_un = item[1]
        elif item[0] == ('Hunter password'):
            hunter_pw = item[1]
except:
    print('Your recon.config folder is empty.  Please answer the following questions to fill it.')
    writeCreds()

br = False

if name1 != None:
    path = '.\\'
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file and 'setting' in file:
                files.append(os.path.join(r, file))
    try:
        y = open(name1 + '.txt', 'r')
    except:
        try:
            y = open('setting_' + name1 + '.txt', 'r')
        except:
            print('There is no setting file called: ' + name1)
    settings = y.read()
    settings = settings.split('\n')
    hunter_io = False
    dns_use = False
    whois_use = False
    mx_use = False
    he_use = False
    if settings[0] == 'True':
        hunter_io = True
    if settings[1] == 'True':
        dns_use = True
    if settings[2] == 'True':
        whois_use = True
    if settings[3] == 'True':
        mx_use = True
    if settings[4] == 'True':
        he_use = True
    y.close()

if name2 != None:
    path = '.\\'
    cont = 'y'
    for r, d, f in os.walk(path):
        for file in f:
            if 'setting_' + name2 in file:
                cont = input('There is already a setting named "' + name2 + '".  Do you want to overwrite it? [y/n] ')
    if cont == 'y':
        if name2[:3] == 'setting_':
            y = open(name2 + '.txt', 'w')
        else:
            y = open('setting_' + name2 + '.txt', 'w')
        y.write(str(hunter_io))
        y.write('\n' + str(dns_use))
        y.write('\n' + str(whois_use))
        y.write('\n' + str(mx_use))
        y.write('\n' + str(he_use))
        y.close()
    else:
        print("OK")
        br = True
if not br:
    driver = webdriver.Firefox(executable_path=gecko_location)

try:
    if dns_use:
        driver.get("https://dnsdumpster.com")
        open_tabs += 1
        time.sleep(2)
        driver.find_element_by_id('regularInput').send_keys(customer_address)
        driver.find_element_by_class_name('btn').click()
        ttimes = 0
        for item in driver.find_elements_by_class_name('col-md-3'):
            if ttimes % 2 == 0:
                text = item.text
                dns_list.append(text)
            ttimes += 1

        for item in dns_list:
            item1 = item.split('\n')
            ip.write(item1[0] + '\n')
except:
    if not br:
        print('Sorry, there was an error with dnsdumpster.')


def whois_org():
    try:
        item_list = []
        main_div = driver.find_element_by_id('maincontent')
        for item1 in main_div.find_elements_by_tag_name('a'):
            item_list.append(item1.text)
        for item1 in item_list:
            driver.get('https://whois.arin.net/rest/customer/' + item1)
            time.sleep(2)
            tables = driver.find_elements_by_tag_name('table')
            try:
                item = tables[1].find_element_by_tag_name('a').text
                ip.write(item + '\n')
            except:
                pass
    except:
        if not br:
            print('Sorry, there was an error with Whois Arin.')

try:
    if whois_use:
        if open_tabs > 0:
            driver.execute_script('''window.open("https://whois.arin.net/ui/advanced.jsp");''')
            driver.switch_to.window(driver.window_handles[open_tabs])
            open_tabs += 1
        else:
            driver.get("https://whois.arin.net/ui/advanced.jsp")
        time.sleep(2)

        def run_arin(second):
            driver.get('https://whois.arin.net/ui/advanced.jsp')
            driver.find_element_by_id('q').send_keys(customer_address)
            times = 1
            org = False
            for item in driver.find_elements_by_tag_name('input'):
                if times == 18 and not second:
                    item.click()
                    driver.find_element_by_id('submitQuery').click()
                    org = True
                elif times == 21 and second:
                    item.click()
                    driver.find_element_by_id('submitQuery').click()
                    whois_org()
                    break
                if org:
                    whois_org()
                times += 1


        run_arin(False)
        run_arin(True)
except:
    if not br:
        print('Sorry, there was an error with Whois Arin.')

try:
    if mx_use:
        if open_tabs > 0:
            driver.execute_script('''window.open("https://mxtoolbox.com/");''')
            driver.switch_to.window(driver.window_handles[open_tabs])
            open_tabs += 1
        else:
            driver.get("https://mxtoolbox.com/")
        time.sleep(4)
        driver.find_element_by_id('ctl00_ContentPlaceHolder1_ucToolhandler_txtToolInput').send_keys(customer_address)
        driver.find_element_by_id('ctl00_ContentPlaceHolder1_ucToolhandler_btnAction').click()
        time.sleep(5)
        times = 0
        for item in driver.find_elements_by_class_name('table-column-IP_Address'):
            ip.write(item.find_element_by_tag_name('a').text + '\n')
            times += 1
except:
    if not br:
        print('Sorry, there was an error with mx toolbox.')

try:
    if he_use:
        if open_tabs > 0:
            driver.execute_script('''window.open("https://bgp.he.net/ip");''')
            driver.switch_to.window(driver.window_handles[open_tabs])
            open_tabs += 1
        else:
            driver.get("https://bgp.he.net/ip")
        time.sleep(2)
        driver.find_element_by_id('search_search').send_keys(customer_address)
        times = 0
        times1 = 0
        item_list = []
        time.sleep(2)
        for item in driver.find_elements_by_tag_name('input'):
            if times == 1:
                item.click()
                time.sleep(2)
                for item1 in driver.find_elements_by_class_name('dnsdata'):
                    if times1 == 4:
                        for item2 in item1.find_elements_by_tag_name('a'):
                            item_list.append(item2.text)
                    times1 += 1
                for item1 in item_list:
                    driver.get('https://bgp.he.net/ip/' + str(item1))
                    try:
                        ip.write('Net Block: ' + driver.find_element_by_class_name('nowrap').find_element_by_tag_name('a').text + '\n')
                    except:
                        pass
            times += 1
except:
    if not br:
        print('Sorry, there was an error with Hurricane Electric.')

try:
    if hunter_io:
        if open_tabs > 0:
            driver.execute_script('''window.open("https://hunter.io/search");''')
            open_tabs += 1
            driver.switch_to.window(driver.window_handles[open_tabs])
        else:
            driver.get("https://hunter.io/search")
        time.sleep(2)
        driver.find_element_by_id('email-field').send_keys(hunter_un)
        driver.find_element_by_id('password-field').send_keys(hunter_pw)
        time.sleep(1)
        driver.find_element_by_class_name('btn-orange').click()
        time.sleep(1)
        driver.find_element_by_id('domain-field').send_keys(customer_address)
        driver.find_element_by_id('search-btn').click()
        time.sleep(3)

        dp = driver.find_element_by_class_name('domain-pattern')
        pattern = dp.find_element_by_tag_name('strong').text

        while True:
            try:
                driver.find_element_by_class_name('show-more').click()
                for item in driver.find_elements_by_class_name('email'):
                    if item not in emails.read().split('\n'):
                        emails.write(item.text + '\n')
            except:
                break
            time.sleep(1)
        emails.close()
except:
    try:
        quota = driver.find_element_by_class_name('board-box')
        print("You don't have enough searches on Hunter.")
    except:
        try:
            login = driver.find_element_by_class_name('alert')
            print("You entered the wrong credentials.")
        except:
            if not br:
                print('Sorry, there was an error with Hunter.')

times = 1
global tt
tt = 0
try:
    if whois_use:
        driver.execute_script('''window.open("https://whois.arin.net/ui/advanced.jsp");''')
        while tt < len(customer):
            driver.get("https://whois.arin.net/ui/advanced.jsp")
            time.sleep(2)

            def run_arin(second):
                driver.find_element_by_id('q').send_keys(customer[tt])
                times = 1
                times_pic = 0
                item_list = []
                for item in driver.find_elements_by_tag_name('input'):
                    if times == 18 and not second:
                        item.click()
                        driver.find_element_by_id('submitQuery').click()
                        whois_org()
                    elif times == 21 and second:
                        item.click()
                        driver.find_element_by_id('submitQuery').click()
                        whois_org()
                        break
                    elif times == 21:
                        run_arin(True)
                        break
                    times += 1


            run_arin(False)
        tt += 1
except:
    if not br:
        print('Sorry, there was an error with Whois Arin.')

try:
    tt = 0
    if he_use:
        driver.execute_script('''window.open("https://bgp.he.net/ip");''')
        while tt < len(customer):
            driver.get("https://bgp.he.net/ip")
            time.sleep(2)
            driver.find_element_by_id('search_search').send_keys(customer[tt])
            times = 0
            times1 = 0
            item_list = []
            time.sleep(2)
            for item in driver.find_elements_by_tag_name('input'):
                if times == 1:
                    item.click()
                    time.sleep(2)
                    for item1 in driver.find_elements_by_class_name('dnsdata'):
                        if times1 == 4:
                            for item2 in item1.find_elements_by_tag_name('a'):
                                item_list.append(item2.text)
                        times1 += 1
                    for item1 in item_list:
                        driver.get('https://bgp.he.net/ip/' + str(item1))
                        ip.write('Net Block: ' + driver.find_element_by_class_name('nowrap').find_element_by_tag_name('a').text + '\n')
                times += 1
        tt += 1
except:
    if not br:
        print('Sorry, there was an error with Hurricane Electric.')

ip.close()

