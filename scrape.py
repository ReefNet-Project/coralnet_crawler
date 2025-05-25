import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
import re  
import os
import logging
from urllib.parse import urlparse, unquote
from time import sleep

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a file handler which logs even debug messages
fh = logging.FileHandler('scrape_logs.log', mode='w')
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


# a dictionary to keep track of the links last visited by the crawler
# this links will be used as a start point in the round
last_images = {}


def get_image_format_from_url(url):
    """
    Extracts the image format from a given image URL.
    """
    # Unquote the URL to handle any URL encoded characters
    url = unquote(url)

    # Extract the path part of the URL
    path = urlparse(url).path

    # Use a regular expression to find the file extension
    match = re.search(r'\.(\w+)(?=[^.]*$)', path)
    if match:
        return match.group(1)
    else:
        return None

def determine_image_format(image_name, image_url):
    """
    Determines the image format, checking the image name first,
    then extracting from the URL if necessary.
    """
    # Check if the image name already has a format
    if '.' in image_name and image_name.rsplit('.', 1)[1] in ['jpg', 'jpeg', 'png', 'gif', 'JPG']:
        return image_name
    else:
        return f'{image_name}.{get_image_format_from_url(image_url)}'
    

def dowload_source_images(source_name , first_image_number):
    page_url = ''
    # check last_images first to get the link of the last visited image and not start from the first_image_number
    if source_name in last_images:
        page_url = last_images[source_name]
        logger.info(f"Last image visited for {source_name} is {page_url}")
    else:        
        logger.info(f"Downloading images for {source_name} starting from {first_image_number}")
        page_url = 'https://coralnet.ucsd.edu/image/' + str(first_image_number) + '/view/'
        
    
    retries = 5
    while True:
        logger.info(f"Downloading image {page_url.split('/')[4]} from {source_name}, URL: {page_url} ")
        r = None  # Initialize r before the loop

        for i in range(retries):
            try:
                r = requests.get(page_url, timeout=30)
                break  # If the request was successful, break out of the loop
            except requests.exceptions.Timeout:
                logger.debug(f"Timeout, retrying... ({i+1}/{retries})")
                sleep(2 ** i)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                logger.error("Connection error")
            except requests.exceptions.RequestException as e:
                logger.error(f"An error occurred: {e}")

        
        # Check if r is still None after the loop
        if r is None or not r.ok:
            logger.error("Failed to retrieve the image page")
            logger.warning("Skipping to the next source")
            # save page_url to last_images for the next source
            last_images[source_name] = page_url
            return
        else:
            last_images[source_name] = page_url
            # Process the response here
            logger.info("Image Page Request successful.")
            soup = BeautifulSoup(r.content, "html.parser")
            # Find the <a> element inside the <h2> tag within the div with id 'header'
            a_element = soup.find('div', id='header').find('h2').find_all('a')[1]
            image_name = a_element.get_text()
            # Check if there are any slashes in the filename
            if '/' in image_name:
                image_name = image_name.replace('/', '_')
                logger.info(f"Slashes in image name, replaced with underscores: {image_name}")

            # Find the <div> with id 'original_image_container'
            div_container = soup.find('div', id='original_image_container')

            # Find the <img> element within this <div>
            img_element = div_container.find('img')
            # Extract the 'src' attribute value
            url = img_element['src'] if img_element else None
            # fix some formatting
            url = url.replace('&amp;', '&')
            url = url.replace('" /', '')

            safe_image_name = determine_image_format(image_name,url)
            logger.info(f"Image name: {image_name}, safe name: {safe_image_name}")

            # Full path for the image
            image_path = os.path.join(f'output/{source_name}/images', safe_image_name)

            if os.path.exists(image_path):
                logger.info(f"Image {page_url.split('/')[4]}, name {image_name} already exists in {source_name}")
            else:
                # now get the image from the URL
                r = requests.get(url, allow_redirects=True)
                # Create the folder if it doesn't exist
                if not os.path.exists(f'output/{source_name}/images'):
                    os.makedirs(f'output/{source_name}/images')

                # Write it to a local file in the specified folder
                with open(image_path, 'wb') as file:
                    file.write(r.content)
                
                logger.info(f"Downloading Finished for image {page_url.split('/')[4]} from {source_name} ")

            # Find the <ul> element with class 'detail_list'
            ul_element = soup.find('ul', class_='detail_list')

            # Find the <a> element that contains the text 'Next'
            next_a_element = ul_element.find('a', string=lambda t: t and 'Next' in t)
            # Check if the <a> element was found
            if not next_a_element:
                break

            # Extract href attribute if the element is found
            next_image_url = next_a_element['href'] if next_a_element else None

            page_url = f'https://coralnet.ucsd.edu{next_image_url}'

    return

# download all images from all sources in the sources_data.csv file
# check if the folder for the source already exists
# check if the folder contains the correct number of images
# if the folder exists and contains the correct number of images, skip to the next source
# if the folder doesn't exist, create it and download the images
def download_all_images(df):
    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        source_name = row['Source']
        images_number = row['ImagesNumber']
        first_image_number = row['FirstImageNumber']
        if os.path.exists(f'output/{source_name}/images'):
            logger.info(f"Folder for {source_name} already exists")
            # compare the number of images in the folder with the images_number in the csv file
            folder_images_number = len(os.listdir(f'output/{source_name}/images'))
            if folder_images_number >= images_number:
                logger.info(f"Folder for {source_name} already contains the correct number of images")
                continue
        # dowload images for the source 
        dowload_source_images(source_name, first_image_number)

    return


# check if all folders in the output folder have the correct number of images
def check_folders(df):
    # get the list of all folders from df["Source"] and check if they contain the right number of images
    folders = df["Source"].tolist()
    for folder in folders:
        folder_path = f'output/{folder}/images'
        if os.path.exists(folder_path):
            folder_images_number = len(os.listdir(folder_path))
            if folder_images_number != df.loc[df["Source"] == folder, "ImagesNumber"].iloc[0]:
                logger.error(f"Folder {folder} does not have the correct number of images")
                return False
        else:
            logger.error(f"Folder {folder} does not exist")
            return False
    
    return True  # return True if all folders have the correct number of images



def main():
    logger.info("Starting downloading process")
    while True:
        try:
            df = pd.read_csv('sources_data.csv')
            download_all_images(df)
            check = check_folders(df)
            if check:
                logger.info("All folders have the correct number of images")
                break
            else:
                continue  # retry if any folders does not have the correct number of images
        except FileNotFoundError:
            logger.error("sources_data.csv file not found")
            sleep(5)  # wait for 5 seconds before retrying
    
    logger.info("Script finished")
    return


if __name__ == "__main__":
    main()