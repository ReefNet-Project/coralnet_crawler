import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
import re  
import os
import logging
from dotenv import load_dotenv

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()


def dowload_source_annotations(session, source_name, source_url):
    logging.info(f'Downloading annotations for source {source_name}')
    response = session.get(source_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract CSRF token
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    url = f'{source_url}export/annotations/'

    payload = {
        'optional_columns': ['annotator_info', 'machine_suggestions', 'metadata_date_aux', 'metadata_other'],
        'csrfmiddlewaretoken': csrf_token,
    }

    headers = {
        'Referer': url
    }
    # Send POST request with credentials and CSRF token
    response = session.post(url, data=payload, headers=headers)

    # Check if login was successful
    if response.ok:
        logging.info('download successful')
        # After submitting the form, handle the response
        # This might include downloading a file if the response is a file
        if response.headers.get('Content-Disposition'):
            # Create the folder if it doesn't exist
            if not os.path.exists(f'output/{source_name}'):
                os.makedirs(f'output/{source_name}')

            annotations_path = os.path.join(f'output/{source_name}', 'annotations.csv')
            # Write it to a local file in the specified folder
            with open(annotations_path, 'wb') as file:
                file.write(response.content)
    else:
        logging.error('download failed')
    return 

def main():
    logging.info("Starting downloading process")

    # Authentication logic here
    # Create a session and login
    session = requests.Session()

    # Get the login page to retrieve CSRF token
    login_url = 'https://coralnet.ucsd.edu/accounts/login/'
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the CSRF token value
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    # Login credentials with CSRF token
    payload = {
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD'),
        'stay_signed_in': 'on',
        'csrfmiddlewaretoken': csrf_token
    }

    # Headers
    headers = {
        'Referer': login_url
    }

    # Send POST request with credentials and CSRF token
    response = session.post(login_url, data=payload, headers=headers)

    if response.ok:
        df = pd.read_csv('sources_data.csv')
        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            source_name = row['Source']
            source_url = row['URL']
            # dowload annotations for the source 
            dowload_source_annotations(session, source_name, source_url)
    else:
        logging.error("Login failed")
        return
    
    logging.info("Script finished")
    return


if __name__ == "__main__":
    main()