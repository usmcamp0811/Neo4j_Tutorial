import httplib2
import os
from tqdm import tqdm
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup
import urllib.request
import ssl
import re
import parsedatetime as pdt
# import pytz
# from pytz import timezone
from datetime import datetime
import datetime
import dateparser

ssl._create_default_https_context = ssl._create_unverified_context

def is_number(a):
    # will be True also for 'NaN'
    try:
        number = float(a)
        return 1
    except ValueError:
        return 0

def mda_small_business_calendar():
    url = 'https://www.mda.mil/business/bus_calendar.html'
    r = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(r, 'lxml')
    events = []
    for event in soup.find_all("h3", class_="collapse-me"):
        events.append(event.text)
    c = pdt.Constants()
    p = pdt.Calendar(c)
    event_dict = {}
    for e in events:
        dates, event_name = e.split('- ')[0], e.split('- ')[1]
        event_dict[event_name.rstrip()] = dateparser.parse(dates.rstrip()), \
                                          dates, url
    return event_dict

def hsv_chamber_calendar():
    url = 'http://www.huntsvillealabamausa.com/index.php?option=com_content&view=article&id=190&Itemid=298'
    r = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(r, 'lxml')
    events = []
    for event in soup.find_all("h4"):
        events.append(event.text)
    c = pdt.Constants()
    p = pdt.Calendar(c)
    event_dict = {}
    for i in range(0, len(events), 2):
        dates, event = events[i], events[i + 1]
        event = event.replace('\nNEW!\r\n  ', '')
        event = event.replace('\nNEW! ', '')
        event = event.replace('\r\n', '')
        event_dict[event.rstrip()] = dateparser.parse(dates.rstrip()), \
                                     dates, url
    return event_dict

def HSV_DnS_calendar():
    url = 'http://www.huntsvilledefenseandspacecalendar.com/'
    r = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(r, 'lxml')
    events = []
    for event in soup.find_all("b"):
        if is_number(event.text[0]):
            events.append(event.text)
    c = pdt.Constants()
    p = pdt.Calendar(c)
    event_dict = {}
    for i in range(len(events)):
        try:
            dates, event = events[i].split('–')[0].replace('\n\t', ' '), \
            events[i].split('–')[1].replace('\n\t', ' ')
            if len(event) > 4:
                dates = dates.rstrip()
                datesr = dates.split()
                datesr.reverse()
                datesr = ' '.join(datesr)
                event_dict[event.rstrip()] = dateparser.parse(dates), \
                                             dates, url
                #TODO: make code to catch the multi-day events... currently this will break
        except:
            pass
    return event_dict

def merge_calendars():
    mda = mda_small_business_calendar()
    cc = hsv_chamber_calendar()
    dns = HSV_DnS_calendar()

    super_calendar = {**mda, **cc, **dns}
    return super_calendar