import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
import re  
import os
import logging

# Basic logging configuration
# logging.basicConfig(filename='scrape_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dowload_source_images(source_name ,images_number, first_image_number):
    logging.info(f"Downloading images for {source_name} from {first_image_number} to {first_image_number + images_number - 1}")
    page_url = 'https://coralnet.ucsd.edu/image/' + str(first_image_number) + '/view/'

    for n in range(images_number):
        logging.info(f"page_url : {page_url}")
        logging.info(f"Downloading image {page_url.split('/')[4]} from {source_name}, URL: {page_url} ")
        # grab the source code
        r = requests.get(page_url)
        soup = BeautifulSoup(r.content, "html.parser")
        # get image name 
        # Find the <a> element inside the <h2> tag within the div with id 'header'
        a_element = soup.find('div', id='header').find('h2').find_all('a')[1]
        image_name = a_element.get_text()

        # Full path for the image
        image_path = os.path.join(f'output/{source_name}/images', image_name)
        if os.path.exists(image_path):
            logging.info(f"Image {page_url.split('/')[4]}, name {image_name} already exists in {source_name}")
            continue

        # Find the <div> with id 'original_image_container'
        div_container = soup.find('div', id='original_image_container')

        # Find the <img> element within this <div>
        img_element = div_container.find('img')
        # Extract the 'src' attribute value
        url = img_element['src'] if img_element else None
        # fix some formatting
        url = url.replace('&amp;', '&')
        url = url.replace('" /', '')
        # now get the image from the URL
        r = requests.get(url, allow_redirects=True)
        # Create the folder if it doesn't exist
        if not os.path.exists(f'output/{source_name}/images'):
            os.makedirs(f'output/{source_name}/images')

        
        # Write it to a local file in the specified folder
        with open(image_path, 'wb') as file:
            file.write(r.content)
        
        # Find the <ul> element with class 'detail_list'
        ul_element = soup.find('ul', class_='detail_list')

        # Find the <a> element that contains the text 'Next'
        next_a_element = ul_element.find('a', string=lambda t: t and 'Next' in t)

        # Extract href attribute if the element is found
        next_image_url = next_a_element['href'] if next_a_element else None

        logging.info(f"Downloading Finished for image {page_url.split('/')[4]} from {source_name} ")

        page_url = f'https://coralnet.ucsd.edu{next_image_url}'

    return

def main():
    logging.info("Starting downloading process")
    df = pd.read_csv('sources_data.csv')
    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        source_name = row['Source']
        images_number = row['ImagesNumber']
        first_image_number = row['FirstImageNumber']
        if os.path.exists(f'output/{source_name}/images'):
            logging.info(f"Folder for {source_name} already exists")
            # compare the number of images in the folder with the images_number in the csv file
            folder_images_number = len(os.listdir(f'output/{source_name}/images'))
            if folder_images_number == images_number:
                logging.info(f"Folder for {source_name} already contains the correct number of images")
                continue
        # dowload images for the source 
        dowload_source_images(source_name ,images_number, first_image_number)
    
    logging.info("Script finished")
    return


if __name__ == "__main__":
    main()