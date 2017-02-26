#!/usr/bin/env python2.7

import urllib, urllib2

# set parameters
url = 'https://almascience.nrao.edu/sc/#queryFormTab'
params = {
             'scs-resolve-name': 'J1058+0133', 
             'dateObservedFrom': '2016-01-01', 
             'dateObservedTo':   '2016-12-01'
         }

# make a string with the request type in it:
method = "POST"

# create a handler. you can specify different handlers here (file uploads etc)
# but we go for the default
handler = urllib2.HTTPHandler()

# create an openerdirector instance
opener = urllib2.build_opener(handler)

# build a request
data = urllib.urlencode(params)
request = urllib2.Request(url, data=data)

# add any other information you want
request.add_header("Content-Type",'application/json')

# overload the get method function with a small anonymous function...
request.get_method = lambda: method

# try it; don't forget to catch the result
try:
    connection = opener.open(request)
except urllib2.HTTPError,e:
    connection = e

# check. Substitute with appropriate HTTP code.
if connection.code == 200:
    data = connection.read()
else:
    # handle the error case. connection.read() will still contain data
    # if any was returned, but it probably won't be of any use
    pass



print(data)



