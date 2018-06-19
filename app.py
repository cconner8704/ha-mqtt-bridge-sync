from flask import Flask
import requests
import json
import argparse
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--oauth', action='store', dest='oauth',
                    help='SmartThings Rest API OAuth Token')

parser.add_argument('-b', '--bridgehost', action='store', dest='bridgehost',
                    help='Hostname of the SmartThings Bridge')

parser.add_argument('-p', '--bridgeport', action='store', dest='bridgeport',
                    help='Port of the SmartThings Bridge')

parser.add_argument('-s', '--bridgessl', action="store_true", dest='bridgessl',
                    default=False, help='Enable SSL for the SmartThings Bridge')

args = parser.parse_args()

OAUTH_KEY = args.oauth
OAUTH_STRING = "Bearer %s" % OAUTH_KEY

stapi_uri = 'https://graph.api.smartthings.com/api/smartapps/endpoints'
stapi_headers = { 'Authorization': OAUTH_STRING }

stbridge_uri = '%s:%s/push' % (args.bridgehost, args.bridgeport)

if args.bridgessl:
    stbridge_uri = 'https://%s' % stbridge_uri
else:
    stbridge_uri = 'http://%s' % stbridge_uri

stbridge_headers = { 'User-Agent': 'Linux UPnP/1.0 SmartThings', 'Content-Type': 'application/json'}

response = requests.get(stapi_uri, headers=stapi_headers)
json_response = json.loads(response.text)

logging.warn("stapi_uri: %s: json_response:" % stapi_uri)
logging.warn("%s" % json_response[0])

base_uri = json_response[0]['uri']
devices_uri = "%s/devices" % base_uri

app = Flask(__name__)

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route("/bye")
def bye():
    return "Bye World!"

@app.route("/getdevices")
def getdevices():
    devices_response = requests.get(devices_uri, headers=stapi_headers)
    devices_json_response = json.loads(devices_response.text)
    logging.warn("devices_uri: %s: devices_json_response:" % devices_uri)
    logging.warn("%s" % devices_json_response[0])

    for device in devices_json_response:
        name = device["displayName"]
        id = device["id"]
        device_uri = "%s/device/%s" % (base_uri, id)
        device_response = requests.get(device_uri, headers=stapi_headers)
        device_json_response = json.loads(device_response.text)
        logging.warn("device_uri: %s: device_json_response:" % devices_uri)
        logging.warn("%s" % device_json_response[0])
        attrs = {"switch", "power", "level"}
        logging.warn("supportedAttributes: %s" % device_json_response["supportedAttributes"])
        for attribute in attrs:
            #    if attribute in json_response["supportedAttributes"]:
            if attribute == "power":
                attr_uri = "%s/attribute/%s" % (device_uri, attribute)
                attr_response = requests.get(attr_uri, headers=stapi_headers)
                attr_json_response = json.loads(attr_response.text)
                logging.warn("attr_uri: %s: attr_json_response:" % attr_uri)
                logging.warn("%s" % attr_json_response[0])
                attr_value = attr_json_response["value"]
                bridge_post_data = {"name": name, "value": attr_value, "type": attribute}
                logging.warn("Pushing to bridge: name: %s: id: %s: attr: %s: value: %s" % (name, id, attribute, attr_value))
#                bridge_push_response = requests.post(stbridge_uri, data=json.dumps(bridge_post_data), headers=stbridge_headers)

    return devices_json_response


if __name__ == '__main__':
    app.run(debug=True)





