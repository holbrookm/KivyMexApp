#!/usr/bin/python
""" Class To Connect and Perfom tasks with NGIN via HTTP persistance"""

"""
The following are the functions in this class and their uses:


Modifying this class for the Kivy Mex App
"""

import  httplib2, json, debug
import socks

class cie_prov:
  def __init__(self,server,url_prefix, username, password):
   
    self.server = server
    self.url_prefix = url_prefix
    self.username = username
    self.password = password

  def get_cie_subscription(self, subnum):
    debug.p("**********************************************************")
    debug.p("FUNC: Class cie_prov: func:- get_cie_subscription *******")
    returncode = 100
    h = httplib2.Http(".cache")
    h.force_exception_to_status_code = True # This informs httplib2 to return http codes as the error code
    h.add_credentials(self.username, self.password)
    debug.p ("http://" + self.server + self.url_prefix + subnum + " GET")
    resp, content = h.request("http://" + self.server + self.url_prefix + subnum, "GET")
    #debug.p(str(resp))
    #debug.p(str(content))
    if int(resp["status"]) == 200:
      debug.p ("HTTP-200 successful request")
      returncode = json.loads(content)
    elif int(resp["status"]) == 404:
      debug.p ("HTTP-404 object not found")
    elif int(resp['status']) == 400:
        debug.p("HTTP-400 Network not available")
    else:
      debug.p( "ERROR  " + resp["status"] + " unknown error")
    
    return returncode

	
  def get_cie_logon(self):
    object_prefix = "/accounts/system/security/users/"
    h = httplib2.Http(".cache")
    h.add_credentials(self.username, self.password)
    h.force_exception_to_status_code = True     # This informs httplib2 to return http codes as the error code
    debug.p ("DEBUG: http://" + self.server + self.url_prefix + object_prefix + self.username + " GET")
    try:
        resp, content = h.request("http://" + self.server + self.url_prefix + object_prefix+ self.username, "GET")
    except httplib2.HttpLib2Error:
        print "GET CIE_LOGON:  ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
    else:
        debug.p(str(resp))
        debug.p(str(content))
        if int(resp["status"]) == 200:
            debug.p("HTTP-200 successful request")
            returncode = json.loads(content)
        elif int(resp["status"]) == 401:
            debug.p("HTTP-401 Authorisation Failure")
            returncode = json.loads(content)
        elif int(resp['status']) == 400:
            returncode = 400
            debug.p("HTTP-400 Network not available")
        else:
            returncode == 100
            debug.p("ERROR  " + resp["status"] + " unknown error")

    return returncode, int(resp['status'])


  def put_cie_object(self,object, data):
    h = httplib2.Http(".cache")
    h.add_credentials(self.username, self.password)
    h.force_exception_to_status_code = True  # This informs httplib2 to return http codes as the error code
    resp, content = h.request("http://" + self.server + self.url_prefix + object, "PUT", json.dumps(data))
    returncode = 100 
    try:
      content_j = json.loads(content) 
    except:
      return 1
    
    if content_j["result"] == "CREATED":
      debug.p("Successfully created" )
      returncode = 0
    elif content_j["result"] == "UPDATED":
      debug.p("Successfully updated" )
      returncode = 0
    elif content_j["result"] == "VALIDATION_ERROR":
      debug.p ("VALIDATION_ERROR" + str(content) )
      returncode = 1
    else:
      debug.p("unknown error" + str(resp) + " " + str(content) )

    return returncode

	
  def get_cie_object(self,object):
    returncode = 100
    h = httplib2.Http(".cache")
    h.force_exception_to_status_code = True  # This informs httplib2 to return http codes as the error code
    h.add_credentials(self.username, self.password)
    debug.p ("http://" + self.server + self.url_prefix + object + "         GET")
    resp, content = h.request("http://" + self.server + self.url_prefix + object, "GET")
    #debug.p(str(resp))
    if int(resp["status"]) == 200:
      debug.p("HTTP-200 successful request")
      returncode = json.loads(content)
    elif int(resp["status"]) == 404:
      debug.p("HTTP-404 object not found")
    else:
      debug.p("ERROR  :" + resp["status"] + " unknown error")

    return returncode    
     
    # cie errors 
    try:
      cie_error = json.loads(content)
      if not cie_error.has_key("result") or cie_error["result"] != "CREATED" and cie_error["result"] != "UPDATED":
        #logger.log( ERROR, cie_error["errors"][0]["error"])
        returncode = 99
    except:
      debug.p("unexpected content received from CIE2 during provisioning of " + str(object) + " received content: " + str(content) )
      debug.p(" URl: http://" + str(self.server) + str(self.url_prefix) + str(object) )
      debug.p(str(json.dumps(data)) )
      
    return returncode


  def put_cie_json_object(self,object, data):
      h = httplib2.Http(".cache")
      h.force_exception_to_status_code = True  # This informs httplib2 to return http codes as the error code
      h.add_credentials('admin', 'password')
      print ("http://" + self.server + self.url_prefix + object + "      PUT" +  (data))
      resp, content = h.request("http://" + self.server + self.url_prefix + object, "PUT", (data))
      returncode = 100 
      try:
        content_j = json.loads(content) 
      except:
        debug.p( "ERROR  :" +  str(json.dumps(data)))
        return 1
     
      if content_j["result"] == "CREATED":
        debug.p ("Successfully created" )
        returncode = 0
      elif content_j["result"] == "UPDATED":
        debug.p("Successfully updated" )
        returncode = 0
      elif content_j["result"] == "VALIDATION_ERROR":
        debug.p("VALIDATION_ERROR" + str(content) )
        returncode = 1
      else:
        debug.p("unknown error" + str(resp) + " " + str(content) )
      return returncode

