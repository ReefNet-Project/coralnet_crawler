import pandas as pd
import requests



df = pd.read_csv('metadata.csv')
imageList = df['Name']
print(imageList[0:3])
numImages = imageList.size
print('Number of Images: ',numImages)


# assumes Images directory already exists
%cd Images
# get images from coralnet website by parsing source code
searchList = imageList
k = 0 # number of images found
baseURLnumber = 134549
runOnce = 0

for n in range(numImages):
  # luckily the images are stored on pages with numerically increasing paths
  # url of first image: https://coralnet.ucsd.edu/image/134549/view/
  # url of last image: https://coralnet.ucsd.edu/image/134938/view/
  page_url = 'https://coralnet.ucsd.edu/image/' + str(baseURLnumber + n) + '/view/'
  # grab the source code
  r = requests.get(page_url)
  source = r.text
  # now search the source code for the images from our annotations list
  # we remove the image from the search list once we find it,
  # so the size of searchList should reduce as n increases
  for i, name in enumerate(searchList):
    if source.find(name) > 0:
    # we found the image name. Now find the image download URL, based on some sleuthing of the HTML.
    # it should contain a Signature, Expiration, and AWSAccessKeyId
    img_url = re.search(r'coralnet-production.s3.amazonaws.com:443(.*?)>', source).group(1)
    url = 'https://coralnet-production.s3.amazonaws.com' + img_url
    # fix some formatting
    url = url.replace('&amp;', '&')
    url = url.replace('" /', '')
    # now get the image from the URL
    r = requests.get(url, allow_redirects=True)
    # write it to a local file
    open(name, 'wb').write(r.content)
    # remove that name from searchList so we don't search for it again
    searchList.drop(searchList.index[i])
    # increment the number of images we have found
    k = k + 1
    if runOnce == 1:
      break
print('found', k, 'images.')