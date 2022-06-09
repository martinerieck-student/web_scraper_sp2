#! python3

# Importing modules
from urllib.request import Request, urlopen
import requests
# import html5lib
from bs4 import BeautifulSoup
import pymysql
import datetime

# Root link is used to establish the base for the next page link to be able to run the program infinitely.
root = "https://www.google.com/"
# This is the link that Google provided while doing a search for the relevant keywords, and will be used for the initial
# scrape.
link = "https://www.google.com/search?q=%22ukraine%22%2B%22Anonymous%22%2B%22cyber%22&source=lmns&tbm=nws&bih=1279&biw=1718&hl=en&sa=X&ved=2ahUKEwiggeHK_8f3AhWpBxAIHVrHAiMQ_AUoAnoECAEQAg"


def news(link):
    # Prerequisites, request and sessions
    req = Request(link, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(req).read()
    with requests.Session() as c:
        soup = BeautifulSoup(webpage, "html5lib")

        # Creating list
        records = []
        # Finding attributes from inspecting Google News site
        for item in soup.find_all('div', attrs={'class': 'ZINbbc luh4tb xpd O9g5cc uUPGi'}):
            # Finding the raw link in Google Metadata from running Beautiful soup (B4S)
            raw_link = (item.find('a', href=True)['href'])

            # Stripping links of any Google related redirects (everything after &sa=U&) and save to "Link" variable
            link = (raw_link.split("/url?q=")[1]).split('&sa=U&')[0]

            # Pulling title though attributes from Google Meta running B4S
            title = (item.find('div', attrs={'class': 'BNeawe vvjwJb AP7Wnd'}).get_text())

            # Pulling description/bio/byline from Google Meta from running B4S
            description = (item.find('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'}).get_text())

            # Formatting: Replacing unnecessary commas and characters that can create issues and save to variable "f_x"
            f_title = title.replace(",", "-")
            f_description = description.replace(",", "-")

            # Pulling Time attribute from Google Meta from running B4S
            time = (item.find('span', attrs={'class': 'xUrNXd UMOHqf'}).get_text())
            # Find scrape date (date when this script is running)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            records = date, time, f_title, f_description, link

            print(records)

            source_db = pymysql.connect(host='localhost', user='py', password='GqxWbRv2593e', database='SOURCES')

            # Prepare cursor object for MySql
            cursor = source_db.cursor()

            # Create table is not exists (MySql) if running for another type of scrape, where a new table is needed.
            # cursor.execute("""CREATE TABLE IF NOT EXISTS ruc_sources(
            # date VARCHAR(30),
            # news_time VARCHAR(30),
            # news_title varchar(255),
            # bio text,
            # link text
            # );""")

            # SQL Insert statement into specific DB table (table name might be changed)
            sql = """INSERT INTO rucyb_sources (scrape_date, news_time, news_title, bio, link)\
                     VALUES (%s, %s, %s, %s, %s)"""

            # Executing the insert statement with the records scraped
            cursor.execute(sql, records)
            source_db.commit()
            print("Records have successfully been inserted to table.")

        # Find the next page button and associated link
        next_page = soup.find('a', attrs={'aria-label': 'Next page'})
        # Strip link and store in variable
        next_page = (next_page['href'])
        # Create new search link to scrape from root plus stripped next page link
        link1 = root + next_page
        # Run the function again until there are no more pages
        news(link1)


# Kicking off the program in an infinite loop until it has looped oer every page available on google.
news(link)
