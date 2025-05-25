import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
import re  
import os
import logging
from dotenv import load_dotenv
from time import sleep

load_dotenv()

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a file handler which logs even debug messages
fh = logging.FileHandler('scrape_annotations.log', mode='w')
fh.setLevel(logging.DEBUG)  # Set the level for the file handler

# Create a console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Set the level for the console handler

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def dowload_source_annotations(session, source_name, source_url, csrf_token):
    annotations_path = os.path.join(f'metadata/{source_name}', 'annotations.csv')
    if os.path.exists(annotations_path):
        logger.info(f"Annotations file for source {source_name} already exists")
        return
    else:
        logger.info(f'Downloading annotations for source {source_url}')
        r = None
        try:
            r = session.get(source_url, timeout=30)
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")

        
        soup = BeautifulSoup(r.text, 'html.parser')

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

        response = None
        try:
            # Send POST request with credentials and CSRF token
            response = session.post(url, data=payload, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")


        # Check if login was successful
        if response is not None and response.ok:
            logger.info('download successful')
            # After submitting the form, handle the response
            # This might include downloading a file if the response is a file
            if response.headers.get('Content-Disposition'):
                # Create the folder if it doesn't exist
                if not os.path.exists(f'metadata/{source_name}'):
                    os.makedirs(f'metadata/{source_name}')

                # Write it to a local file in the specified folder
                with open(annotations_path, 'wb') as file:
                    file.write(response.content)
        else:
            logger.error('download failed')

        return 

def main():
    logger.info("Starting downloading process for annotations")

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
        logger.info('login successfully')
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the CSRF token value
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        df = pd.read_csv('sources_data _ann.csv')
        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            source_name = row['Source']
            source_url = row['URL']
            # dowload annotations for the source 
            dowload_source_annotations(session, source_name, source_url, csrf_token)
    else:
        logger.error("Login failed")
        return
    
    logger.info("Script finished")
    return


if __name__ == "__main__":
    main()