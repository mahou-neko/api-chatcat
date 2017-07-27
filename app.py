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

    elif req.get("result").get("action")=="get_protocol_info_more":
        result = req.get("result")
        parameters = result.get("parameters")
        prot = parameters.get("protocols")
        infor = parameters.get("Information")
        res = prot_more_info_more(prot, infor)

    elif req.get("result").get("action")=="get_ipvdiff":
        result = req.get("result")
        parameters = result.get("parameters")
        prot = parameters.get("protocols")
        res = prot_more_info_more("IP", "advantages")

    elif req.get("result").get("action")=="get_layer_info_general":
        result = req.get("result")
        parameters = result.get("parameters")
        res = layer_general_event()

    elif req.get("result").get("action")=="trigger_peer_event":
        result = req.get("result")
        parameters = result.get("parameters")
        res = peer_event()

    elif req.get("result").get("action")=="p2p_info":
        result = req.get("result")
        parameters = result.get("parameters")
        topo = parameters.get("Topologies")
        res = p2p_inf(topo)

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

def p2p_inf(topo):
    topodef = {'p2pv1':'Every node of the overlay knows k > 2 other nodes. Data gets flooded over the edges and every node contains every information.',
                'p2pv2':'Every node contains only a small fraction of the data. Hence rare content is hard to find. This type of p2p is usually deployed via directory servers or flooding with backtracking.',
                'dht':'Distributed Hash-Tables are a structured p2p overlay and utilizes a dynamic number of nodes. I realizes a cyclic data space and since every node knows the address of its logical successor, the complexity of searches is reduced to O(n).',
                'unstructured':'Unstructured peer-to-peer networks do not impose a particular structure on the overlay network by design, but rather are formed by nodes that randomly form connections to each other.',
                'structured':'In structured peer-to-peer networks the overlay is organized into a specific topology, and the protocol ensures that any node can efficiently search the network for a file/resource, even if the resource is extremely rare.'}
    if topo in topodef:
        speech = topodef[topo]
    else:
        speech = "Could you tell me the p2p form you are interested in again?"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


def peer_event():
    speech = "peer event was triggered!"

    return {
    "speech": speech,
    "displayText": speech,
    # "data": data,
    # "contextOut": [],
    "source": "apiai-weather-webhook-sample",
    "followupEvent":{"name":"peerevent","data":{" ":" "}}
    }

def layer_general_event():
    speech = "Layer general event was triggered!"

    return {
    "speech": speech,
    "displayText": speech,
    # "data": data,
    # "contextOut": [],
    "source": "apiai-weather-webhook-sample",
    "followupEvent":{"name":"layergeneraltrigger","data":{" ":" "}}
    }


def prot_more_info_more(prot, infor):

    if infor == "advantages":
        speech = prot_advantages(prot)
    elif infor == "issues":
        speech = prot_disadvantages(prot)
    elif infor == "alternatives":
        speech = prot_alternatives(prot)
    elif infor == "difference":
        speech = prot_diff_udp_tcp()
    else:
        speech = "Mhh I am not quite sure about " + infor + " but I will ask someone and come back to you :) In the mean time we could talk about advantages, issues or alternatives to this protocol or something else altogehter!"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def prot_diff_udp_tcp():
    return "There are two types of Internet Protocol (IP) traffic. They are TCP or Transmission Control Protocol and UDP or User Datagram Protocol. TCP is connection oriented – once a connection is established, data can be sent bidirectional. UDP is a simpler, connectionless Internet protocol."


def prot_advantages(prot):
    protdef = {'TCP':'The main advantage of TCP is that it offers connection-oriented communication - which means that  a communication session or a semi-permanent connection is established before any useful data can be transferred, and where a stream of data is delivered in the same order as it was sent',
                'HTTP':'It s greates adantage is that basically is everywhere on the internet',
                'SMTP':'Although proprietary systems (such as Microsoft Exchange and IBM Notes) and webmail systems (such as Outlook.com, Gmail and Yahoo! Mail) use their own non-standard protocols to access mail box accounts on their own mail servers, all use SMTP when sending or receiving email from outside their own systems.',
                'IMAP':'The main advantage of IMAP would be that one can acces their mails directly on the server',
                'DNS':'The Domain Name System delegates the responsibility of assigning domain names and mapping those names to Internet resources by designating authoritative name servers for each domain. Network administrators may delegate authority over sub-domains of their allocated name space to other name servers. This mechanism provides distributed and fault tolerant service and was designed to avoid a single large central database.',
                'SIP':'SIPs main advantages lies within its capability to singal and control multimedia communication sessions',
                'RTP':'RTPs greates strength is that it is designed for end-to-end, real-time, transfer of streaming media. The protocol provides facilities for jitter compensation and detection of out of sequence arrival in data, which are common during transmissions on an IP network. RTP allows data transfer to multiple destinations through IP multicast.',
                'HTML':'Advantes of HTML are...',
                'IP':'IPv4 provides safeguards to ensure that the IP packet header is error-free. A routing node calculates a checksum for a packet. If the checksum is bad, the routing node discards the packet. Although the Internet Control Message Protocol (ICMP) allows such notification, the routing node is not required to notify either end node of these errors. By contrast, in order to increase performance, and since current link layer technology is assumed to provide sufficient error detection, the IPv6 header has no checksum to protect it.',
                'UDP':'Since UDP is connectionless it is a ton fastern than TCP.',
                'RPC':'The greates advantage of the RPC model is that it implies a level of location transparency, namely that calling procedures is largely the same whether it is local or remote, but usually they are not identical, so local calls can be distinguished from remote calls. Remote calls are usually orders of magnitude slower and less reliable than local calls, so distinguishing them is important.'
                }
    return protdef[prot]


def prot_disadvantages(prot):
    protdef = {'TCP':'Some possible issues with TCP are Denial of Service, Connection hijaking and TCP veto.',
                'HTTP':'The TRACE method can be used as part of a class of attacks known as cross-site tracing; for that reason, common security advice is for it to be disabled in the server configuration. Microsoft IIS supports a proprietary "TRACK" method, which behaves similarly, and which is likewise recommended to be disabled',
                'SMTP':'One cannot delete or access mails directly on the server',
                'IMAP':'IMAPs disadvantages would be...',
                'DNS':'Several vulnerability issues were discovered and exploited by malicious users. One such issue is DNS cache poisoning, in which data is distributed to caching resolvers under the pretense of being an authoritative origin server, thereby polluting the data store with potentially false information and long expiration times (time-to-live). Subsequently, legitimate application requests may be redirected to network hosts operated with malicious intent.',
                'SIP':'Issues with SIP include...',
                'RTP':'The most common problems with RTP are...',
                'HTML':'Common issues with HTML include...',
                'IP':'Various error conditions may occur, such as data corruption, packet loss, duplication and out-of-order delivery. Because routing is dynamic, meaning every packet is treated independently, and because the network maintains no state based on the path of prior packets, different packets may be routed to the same destination via different paths, resulting in out-of-order sequencing at the receiver.',
                'UDP':'Since UDP emphazises reduced latency over reliability, it is not the best option if you need your data to arrive in the correct order to guarantee correct delivery!',
                'RPC':'I am not quite sure about RPCs disandavtages... I ll get back to you for this question though!'
                }
    return protdef[prot]


def prot_alternatives(prot):
    protdef = {'TCP':'UDP is the connection-less counterpart to TCP.',
                'HTTP':'HTTPS would be a good alternative',
                'SMTP':'IMAP or POP3 are more common alternatives',
                'IMAP':'POP3 (more commonly used today) or SMTP woudl be alternatives to IMAP',
                'DNS':'I think we did not disucss alternatives for DNS...',
                'SIP':'Alternatives to SIP would be IAX, ICE, XMPP (Google Hangouts)',
                'RTP':'Alternatives for RTP include...',
                'HTML':'HTML alternatives would consist of...',
                'IP':'There are two commonly used versions of IP - IPv4 and IPv6',
                'UDP':'TCP would be the connection-oriented counterpart to UDP.',
                'RPC':'RPCs are a form of inter-process communication (IPC), in that different processes have different address spaces: if on the same host machine, they have distinct virtual address spaces, even though the physical address space is the same; while if they are on different hosts, the physical address space is different. Many different (often incompatible) technologies have been used to implement the concept.'
                }
    return protdef[prot]


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
        speech = protdef[prot] + "Would you like to hear a bit more about " + prot + " ?"
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
