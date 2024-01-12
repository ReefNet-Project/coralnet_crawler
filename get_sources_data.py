# get sources data and save into a csv file
# later each source images will downloaded based on the information gathered here 
# the information gathered from coralnet about the sources is based on the file sources.csv that contains the list of the sources that we should 
# scrape with the flag valid == 'yes'

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag


def get_source_images_number(source_url):
    page = requests.get(source_url)
    soup = BeautifulSoup(page.content, "html.parser")
    # Find the table with class 'detail_box_table'
    h3 = soup.find('h3', string='Image Status')

    if h3:
        table = h3.find_next_sibling('table', class_='detail_box_table')
        value = None
        # Find all <td> elements within this table
        if table:
            td_elements = table.find_all('td')
            for td in td_elements:
                if "Total images:" in td.get_text():
                    a_element = td.find('a')
                    if a_element:
                        # Extract the text and strip it to remove leading/trailing whitespace
                        value = a_element.get_text(strip=True)
                        return value

def get_source_first_image_number(source_images_url):
    page = requests.get(source_images_url)
    # Parse the HTML content
    soup = BeautifulSoup(page.content, 'html.parser')
    # Find the div with id 'content-container'
    content_div = soup.find('div', id='content-container')
    # Find the first 'a' element within this div
    first_a = content_div.find('a') if content_div else None
    # Extract the href attribute
    href = first_a['href'] if first_a else None
    source_first_image_number = int(href.split('/')[2])
    return source_first_image_number


def main():
    df = pd.read_csv('sources.csv')
    df = df[['Source', 'Valid']]

    # Create a boolean mask for valid data
    mask_valid = df['Valid'] == 'yes'

    df.loc[mask_valid, 'URL'] = None
    df.loc[mask_valid, 'ImagesURL'] = None
    df.loc[mask_valid, 'ImagesNumber'] = None
    df.loc[mask_valid, 'FirstImageNumber'] = None
    df_valid = df[mask_valid].copy()

    home_url = 'https://coralnet.ucsd.edu/source/about/'
    page = requests.get(home_url)
    soup = BeautifulSoup(page.content, "html.parser")
    URL = 'https://coralnet.ucsd.edu'
    sources_list = soup.find_all("ul", {"class": "object_list"})[0].children

    j = 0
    for child in sources_list:
        if isinstance(child, Tag):
            # Find the a element within the li element
            a_element = child.find('a')
            if a_element:
                # Extract the href attribute and text
                href = a_element.get('href')
                text = a_element.get_text()
                row_indices = df_valid[df_valid['Source'] == text].index
                # Check if row_indices is empty
                if row_indices.empty:
                    continue
                else:
                    j+=1
                    print(f'****************** found {j} ******************')
                    source_url =  URL + href
                    source_images_url = URL + href +'browse/images/'
                    # get the total number of images 
                    print(f'source_url {source_url}')
                    source_images_number = get_source_images_number(source_url)
                    print(f'source_images_number {source_images_number}')
                    source_first_image_number = get_source_first_image_number(source_images_url)
                    print(f'source_first_image_number {source_first_image_number}')
                    df_valid.loc[row_indices, ['URL', 'ImagesURL', 'ImagesNumber', 'FirstImageNumber']] = [source_url, source_images_url, source_images_number, source_first_image_number]


    df_valid.to_csv('output.csv', index=False)

    return


if __name__ == "__main__":
    main()