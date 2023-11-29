import requests
import base64
import os

print('')

url = "https://api.imgur.com/3/image"

payload={'image': base64.b64encode(open('image.png', 'rb').read())}
files=[

]
# print(str(os.environ['imgur']))
headers = {
  'Authorization': 'Client-ID ' + os.environ['IMGUR']
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
