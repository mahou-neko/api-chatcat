#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action")=="yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
           return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)

    elif req.get("result").get("action")=="getjoke":
        baseurl = "http://api.icndb.com/jokes/random"
        result = urlopen(baseurl).read()
        data = json.loads(result)
        res = makeWebhookResultForGetJoke(data)

    elif req.get("result").get("action")=="layerabout":
        result = req.get("result")
        parameters = result.get("parameters")
        layer = parameters.get("layer")
        res = makeWebhookResultLayerAbout(layer)

    elif req.get("result").get("action")=="greeting":
        result = req.get("result")
        parameters = result.get("parameters")
        #eve = parameters.get("eve")
        res = makeWebhookResultTriggerEvent()
    else:
        return {}
 
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeWebhookResultTriggerEvent():
    speech = "It looks like you triggered an event!"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
        "followupEvent": "name":"eventtry","data": data
    }

def makeWebhookResultLayerAbout(layer):
    layerdef = {'physical layer':'The physical layer handels mechanical and electrical/optical linkage. It converts logical symbols into electrical(optical) ones and measures optical signals to reconstruct logical symbols', 
    'data link layer':'The data link layer covers transmission errors and handels media access. It is also concerned with congestion control.', 
    'network layer':'On the network layer paths from senders to recipients are chosen. Hence this layer also has to cope with heterogenius subnets and is responsibe for accounting.',
    'transport layer':'The transport layer offers secure end-to-end-communication between processes. Therefore it is also in charge for data stream control between endsystems. A few concerns of this layer are multiplexing, segmentation and acknowledgements in order to provide reliable transmission.',
    'session layer':'The name of this layer almost gives all its functionalities away! It mostly deals with communication managment, dialog control and synchronization.',
    'presentation layer':'Converting between dataformats, compression and decrompession as well as encryption are the main converns of the presentation layer.',
    'application layer':'Its name almost tells it all. The application layer handels communication between applications and deals with application specific services like e-mail, telnet etc.',
    'layer':'Alright! Layers basically are subdivisions of communication models. A Layer basically is a collection of similar functions that provide services to the layer above it and receives services from the layer below it.',
    'internet':'The internet layer has the same responsabilites as the third layer of the OSI model (which would be the network layer).',
    'link':'The link layer corresponds to the OSI model layers 1 and 2 (physical layer and data link layer).'}
    #maybe add a would you like to hear more right here! Would be a nice conversation flow!

    #might check if layer is defined in our dic!
    speech = layerdef[layer]

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeWebhookResultForGetJoke(data):
    valueString = data.get('value')
    joke = valueString.get('joke')
    speechText = joke
    displayText = joke
    return {
        "speech": speechText,
        "displayText": displayText,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
