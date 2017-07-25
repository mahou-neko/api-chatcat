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

    elif req.get("result").get("action")=="layer4_congestion":
        result = req.get("result")
        parameters = result.get("parameters")
        congestion4 = parameters.get("congestion_control")
        res = congestion_control_layer4(congestion4)

    elif req.get("result").get("action")=="layer2_congestion":
        result = req.get("result")
        parameters = result.get("parameters")
        congestion2 = parameters.get("congestion_control")
        res = congestion_control_layer2(congestion2)

    elif req.get("result").get("action")=="get_protocol_spec":
        result = req.get("result")
        parameters = result.get("parameters")
        prot = parameters.get("protocols")
        res = prot_info(prot)

    elif req.get("result").get("action")=="get_protocol_spec_info":
        result = req.get("result")
        parameters = result.get("parameters")
        prot = parameters.get("protocols")
        res = prot_more_info(prot)

    #elif req.get("result").get("action")=="greeting":
        #result = req.get("result")
        #parameters = result.get("parameters")
        #eve = parameters.get("eve")
        #res = makeWebhookResultTriggerEvent()
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

def prot_info(prot):
    protdef = {'TCP':'TCP = Transmission Control Protocol',
                'HTTP':'HTTP = Hyper Text Transfer Protocol',
                'SMTP':'SMTP = Simple Mail Transport Protocol',
                'IMAP':'IMAP = Internet Message Access Protocol',
                'DNS':'DNS = Domain Name System',
                'SIP':'SIP = Session Initiation Protocol',
                'RTP':'RTP = Real-time Transport Protocol',
                'HTML':'HTML = Hypertext Markup Language',
                'IP':'IP = Internet Protocol',
                'UDP':'UDP = User Datagram Protocol',
                'RPC':'RPC = Remote Procedure Call'
                }
    #in case of no specific protocol - entities none or protocol
    if prot in protdef:
        speech = protdef[prot]
    else:
        speech = "I guess it's time to switch topics then :)"
    if prot == "none" or prot == "protocol":
        speech = "In this case... Would you like to talk about protocols in general then?"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def prot_more_info(prot):
    protdef = {'TCP':'The Transmission Control Protocol (TCP) is one of the main protocols of the Internet protocol suite. It originated in the initial network implementation in which it complemented the Internet Protocol (IP). Therefore, the entire suite is commonly referred to as TCP/IP. TCP provides reliable, ordered, and error-checked delivery of a stream of octets between applications running on hosts communicating by an IP network. Major Internet applications such as the World Wide Web, email, remote administration, and file transfer rely on TCP.',
                'HTTP':'The Hypertext Transfer Protocol (HTTP) is an application protocol for distributed, collaborative, and hypermedia information systems. HTTP is the foundation of data communication for the World Wide Web. Hypertext is structured text that uses logical links (hyperlinks) between nodes containing text. HTTP is the protocol to exchange or transfer hypertext.',
                'SMTP':'Simple Mail Transfer Protocol (SMTP) is an Internet standard for electronic mail (email) transmission. Although electronic mail servers and other mail transfer agents use SMTP to send and receive mail messages, user-level client mail applications typically use SMTP only for sending messages to a mail server for relaying. For retrieving messages, client applications usually use either IMAP or POP3.',
                'IMAP':'In computing, the Internet Message Access Protocol (IMAP) is an Internet standard protocol used by e-mail clients to retrieve e-mail messages from a mail server over a TCP/IP connection. IMAP was designed with the goal of permitting complete management of an email box by multiple email clients, therefore clients generally leave messages on the server until the user explicitly deletes them.',
                'DNS':'The Domain Name System (DNS) is a hierarchical decentralized naming system for computers, services, or other resources connected to the Internet or a private network. It associates various information with domain names assigned to each of the participating entities. Most prominently, it translates more readily memorized domain names to the numerical IP addresses needed for locating and identifying computer services and devices with the underlying network protocols. By providing a worldwide, distributed directory service, the Domain Name System is an essential component of the functionality on the Internet, that has been in use since 1985.',
                'SIP':'The Session Initiation Protocol (SIP) is a communications protocol for signaling and controlling multimedia communication sessions in applications of Internet telephony for voice and video calls, in private IP telephone systems, as well as in instant messaging over Internet Protocol (IP) networks. SIP works in conjunction with several other protocols that specify and carry the session media. Media type and parameter negotiation and media setup is performed with the Session Description Protocol (SDP), which is carried as payload in SIP messages. For the transmission of media streams (voice, video) SIP typically employs the Real-time Transport Protocol (RTP) or the Secure Real-time Transport Protocol (SRTP).',
                'RTP':'The Real-time Transport Protocol (RTP) is a network protocol for delivering audio and video over IP networks. RTP is used extensively in communication and entertainment systems that involve streaming media, such as telephony, video teleconference applications, television services and web-based push-to-talk features. RTP typically runs over User Datagram Protocol (UDP). RTP is used in conjunction with the RTP Control Protocol (RTCP). While RTP carries the media streams (e.g., audio and video), RTCP is used to monitor transmission statistics and quality of service (QoS) and aids synchronization of multiple streams. RTP is one of the technical foundations of Voice over IP and in this context is often used in conjunction with a signaling protocol such as the Session Initiation Protocol (SIP) which establishes connections across the network.',
                'HTML':'Hypertext Markup Language (HTML) is the standard markup language for creating web pages and web applications. With Cascading Style Sheets (CSS) and JavaScript it forms a triad of cornerstone technologies for the World Wide Web. Web browsers receive HTML documents from a webserver or from local storage and render them into multimedia web pages. HTML describes the structure of a web page semantically and originally included cues for the appearance of the document.',
                'IP':'The Internet Protocol (IP) is the principal communications protocol in the Internet protocol suite for relaying datagrams across network boundaries. Its routing function enables internetworking, and essentially establishes the Internet. IP has the task of delivering packets from the source host to the destination host solely based on the IP addresses in the packet headers. For this purpose, IP defines packet structures that encapsulate the data to be delivered. It also defines addressing methods that are used to label the datagram with source and destination information.',
                'UDP':'In electronic communication, the User Datagram Protocol (UDP) is one of the core members of the Internet protocol suite. With UDP, computer applications can send messages, in this case referred to as datagrams, to other hosts on an Internet Protocol (IP) network. Prior communications are not required in order to set up transmission channels or data paths. UDP uses a simple connectionless transmission model with a minimum of protocol mechanism. UDP provides checksums for data integrity, and port numbers for addressing different functions at the source and destination of the datagram. It has no handshaking dialogues, and thus exposes the users program to any unreliability of the underlying network: there is no guarantee of delivery, ordering, or duplicate protection',
                'RPC':'n distributed computing, a remote procedure call (RPC) is when a computer program causes a procedure (subroutine) to execute in a different address space (commonly on another computer on a shared network), which is coded as if it were a normal (local) procedure call, without the programmer explicitly coding the details for the remote interaction. That is, the programmer writes essentially the same code whether the subroutine is local to the executing program, or remote. This is a form of client–server interaction (caller is client, executor is server), typically implemented via a request–response message-passing system.'
                }
    #in case of no specific protocol - entities none or protocol
    if prot in protdef:
        speech = protdef[prot]
    else:
        speech = "I guess it's time to switch topics then :)"
    if prot == "none" or prot == "protocol":
        speech = "In this case... Would you like to talk about protocols in general then?"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }



def congestion_control_layer2(congestion):
    con_methods = {'aloha':'The first version of the protocol was quite simple: If you have data to send, send the data - If, while you are transmitting data, you receive any data from another station, there has been a message collision. All transmitting stations will need to try resending "later". Note that the first step implies that Pure ALOHA does not check whether the channel is busy before transmitting. Since collisions can occur and data may have to be sent again, ALOHA cannot use 100 percent of the capacity of the communications channel. How long a station waits until it transmits, and the likelihood a collision occurs are interrelated, and both affect how efficiently the channel can be used.',
                    's-aloha':'An improvement to the original ALOHA protocol was "Slotted ALOHA", which introduced discrete timeslots and increased the maximum throughput. A station can start a transmission only at the beginning of a timeslot, and thus collisions are reduced. In this case, only transmission-attempts within 1 frame-time and not 2 consecutive frame-times need to be considered, since collisions can only occur during each timeslot.',
                    'CSMA':'Carrier-sense multiple access (CSMA) is a media access control (MAC) protocol in which a node verifies the absence of other traffic before transmitting on a shared transmission medium. A transmitter attempts to determine whether another transmission is in progress before initiating a transmission using a carrier-sense mechanism. That is, it tries to detect the presence of a carrier signal from another node before attempting to transmit.',
                    'CSMA/CD':'CSMA/CD is used to improve CSMA performance by terminating transmission as soon as a collision is detected, thus shortening the time required before a retry can be attempted.',
                    'CSMA/CA':'In CSMA/CA collision avoidance is used to improve the performance of CSMA. If the transmission medium is sensed busy before transmission, then the transmission is deferred for a random interval. This random interval reduces the likelihood that two or more nodes waiting to transmit will simultaneously begin transmission upon termination of the detected transmission, thus reducing the incidence of collision.'}

    if congestion in con_methods:
        speech = con_methods[congestion]
    else:
        speech = "This method is not part of layer 2's congestion control!"

    if congestion == "RED":
        return {"followupEvent":{"name":"red_con","data":{" ":" "}}}

    if congestion == "congestion control general":
        return {"followupEvent":{"name":"con_general","data":{" ":" "}}}

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def congestion_control_layer4(congestion):
    con_methods = {'reno':'If three duplicate ACKs are received, Reno will perform a fast retransmit and skip the slow start phase (which is part of Tahoe s procedure) by instead halving the congestion window (instead of setting it to 1 MSS like Tahoe), setting the slow start threshold equal to the new congestion window, and enter a phase called Fast Recovery.',
                    'tahoe':'If three duplicate ACKs are received, Tahoe performs a fast retransmit, sets the slow start threshold to half of the current congestion window, reduces the congestion window to 1 MSS, and resets to slow start state',
                    'TCP congestion control':'Congestion control via TCP is deployed either with Reno or Tahoe. Whenever duplicate ACKs are received either a slow start or a fast recovery is performed'}
    #speech = con_methods[congestion]
    if congestion in con_methods:
        speech = con_methods[congestion]
    else:
        speech = "This method is not part of layer 4's congestion control!"

    if congestion == "RED":
        return {"followupEvent":{"name":"red_con","data":{" ":" "}}}

    if congestion == "congestion control general":
        return {"followupEvent":{"name":"con_general","data":{" ":" "}}}

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


def makeWebhookResultTriggerEvent():
    speech = "It looks like you triggered an event!"

    return {
    "speech": speech,
    "displayText": speech,
    # "data": data,
    # "contextOut": [],
    "source": "apiai-weather-webhook-sample",
    "followupEvent":{"name":"eventtry","data":{" ":" "}}
    }
        #"speech": speech,
        #"displayText": speech,
        # "data": data,
        # "contextOut": [],
        #"source": "apiai-weather-webhook-sample"
        #"followupEvent": "eventtry"
    #}

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
