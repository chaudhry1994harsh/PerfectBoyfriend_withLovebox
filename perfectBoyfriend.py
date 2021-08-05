import schedule
import time 
from PIL import Image, ImageDraw
import textwrap
import base64
import json
import requests
import random
import io
import yaml

'''
parts that can be configured
API request that gets the quote 
text wrap size sets min line buffer horizontal 
min line buffer for vertical
quotes file name 
'''
#W H = 1280×960


def drawImage(msg, subscription):
    W, H = (320,240)
    im = Image.new("RGBA",(W,H),"black")
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(msg[0])
    align = 'odd' if len(msg) == 1 else 'even'
    if align == 'even': 
        baseline = (H-h)/2 - (len(msg) * 14)/2  
        for line in msg:
            w, h = draw.textsize(line)
            draw.text(((W-w)/2,baseline), line, fill="white")
            baseline = baseline + 14
    else:
        baseline = (H-h)/2 - (len(msg) * 14)/2 + 7  
        for line in msg:
            w, h = draw.textsize(line)
            draw.text(((W-w)/2,baseline), line, fill="white")
            baseline = baseline + 14
    if subscription is False:
        line = "theysaidso.com"
        draw.text((225,220), line, fill="white")
    with io.BytesIO() as output:
        im.save(output, format="GIF")
        contents = output.getvalue()
    return im, contents

def get_quote():
    URL = "http://quotes.rest/qod.json?category=love"
    r = requests.get(URL)
    resp = r.json()
    resp = {"quote":resp['contents']['quotes'][0]['quote'], "author":resp['contents']['quotes'][0]['author']}
    return resp

def getJson_storedQuotes():
    with open('quotes.json','r') as json_file:
        quotes = json.load(json_file)
    return quotes


def create_message(resp):
    quote = textwrap.wrap(resp['quote'], 45)
    validity = False if 220<= len(quote)*14 else True
    storedQuotes = getJson_storedQuotes()
    if validity == True and resp not in storedQuotes: 
        storedQuotes.append({"quote":resp['quote'], "author":resp['author']})
        type(storedQuotes)
        with open('quotes.json', 'w') as json_file:
            json_file.write(json.dumps(storedQuotes))
        return quote
    else: 
        quote = storedQuotes[random.randint(0, len(storedQuotes)-1)]["quote"]
        quote = textwrap.wrap(quote,45)
        return quote

def encodeMessage_base64(message):
    encoded_message = base64.b64encode(message)
    #encoded_message = base64.b64encode(message.tobytes())
    return encoded_message

def check_drawEncoded(encoded_message):
    #lol = base64.standard_b64decode(encoded_message)
    lol = base64.b64decode(encoded_message)
    img = Image.frombytes('RGBA', (320,240), lol, 'raw')
    #img = base64.decodebytes(example)
    img.show()

def create_payload(msg, recipient, deviceID):
    with open('postFormat.json','r') as json_file:
        op = json.load(json_file)
    op['variables']['base64'] = msg.decode('ascii')
    op['variables']['recipient'] = recipient
    op['variables']['options']['deviceId'] = deviceID
    return op

def send_love(payload,auth):
    url = 'https://app-api.loveboxlove.com/v1/graphql'
    header = {'Connection':'keep-alive','Content-Type':'application/json', 'Authorization': auth}
    response = requests.post(url, headers=header, json=payload)
    return response


def perfBoyfriend():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)
    resp = get_quote()
    #resp
    msg = create_message(resp)
    #msg
    img, img_toEncode = drawImage(msg, config['subscription'])
    #img.show()
    encoded_message = encodeMessage_base64(img_toEncode)
    #check_drawEncoded(encoded_message)
    payload = create_payload(encoded_message, config['recipient'], config['deviceID'])
    #payload
    response = send_love(payload,config['authorisation'])
    #response
    #response.json()
    #response.content    



def checker():
    print("lol checked")

schedule.every(10).seconds.do(checker)
schedule.every().day.do(checker)

while True:
    schedule.run_pending()
    time.sleep(18000)
