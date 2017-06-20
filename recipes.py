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
    baseurl = "https://food2fork.com/api/search?key=6507744e6236b538625e845500a3184e&"
    dynamic_Content = getDynamicContent(req)
    if dynamic_Content is None:
        return {}
    final_url = baseurl + urlencode({'q': dynamic_Content})
    result = urlopen(final_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def getDynamicContent(req):
    result = req.get("result")
    parameters = result.get("parameters")
    dishType = parameters.get("dish-type")
    vegetable = parameters.get("vegetable")
    meat = parameters.get("meat")
    if (dishType is None) and (vegetable is None) and (meat is None):
        return None
      
    return dishType+","+vegetable+","+meat


def makeWebhookResult(data):
    count = data.get('count')
    c = randint(0, count);
   
    recipes = data.get('recipes[0]')
    if recipes is None:
        return {}

    title = recipes.get('title')
    if title is None:
        return {}

    publisher = recipes.get('publisher')
    if publisher is None:
        return {}

    imageUrl = recipes.get('image_url')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "I think you should try the " + title + " recipe I found on " + publisher + " website"
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": {image} ,
        # "contextOut": [],
        "source": "apiai-recipe-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
