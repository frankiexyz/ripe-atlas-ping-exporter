#!/usr/bin/env python
from __future__ import division
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import socket
import urllib2
import pyasn
import urlparse
import cStringIO
import re
import json
import os
from geoip import geolite2

def getLatestDATA(TASKID):
        ATLAS_URL = "https://atlas.ripe.net/api/v2/measurements/{}/latest/?versions=2".format(TASKID)
	req = urllib2.Request(ATLAS_URL)
	req.add_header('Accept', 'application/json')
	res = urllib2.urlopen(req)
	resdata = res.read()
	jsonoutput = json.loads(resdata)
        output = []
	for i in jsonoutput:
            print i['from']
            try:
	        ASN = asndb.lookup(i['from'])[0]
	        city = geolite2.lookup(i['from']).country
            except:
                ASN = "NA"
                city = "NA"
	    output.append( "ripe_ping_avg{{label=\"{}\",city=\"{}\",src_ip=\"{}\",dst_name=\"{}\"}} {}\n".format(ASN, city,i['from'], i['dst_name'], i['avg']))
	    output.append( "ripe_ping_min{{label=\"{}\",city=\"{}\",src_ip=\"{}\",dst_name=\"{}\"}} {}\n".format(ASN, city, i['from'], i['dst_name'], i['min']))
	    output.append( "ripe_ping_max{{label=\"{}\",city=\"{}\",src_ip=\"{}\",dst_name=\"{}\"}} {}\n".format(ASN, city, i['from'], i['dst_name'], i['max']))
            try:
	        output.append( "ripe_ping_loss{{label=\"{}\",city=\"{}\",src_ip=\"{}\",dst_name=\"{}\"}} {}\n".format(ASN, city, i['from'], i['dst_name'],  (((i['sent']-i['rcvd'])*100)/i['sent'])))
            except ZeroDivisionError:
                print "Ignore"
        return output

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print parsed_path.query
	message = ""
        if "&" in parsed_path.query:
		if "module" in parsed_path.query.split('&')[0]:
			if "PING" in parsed_path.query.split('&')[0]:
				print "PING"
				message = message.join(getLatestDATA(parsed_path.query.split('&')[1].split('=')[1]))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    asndb = pyasn.pyasn('/ipasn_20160805.dat')
    server = ThreadedHTTPServer(('0.0.0.0', 9001), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
