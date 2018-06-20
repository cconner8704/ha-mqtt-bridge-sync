from flask import Flask
import requests
import json
import argparse
import sys
import logging

#level=logging.DEBUG
logging_level=logging.INFO
logging.basicConfig(stream=sys.stdout, level=logging_level)

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

try:
    api_response = requests.get(stapi_uri, headers=stapi_headers)
    api_response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    logging.exception("Http Error:", errh)
    logging.exception("Got %s Look into this: %s" % (api_response.status_code, api_response.text))
except requests.exceptions.ConnectionError as errc:
    logging.exception("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    logging.exception("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    logging.exception("RequestsException:", err)

api_json_response = json.loads(api_response.text)

logging.info("stapi_uri: %s: json_response:" % stapi_uri)
logging.info("%s" % api_json_response[0])

base_uri = api_json_response[0]['uri']
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
    try:
        devices_response = requests.get(devices_uri, headers=stapi_headers)
        devices_response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.exception("Http Error:", errh)
        logging.exception("Got %s Look into this: %s" % (devices_response.status_code, devices_response.text))
    except requests.exceptions.ConnectionError as errc:
        logging.exception("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logging.exception("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logging.exception("RequestsException:", err)

    devices_json_response = json.loads(devices_response.text)
    logging.debug("devices_uri: %s: devices_json_response:" % devices_uri)
    logging.debug("%s" % devices_json_response[0])
    device_list = {}
    for device in devices_json_response:
        name = device["displayName"]
        id = device["id"]
        device_list[id] = name

    return json.dumps(device_list)

@app.route("/updatedevices")
def updatedevices():
    try:
        devices_response = requests.get(devices_uri, headers=stapi_headers)
        devices_response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.exception("Http Error:", errh)
        logging.exception("Got %s Look into this: %s" % (devices_response.status_code, devices_response.text))
    except requests.exceptions.ConnectionError as errc:
        logging.exception("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logging.exception("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logging.exception("RequestsException:", err)

    devices_json_response = json.loads(devices_response.text)
    logging.debug("devices_uri: %s: devices_json_response:" % devices_uri)
    logging.debug("%s" % devices_json_response[0])

    for device in devices_json_response:
        name = device["displayName"]
        id = device["id"]
        device_uri = "%s/device/%s" % (base_uri, id)
        try:
            device_response = requests.get(device_uri, headers=stapi_headers)
            device_response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.exception("Http Error:", errh)
            logging.exception("Got %s Look into this: %s" % (device_response.status_code, device_response.text))
        except requests.exceptions.ConnectionError as errc:
            logging.exception("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            logging.exception("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            logging.exception("RequestsException:", err)

        device_json_response = json.loads(device_response.text)
        logging.debug("device_uri: %s: device_json_response:" % device_uri)
        logging.debug("%s" % device_json_response)
        attrs = {"switch", "power", "level"}
        logging.debug("supportedAttributes: %s" % device_json_response["supportedAttributes"])
        for attribute in attrs:
            if attribute in device_json_response["supportedAttributes"]:
#            if attribute == "power":
                attr_uri = "%s/attribute/%s" % (device_uri, attribute)
                try:
                    attr_response = requests.get(attr_uri, headers=stapi_headers)
                    attr_response.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    logging.exception("Http Error:", errh)
                    logging.exception("Got %s Look into this: %s" % (attr_response.status_code, attr_response.text))
                except requests.exceptions.ConnectionError as errc:
                    logging.exception("Error Connecting:", errc)
                except requests.exceptions.Timeout as errt:
                    logging.exception("Timeout Error:", errt)
                except requests.exceptions.RequestException as err:
                    logging.exception("RequestsException:", err)

                attr_json_response = json.loads(attr_response.text)
                logging.debug("attr_uri: %s: attr_json_response:" % attr_uri)
                logging.debug("%s" % attr_json_response)
                attr_value = attr_json_response["value"]
                if attr_value is not None:
                    bridge_post_data = {"name": str(name), "value": attr_value, "type": str(attribute)}
                    logging.info(
                        "Pushing to bridge: name: %s: id: %s: attr: %s: value: %s" % (name, id, attribute, attr_value))
                    try:
                        bridge_push_response = requests.post(stbridge_uri, data=json.dumps(bridge_post_data),
                                                             headers=stbridge_headers)
                        bridge_push_response.raise_for_status()
                    except requests.exceptions.HTTPError as errh:
                        logging.exception("Http Error:", errh)
                        logging.exception("Got %s Look into this: %s" % (bridge_push_response.status_code, bridge_push_response.text))
                    except requests.exceptions.ConnectionError as errc:
                        logging.exception("Error Connecting:", errc)
                    except requests.exceptions.Timeout as errt:
                        logging.exception("Timeout Error:", errt)
                    except requests.exceptions.RequestException as err:
                        logging.exception("RequestsException:", err)

    return "Updating MQTT Bridge Devices Complete"

if __name__ == '__main__':
    app.run(debug=True)





