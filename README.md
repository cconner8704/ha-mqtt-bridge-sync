Test web app with REST API to sync the current state of Home Assistant to SmartThings hub.
I was having issues with the HA Smartthings Bridge not always being in sync.  This will periodically
compare the states of SmartThings and HA and then push to MQTT if HA is out of sync.  Currently
depends on a REST API app in SmartThings:

https://github.com/bradymholt/smartthings-rest-api

Docker container using python:3 and install flask, requests and supervisord





Look into this:

https://community.smartthings.com/t/createapp-rest-api/109711