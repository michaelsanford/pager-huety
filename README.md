Dockerized Pager-Huety
===============================
A script to trigger Philip Hue lightbulbs based on triggered incidents from PagerDuty.

Dockerized
-----
```
docker build -t pagerhuety .
```


Usage
-----
    -h, --help            show this help message and exit
    --pd-api-key PD_API_KEY
                          API Key for pager duty
    --hue-host HUE_HOST   Hostname of your Philips Hue Bridge
    --lamp LAMP           Numeric id of the lamp to flash
    --night-only          Will only flash lights between 9PM - 7AM
    --user-filter USER_FILTER
                          Only trigger lights if incident is assigned to one of
                          these user ids
    --test                Test Pager Duty connection and Flash lights
    --log-level LOG_LEVEL
                          Set logging level

Example
-----
    ./pager-huety.py --pd-api-key=asdfgh --hue-host=Philips-hue.home


Colophon
-----
Originally authored by Justin Lintz <jlintz@gmail.com> as a module to control Philips Hue light bulbs based on Pager Duty alerts.