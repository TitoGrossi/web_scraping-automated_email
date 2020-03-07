import requests
from bs4 import BeautifulSoup
from csv import reader

def handle_pagination(page, titles):
    # Function to handle pagination, if there is any

    # Gettin pagination of current page
    pagination = page.find('ul', class_='pagination')
    if pagination:
        # Making sure the next page button is active
        next_page_button = pagination.find('ul', class_='pagination')
        while next_page_button: # While the button is active
            # Get the respose of the url
            next_page = requests.get(next_page_button.find('a')['href'])
            soup = BeautifulSoup(next_page.content, 'html.parser')
            # Find all the titles (which have links to the publication itself) of the page
            # search for publications related to ANTAQ
            titles.extend(soup.find_all('h5', class_='title-maker'))
            handle_pagination(soup, titles)
    return titles

def enter_page(page_url):
    # Function to get the page of the pbulications
    # response and return that or a error message
    page = requests.get(page_url)
    if page.status_code == 200: # If response was ok, return page
        return page
    else: # Else, return error message
        return 'Could not access {}'.format(page_url)

def create_pub_message(page):
    # Parse through the page
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get first informations (title and identification)
    title = soup.find('h2', {'class': 'cabecalho-titulo-dou'})
    identification = soup.find('p', {'class': 'identifica'})

    # Get every detail
    details_pub = soup.find_all('p', {'class': 'text-center'})

    # Get every paragraph
    paragraphs = soup.find_all('p', {'class': 'dou-paragraph'})

    # Create string with some divs and styles alongside for better visualization
    html_message = ['''
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
      <head>
        <meta charset="utf-8">
        <title></title>
      </head>
      <body>
    ''']

    html_message.append('<div style="background-color:#b8b8cf;margin-bottom:150px">')
    html_message.append('''\
    <h1 style="text-align:center;font-family:'Times New Roman';color:black">{}</h1>'''.format(title.text))

    html_message.append('<div style="text-align:center">')
    for detail in details_pub[:7]:
        html_message.append('''
        <p style="color:black">{}</p>'''.format(detail.text))
    html_message.append('</div>')

    for detail in details_pub[7:]:
        html_message.append('''
        <p style="color:black">{}</p>'''.format(detail.text))

    for paragraph in paragraphs:
        html_message.append('''\
        <p style="font-family:'Arial Black';text-indent:40px;color:black;text-align:justify">{}</p>
        '''.format(paragraph.text))


    # Join message as one string
    html_message = ''.join(html_message)

    # Return the really long string
    return html_message

def get_email_list(file):
    with open(file, newline='') as f: # Opening file
        # Create reader instance, passing file
        email_list_csv = reader(f, delimiter=';')
        # Get first column, which should have the email adresses
        email_list = next(email_list_csv)
        for email in email_list: # For each email adress
            if type(email) != str or email == '': # If somebody messed up and left an entry empty
                #Delete the email from the list
                email_list.remove(email)
        # Return email_list
        return email_list
