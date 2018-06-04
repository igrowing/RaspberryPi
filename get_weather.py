#!/usr/bin/env python
""" Get local weather.
First retrieve location using external IP.
Then get weather with the location.
"""

from __future__ import unicode_literals

# import pyowm
import json
import argparse
import requests
from pprint import pprint
from urllib2 import urlopen
from contextlib import closing

# Get ready to post MQTT status. Install the library first.
# sudo pip install paho-mqtt
import paho.mqtt.publish as publish


def get_location():
    '''Return current location as dictionary determined by external IP.
    {u'city': u'City name',
     u'region_code': u'2B',
     u'region_name': u'Region name',
     u'ip': u'111.222.0.123',
     u'time_zone': u'Continent/City',
     u'longitude': 12.345,
     u'latitude': 56.789,
     u'metro_code': 0,
     u'country_code': u'2B',
     u'country_name': u'Country',
     u'zip_code': u''}
    '''

    url = 'http://freegeoip.net/json/'
    try:
        with closing(urlopen(url)) as response:
            location = json.loads(response.read())
        # pprint(location)
        return location

    except Exception:
        return {}


def get_weather(now=True, api=None):
    '''Returns Dict() of weather, based on current geolocation.'''

    loc = get_location()
    if not loc or not api:
        return {}

    try:
        req = "api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&APPID=%s" if now else "api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&APPID=%s"
        r = requests.get('http://' + req % (loc['latitude'], loc['longitude'], api))
        return r.json()

    except Exception:
        return {}


#####################  MAIN  ####################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('api', help='OpenWeatherMap API key')
    parser.add_argument('-n', '--now', help='Get current weather. Default.', required=False, action="store_true")
    parser.add_argument('-f', '--forecast', help='Get 5-day forecast weather', required=False, action="store_true")
    parser.add_argument('-m', '--mqtt', help='Publish result to MQTT server. [address] or [address:port]', required=False)

    args = parser.parse_args()
    is_now = not args.forecast or args.now
    weather = get_weather(now=is_now, api=args.api)
    if not weather:
        print "Error: can't retrieve weather from the server"
        exit(1)

    pprint(weather)

    try:
        # Publish to MQTT if required
        if args.mqtt:
            mqtt_srv = args.mqtt.split(':')
            port = int(mqtt_srv[1]) if len(mqtt_srv) > 1 else 1883
            topic = 'shm/weather/now' if is_now else 'shm/weather/forecast'
            publish.single(topic=topic, payload=str(weather), hostname=mqtt_srv[0], port=port)
    except TypeError:
        print "Error: convert data"
        exit(10)

    except IOError:
        print "Error: can't communicate with MQTT broker"
        exit(20)

    except ValueError:
        print "Error: user provided bad input"
        exit(40)
