#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from random import randint

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests

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
    if req.get("result").get("action") != "recipe.recommendation":
        return {}
    baseurl = "https://food2fork.com/api/search?"
    dynamic_Content = getDynamicContent(req)
    if dynamic_Content is None:
        return {}
    final_url = baseurl + urlencode({'key':'6507744e6236b538625e845500a3184e','q': dynamic_Content})
    result = requests.get(final_url)
    data = json.loads(result.text)
    res = makeWebhookResult(data)
    return res


def getDynamicContent(req):
    result = req.get("result")
    parameters = result.get("parameters")
    dishType = parameters.get("dish-type")
    vegetable = parameters.get("vegetable")
    #meat = parameters.get("meat")
    if (dishType is None) and (vegetable is None):# and (meat is None):
        return None
      
    return dishType+","+vegetable#+","+meat


def makeWebhookResult(data):
    count = data['count']
    c = randint(0, count);
   
    title = data['recipes'][c]['title']
    if title is None:
        return {}

    publisher = data['recipes'][c]['publisher']
    if publisher is None:
        return {}
		
	sourceURL = data['recipes'][c]['source_url']
    if sourceURL is None:
        return {}

    #imageUrl = recipes.get('image_url')
   
    # print(json.dumps(item, indent=4))

    speech = "I think you should try the " + title + " recipe I found on " + publisher + " website"
	displayText = "I think you should try the " + title + " recipe I found on " + publisher + " website. Link to recipe is below : " + sourceURL
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": displayText,
        "data": {} ,
        "contextOut": [],
        "source": "apiai-recipe-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
