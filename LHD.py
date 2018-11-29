import requests
from PIL import Image
from io import BytesIO

from http.server import BaseHTTPRequestHandler,HTTPServer
import time

# Generate APIs
def get_apis():
    img_urls = []

    for i in range(2):
        got = False
        while not got:
            try:
                response = requests.get('https://api.publicapis.org/random')
                data = response.json()['entries'][0]

                print(data['API'])
                print(data['Description'])
                print(data['Link'])

                subscription_key = 'a22fc43ad9bf419faec653b51f8d7b03'
                assert subscription_key

                search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
                search_term = data['Description']

                headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
                params  = {
                    "q": search_term,
                    "license": "public",
                    "imageType": "photo"
                }

                response = requests.get(search_url, headers=headers, params=params)
                response.raise_for_status()
                search_results = response.json()

                img_url = search_results["value"][0]["thumbnailUrl"]
            except(IndexError):
                got = False
            else:
                got = True
                img_urls.append([
                    data['API'],
                    data['Description'],
                    data['Link'],
                    img_url
                ])

    return img_urls

# Server configuration
hostName = 'api-suggestions.herokuapp.com'
hostPort = 80

template = '''
<!DOCTYPE html>
<html>
<head>
<!--path: {}-->

<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API generator</title>
</head>
<body>

<h1 style="text-align: center;">Suggested APIs</h1>

<div style="width: 85%;margin: auto;">
<div style="box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);transition: 0.3s;width: 48%;height: 50%;border-radius: 5px;margin: auto;float: left;">
<div style="padding: 2px 16px;">
<h2><a href="{}">{}</a></h2>
<p>{}</p> 
</div>
<img src="{}" style="width:100%;border-radius: 5px 5px 0 0;">
</div>

<div style="box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);transition: 0.3s;width: 48%;height: 50%;border-radius: 5px;margin: auto;float: right;">
<div style="padding: 2px 16px;">
<h2><a href="{}">{}</a></h2>
<p>{}</p> 
</div>
<img src="{}" style="width:100%;border-radius: 5px 5px 0 0;">
</div>
</div>

</body>
</html> 
'''

error = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API generator</title>
</head>
<body>

<h1 style="text-align: center;">Are you looking for our <a href="/api/">APIs suggestions</a>?</h1>

</body>
</html> 
'''

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path == '/api/':
            img_urls = get_apis()
            self.wfile.write(bytes(template.format(
                self.path,
                img_urls[0][2],
                img_urls[0][0],
                img_urls[0][1],
                img_urls[0][3],
                img_urls[1][2],
                img_urls[1][0],
                img_urls[1][1],
                img_urls[1][3]
            ), 'utf-8'))
        else:
            self.wfile.write(bytes(error, 'utf-8'))


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))

# Comments
"""
# Show image in PIL plot
import matplotlib.pyplot as plt
img_data = requests.get(img_url)
img_data.raise_for_status()
image = Image.open(BytesIO(img_data.content))
img_plot = plt.imshow(image)
plt.axis('off')
plt.show()
"""
