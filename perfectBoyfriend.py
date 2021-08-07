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
import os 

'''
parts that can be configured
API request that gets the quote 
text wrap size sets min line buffer horizontal 
min line buffer for vertical
quotes file name 
'''
#W H = 1280×960

print(time.strftime('%X %x %Z'))
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()
print(time.strftime('%X'))

def drawImage(msg, subscription, type):
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
    if subscription is False and type == "quote":
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
    storedQuotes = getJson_storedQuotes()
    if resp not in storedQuotes and len(resp["quote"])*14 <= 220:
        storedQuotes.append({"quote":resp['quote'], "author":resp['author']})
        with open('quotes.json', 'w') as json_file:
            json_file.write(json.dumps(storedQuotes))
        quote = resp["quote"]
        print("new quote")
    else:
        quote = storedQuotes[random.randint(0, len(storedQuotes)-1)]["quote"]
        print("old quote")
    quote = textwrap.wrap(quote,45)
    return quote

def getJson_storedQuotes():
    with open('quotes.json','r') as json_file:
        quotes = json.load(json_file)
    return quotes

def get_config():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)
    return config

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
    with open('payload.json','r') as json_file:
        op = json.load(json_file)
    op['variables']['base64'] = msg.decode('ascii')
    op['variables']['recipient'] = recipient
    op['variables']['options']['deviceId'] = deviceID
    return op

def send_request(payload,auth):
    url = 'https://app-api.loveboxlove.com/v1/graphql'
    header = {'Connection':'keep-alive','Content-Type':'application/json', 'Authorization': auth}
    response = requests.post(url, headers=header, json=payload)
    return response

def get_greeting(type):
    with open('greetings.json','r') as json_file:
        op = json.load(json_file)
    greeting = op[type]
    greeting = greeting[random.randint(0, len(greeting)-1)]
    greeting = textwrap.wrap(greeting,45)
    return greeting


def send_quotes():
    config = get_config()
    msg = get_quote()
    #msg
    img, img_toEncode = drawImage(msg, config['subscription'], "quote")
    #img.show()
    encoded_message = encodeMessage_base64(img_toEncode)
    #check_drawEncoded(encoded_message)
    payload = create_payload(encoded_message, config['recipient'], config['deviceID'])
    #payload
    response = send_request(payload,config['authorisation'])
    #response
    #response.json()
    #response.content    
    return schedule.CancelJob

def send_greeting(type):
    config = get_config()
    msg = get_greeting(type)
    #msg
    img, img_toEncode = drawImage(msg, config['subscription'], "greeting")
    #img.show()
    encoded_message = encodeMessage_base64(img_toEncode)
    #check_drawEncoded(encoded_message)
    payload = create_payload(encoded_message, config['recipient'], config['deviceID'])
    #payload
    response = send_request(payload,config['authorisation'])
    #response
    #response.json()
    #response.content    
    return schedule.CancelJob


def randomiser_timeofDay(eta):
    if eta == "morning":
        hr = random.randint(4,8)
        min = random.randint(0,60)
    elif eta == "night":
        hr = random.randint(22,23)
        min = random.randint(30,60)
    elif eta == "quote":
        hr = random.randint(12,18)
        min = random.randint(0,60)
    if hr < 10 : hr = "0"+str(hr)
    if min < 10 : min = "0"+str(min)
    return str(hr) + ":" + str(min)


def checker(lol):
    if lol == 1 : print("lol checked")
    print(time.strftime('%X'))
    return schedule.CancelJob

schedule.every().day.at(randomiser_timeofDay("morning")).do(checker, 1)
schedule.every(10).seconds.do(checker, 1)
#schedule.every().day.do(checker)
schedule.every().day.at(randomiser_timeofDay("morning")).do(checker, 1)
schedule.every().day.at(randomiser_timeofDay("night")).do(checker, 1)
schedule.every().day.at(randomiser_timeofDay("quote")).do(checker, 1)

schedule.clear()
schedule.get_jobs()

def random_scheduler():
    #schedule.clear()
    '''
    schedule.every().day.at(randomiser_timeofDay("morning")).do(checker, 1)
    schedule.every().day.at(randomiser_timeofDay("night")).do(checker, 1)
    schedule.every().day.at(randomiser_timeofDay("quote")).do(checker, 1)
    '''
    schedule.every().day.at('13:55').do(checker, 1)
    schedule.every().day.at('14:00').do(checker, 1)
    schedule.every().day.at('14:05').do(checker, 1)
    schedule.every().day.at("14:10").do(random_scheduler)
    return schedule.CancelJob


schedule.every().day.at("13:47").do(random_scheduler)
schedule.get_jobs()

while True:
    print(time.strftime('%X'))
    schedule.run_pending()
    print(schedule.get_jobs())
    #time.sleep(18000)
    time.sleep(240)

