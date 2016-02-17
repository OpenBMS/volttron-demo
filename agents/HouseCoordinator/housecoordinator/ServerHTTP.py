#!/usr/bin/env python
 
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
import copy
import urlparse

msg = {}
instance = None

#Create custom HTTPRequestHandler class
class HouseHTTPServer(BaseHTTPRequestHandler):

  @staticmethod
  def set_buffer(data):
    print "Entered Static Method"
    global msg
    msg = copy.copy(data) 
    print msg

  @staticmethod
  def set_instance(inst_val):
     global instance
     instance = inst_val;
     print "Got hold of HC Agent Instance"      
 
  #handle GET command
  def do_GET(self):
    print('it is a GET')
    self.send_response(200) 
    self.send_header('Content-type','text-html')
    self.end_headers()
    #send file content to client
    print "SENT DATA"
    global msg
    print  msg
    self.wfile.write(json.dumps(msg))

  def do_POST(self):
    print("Inside POST -- probably a command !!")
    length = int(self.headers.getheader('content-length'))
    print "length %d"%length
    field_data = self.rfile.read(length)
    print type(field_data)
    print "field_data %s"%(field_data)
    #Parse  through the control msg and take necessary steps
    json_acceptable_string = field_data.replace("'", "\"")
    fields = json.loads(json_acceptable_string)
    print fields
    if fields['type'] == "device":
      print "Control Msg : device type "
      instance.create_and_publish_topic(fields)
    elif fields['type'] == "profile":
      print "Control Msg : Profile"
      instance.set_mode(fields['value'])
    elif fields['type'] == "price":
      print "Control Msg : Price"
      instance.set_price(float(fields['value']))
    elif fields['type'] == 'disruption':
      instance.handle_disruption()

    self.send_response(200) 

