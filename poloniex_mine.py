### Mine the text comments from the Poloniex trollbox, and the coin prices in BTC
#
# Scrapes the trollbox once every minute (can be changed to a different
# amount of time) and write all comments to a txt file
# 
# Also at that time, scrapes all the coin prices for all coins in BTC
# values and writes these to a file
#
# Comments and coin prices are later explored in a sentiment analysis,
# to see if comments can be useful for price prediction

### Mandatory pre-rec: 
# Pre-recs are all for OSX
# Install BeautifulSoup and selenium for Python on command line:
#   pip3 install beautifulsoup4
#   sudo easy_install selenium
# Place phantomjs.exe in python default directory.

# Import the packages
import platform
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import time
from datetime import datetime
from itertools import zip_longest


# Version Windows check (checking if Windows or OSX)
if platform.system() == 'Windows':
    PHANTOMJS_PATH = './phantomjs.exe'
else:
    PHANTOMJS_PATH = './phantomjs'

    
### Main function: loop this part every minute
def execute():
    os.chdir('/Users/me')
    #Boot up the phantom browser    
    browser = webdriver.PhantomJS(PHANTOMJS_PATH)
    #Browse to the website
    browser.get('https://www.poloniex.com/trollbox')
    #Scrape that post-javascript HTML 
    source = BeautifulSoup(browser.page_source, "html.parser")
    #Identifies the table with chat content, ids, usernames
    rawhtmltext = source.findAll('table')[0].tbody.findAll('tr')
    rawhtmltext = str(rawhtmltext)
    # actual text is between “strong>” and “</td” 
    p = re.compile('</strong>(.*?)</td')
    rawtext = p.findall(rawhtmltext)
    # remove any image filenames (bans) from the list of strings:
    keywordFilter = set(['<strong>'])
    rawtext = [str for str in rawtext if not any(i in str for i in keywordFilter)]
    # Save gathered text to file with the date and time:
    os.chdir('/Users/me/Documents/trollboxtext')
    filename = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(filename,'w') as f:
        f.write( ','.join( rawtext ) )
    ### In another directory, store the price in BTC for this date and time
    ### Go to the website (usdt_ltc just to be constant, grabbing BTC from
    ### this page though)
    browser.get('https://www.poloniex.com/exchange#usdt_ltc')
    time.sleep(1)
    source = BeautifulSoup(browser.page_source, "html.parser")
    # turn the page html into a string
    source = str(source)
    # find all the coin prices
    p = re.compile('class="coin">(.*?)</td><td class="volume')
    rawprices = p.findall(source)
    # Just want the prices in BTC, so removing the ETH and USD prices
    alpha_rawprices = sorted(rawprices)
    # Remove the duplicate prices from the page
    o = []
    q = 'start'
    for n in alpha_rawprices:
        if n[0:4] == q[0:4]:
            continue
        o.append(n)
        q = n
    # Now duplicates are gone, remove the extra HTML in the middle
    prices = []
    for x in o:
        prices.append(x.replace('</td><td class="price">',' '))
    browser.close()
    browser.quit()
    os.chdir('/Users/me/Documents/BTC_prices')
    filename = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(filename,'w') as f:
        f.write( ','.join( prices ) )

    # Do this every minute    
    time.sleep(60)

# Loop indefinitely
while True:
    execute()
