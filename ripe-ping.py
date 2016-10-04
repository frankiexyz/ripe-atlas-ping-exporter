#!/usr/bin/env python
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
from geoip import geolite2


APIKEY="YOUR API KEY"
ATASKID="YOUR Task KEY""


def getLatestDATA(TASKID):
	ATLAS_URL="https://atlas.ripe.net/api/v1/measurement-latest/"+str(TASKID)+"/?key="+APIKEY
	req = urllib2.Request(ATLAS_URL)
	req.add_header('Accept', 'application/json')
	res = urllib2.urlopen(req)
	resdata=res.read()
	jsonoutput=json.loads(resdata)
        output=[]
	for i in jsonoutput:
	    ASN=asndb.lookup(jsonoutput[i][0]['from'])[0]
	    city=geolite2.lookup(jsonoutput[i][0]['from']).country
	    output.append( "ripe_ping_avg{label=\""+str(ASN)+"\",city=\""+str(city)+"\"} "+str(jsonoutput[i][0]['avg'])+"\n")
	    output.append( "ripe_ping_loss{label=\""+str(ASN)+"\",city=\""+str(city)+"\"} "+ str((3-jsonoutput[i][0]['rcvd'])/3*100)+"\n")
        return output

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print parsed_path.query
	message=""
        if "&" in parsed_path.query:
		if "module" in parsed_path.query.split('&')[0]:
			if "PING" in parsed_path.query.split('&')[0]:
				print "PING"
				message=message.join(getLatestDATA(parsed_path.query.split('&')[1].split('=')[1]))
			elif "DNS" in parsed_path.query.split('&')[0]:
				print "DNS"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    asndb = pyasn.pyasn('ipasn_20160805.dat')
    server = ThreadedHTTPServer(('0.0.0.0', 9001), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
