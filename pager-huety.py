#!/usr/bin/env python3

import sys
import logging
from datetime import datetime
from time import sleep
from requests.exceptions import RequestException
import requests
from phue import Bridge
from os import getenv

logger = logging.getLogger('pager-huety')


def is_night_time(pm=21, am=7):
    cur_hour = datetime.now().hour
    return cur_hour >= pm or cur_hour <= am


class PagerHuety(object):
    def __init__(self, api_key, hue_host):
        self.api_key = api_key
        self.bridge = Bridge(hue_host)
        self._hue_host = hue_host

    def fetch_incidents(self, user_ids=None):
        """
        Grab latest triggered alerts from pager duty
        optionally filtered by user_ids

        Returns:
            JSON object
        """
        headers = { \
            'Authorization': 'Token token={}'.format(self.api_key), \
            'Accept': 'application/vnd.pagerduty+json;version=2' \
        }
        incidents_url = 'https://api.pagerduty.com/incidents?time_zone=UTC&status=triggered'

        if user_ids:
            incidents_url += '{}&user_ids%5B%5D={}'.format(incidents_url, user_ids)

        logger.info('Fetching pager duty incidents')

        try:
            response = requests.get(incidents_url, headers=headers)
        except RequestException as e:
            logger.exception('Error connecting to PagerDuty: %s', e)
            sys.exit(1)

        return response.json()

    def flash_light(self, light_id):
        """
        Flash light_id bulb red and blue 3x, then
        turn to bright white for 10 seconds and shut off
        """
        red = 65280
        blue = 46920

        logger.info('Flashing lights')
        logger.debug('Light ID: %d', light_id)
        logger.debug('Lights: %s', self.bridge.lights_by_id)

        self.bridge.get_light_objects()
        light = self.bridge.lights_by_id[light_id]
        # turn light on
        self.bridge.set_light(light_id, 'on', True)

        # blink red and blue
        for _ in range(0, 2):
            light.hue = red
            sleep(1.5)
            light.hue = blue
            sleep(1.5)

        # set to bright white
        light.xy = [.2, .2]
        sleep(10)

        # turn light off
        self.bridge.set_light(light_id, 'on', False)

        return


def main():    
    pd_api_key = getenv('PD_API_KEY')

    hue_host = getenv('HUE_HOST')

    lamp = getenv('LAMP', 3)

    night_only = getenv('NIGHT_ONLY', False)

    user_filter = getenv('PD_USER_FILTER')

    log_level = getenv('LOG_LEVEL', 'WARN')

    log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    phue_logger = logging.getLogger('phue')
    logger.setLevel(level=log_level)
    phue_logger.setLevel(level=log_level)

    if test:
        logger.info('Running in TEST mode')

    if pd_api_key is None:
        logger.critical('FATAL: PD_API_KEY environment variable not set.')
        sys.exit(1)

    if hue_host is None:
        logger.critical('FATAL: HUE_HOST environment variable not set.')
        sys.exit(1)

    if lamp is None:
        logger.critical('FATAL: LAMP environment variable not set.')
        sys.exit(1)

    ph = PagerHuety(pd_api_key, hue_host)

    while True:
        if not is_night_time() and night_only and not test:
            logger.info('Night time only mode set, not running')
            continue

        incidents = ph.fetch_incidents(user_filter)

        if incidents['total'] != 0 or test:
            logger.info('Triggering lights')
            ph.flash_light(lamp)

        sleep(30)


if __name__ == '__main__':
    main()
