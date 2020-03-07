import os
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
from datetime import date
from auxiliary import create_pub_message, get_email_list, enter_page, handle_pagination

# Get the current date, adding a 0 in front of the month or day if either one of
# those is less than 10, in order to get the correct url
today = date.today()
if today.month > 9:
    month = today.month
else:
    month = '0{}'.format(today.month)

if today.day > 9:
    day = today.day
else:
    day = '0{}'.format(today.day)

today = '{}-{}-{}'.format(today.year, month, day)

# Url of the page on current data (taken from today variable) with 'ANTAQ' filter
dou_site_name = 'http://www.in.gov.br/consulta?q=antaq&publishFrom={date}&publishTo={date}&delta=75'.format(date=today)
# Get the response of the url
dou_site = requests.get(dou_site_name)
# BeautifulSoup object to parse through the page
soup = BeautifulSoup(dou_site.content, 'html.parser')

# Find all titles (which have links to the publications itself) of the page
# search for publications related to ANTAQ
titles = soup.find_all('h5', class_='title-marker')

# Now making sure if there is no pagination
if pagination: # If there is any (pagination not None)
    titles = handle_pagination(soup, titles)

# Create empty list
pubs = []
for title in titles:
    # For every link found, enter the page through its link
    page = enter_page(title.find('a')['href'])
    # Append the important informations of the page to pub, using the
    # create_pub_message function
    pubs.append(create_pub_message(page))
    # Also append the link to make accessing the page an easy job
    pubs.append('<p>Link: </p><a>{}</a>'.format(title.find('a')['href']))

# Join the message as one string
pubs = ''.join(pubs)

# Get the email adress and password which are stored on the enviroment variables
EMAIL_ADRESS = os.environ.get('LOGIN_EMAIL_AUTOMACAO')
EMAIL_PASS = os.environ.get('SENHA_EMAIL_AUTOMACAO')

# Instantiate EmailMessage object
msg = EmailMessage()
msg['From'] = EMAIL_ADRESS
# Get all receivers from the csv file email_list.csv
receivers = get_email_list('email_list.csv')
msg['To'] = ', '.join(receivers)
msg['Subject'] = 'Automacao - DOU - {}'.format(today)

msg.set_content('Plain text')

msg.add_alternative(pubs, subtype='html')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp: # Initiate section
    # Login
    smtp.login(EMAIL_ADRESS, EMAIL_PASS)
    # Send message
    smtp.send_message(msg)
