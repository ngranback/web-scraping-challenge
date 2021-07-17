from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
from flask import Flask, render_template





app = Flask(__name__)
@app.route("/scrape")
def scrape():


    # ---------------
    # MARS NEWS
    # ---------------
    print('Gathering latest news...')

    url1 = 'https://redplanetscience.com/'  
    driver = webdriver.Chrome('C:/Users/nella/BOOTCAMP/chromedriver') 
    driver.get(url1) 

    # Retrieve snapshot of website
    time.sleep(5) 
    html1 = driver.page_source
    driver.close()


    # Translate it
    soup1 = BeautifulSoup(html1, 'html.parser')

    latest_title = soup1.find('div', class_='content_title').text
    latest_date = soup1.find('div', class_='list_date').text
    latest_blurb = soup1.find('div', class_='article_teaser_body').text

    # Store information about latest article in dictionary
    latest_dict = {
        'Latest Article Title': latest_title,
        'Latest Article Date': latest_date,
        'Latest Article Blurb': latest_blurb
    }


    # ---------------
    # FEATURED IMAGE
    # ---------------
    print('Grabbing featured image...')

    # Setup splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    url2 = 'https://spaceimages-mars.com/'
    browser.visit(url2)
    browser.links.find_by_partial_text('FULL IMAGE').click()

    html2 = browser.html
    soup2 = BeautifulSoup(html2, 'html.parser')
    browser.close()

    src = soup2.find('img', class_='fancybox-image')['src']
    featured_image_url = url2 + src


    # ---------------
    # MARS FACTS
    # ---------------
    print('Gathering fun facts...')

    url3 = 'https://galaxyfacts-mars.com/'

    all_tables = pd.read_html(url3)
    facts_table = all_tables[1]

    facts_html = facts_table.to_html()
    facts_html = facts_html.replace('\n','')


    # ---------------
    # HEMISPHERE PICS
    # ---------------
    print('Grabbing photos...')

    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    url4 = 'https://marshemispheres.com/'
    browser.visit(url4)
    html4 = browser.html
    soup4 = BeautifulSoup(html4, 'html.parser')

    # list of elements to loop through
    items = soup4.find_all('div', class_='item')

    # initialize empty list to fill with dictionaries
    hemisphere_image_urls  = []

    for i in range(4):
        browser.links.find_by_partial_text('Hemisphere')[i].click()

        item_title = items[i].div.a.text
        item_title = item_title.replace(' Enhanced', '')
        item_title = item_title.replace('\n', '')
        
        temp_html = browser.html
        temp_soup = BeautifulSoup(temp_html, 'html.parser')
        downloads = temp_soup.find('div', class_='downloads')
        # the url comes in 2 parts
        img_url = downloads.ul.li.a['href']
        temp_url = browser.url
        
        # create dictionary
        item_dict = {'title': item_title, 'img_url': temp_url + img_url}
        # insert dictionary into list
        hemisphere_image_urls.append(item_dict)
        
        
        #return to previous page to click the next link
        browser.back()
        
    browser.quit()


    # --------------
    # Create final dictionary
    # --------------

    return_dict = {
        'Latest Article Info': latest_dict,
        'Featured Image': featured_image_url,
        'Mars Facts (html)': facts_html,
        'Hemisphere Photos': hemisphere_image_urls, 
    }

    
    # connect to Mongo 

    client = MongoClient('mongodb+srv://mongo:mongo@ngranback.bmasa.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    NLG_DB = client['NLG_DB']
    mars_scrape_collection = NLG_DB['Mars_Scrape']

    mars_scrape_collection.insert_many(return_dict)





