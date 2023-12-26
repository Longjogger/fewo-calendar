import os
from dotenv import load_dotenv
#from ast import For
import pycurl
import certifi
import json
from io import BytesIO
import caldav
from datetime import datetime
from icalendar import Calendar, Event
import uuid
import pytz

# Load config from .env file
load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TABLESHEADURL = os.getenv('TABLESHEADURL')
TABLESDATAURL = os.getenv('TABLESDATAURL')
CALURL = os.getenv('CALURL')

# Config
username = 'ruegen'
password = 'CkT_pZ/dE45/4to93iu\XdonRLt/V/5cFnQgzw2p'
calurl = 'https://cloud.erikdonner.de/remote.php/dav/principals/users/ruegen/'


# Calendar colors
colors = {}
colors['Eigenbelegung'] = 'blue'
colors['Buchung'] = 'green'
colors['Stornierung'] = 'silver'


# cURL request for getting data from Nextcloud Tables View
# Parameter: URL, Username, Password
def getTablesData(url, username, password):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.USERPWD, '%s:%s' %(username, password))
    c.setopt(c.HTTPHEADER, ['Accept: application/json'])
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()
    body = buffer.getvalue()
    return json.loads(body.decode('iso-8859-1'))


# Load data from Nextcloud Tables
head = getTablesData(TABLESHEADURL, USERNAME, PASSWORD)
data = getTablesData(TABLESDATAURL, USERNAME, PASSWORD)


# Open Calendar 
client = caldav.DAVClient(CALURL, username=USERNAME, password=PASSWORD)
principal = client.principal()
calendars = principal.calendars()
calendar = calendars[0]

# Delete all events in calendar
date_start = datetime(1900, 1, 1, 0, 0, 0)
date_end = datetime(2100, 1, 1, 0, 0, 0)
events = calendar.date_search(start=date_start, end=date_end)
for event in events:
    event.delete()

# Create new events and save them
for item in data:
    cal = Calendar()
    event = Event()
    random_uid = str(uuid.uuid4())
    event.add('uid', random_uid)
    summary = ''
    description = ''
    buchungstyp = ''
    for i in range(len(head)):
        if head[i]['title'] == 'Anreise':
            travel = item['data'][i]['value']
            traveldate = travel.split('-')
            event.add('dtstart', datetime(int(traveldate[0]), int(traveldate[1]), int(traveldate[2]), 12, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")))
            description += head[i]['title'] + ': ' + traveldate[2] + '.' + traveldate[1] + '.' + traveldate[0] + '\n'
        elif head[i]['title'] == 'Abreise':
            travel = item['data'][i]['value']
            traveldate = travel.split('-')
            event.add('dtend', datetime(int(traveldate[0]), int(traveldate[1]), int(traveldate[2]), 12, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")))
            description += head[i]['title'] + ': ' + traveldate[2] + '.' + traveldate[1] + '.' + traveldate[0] + '\n'
        elif head[i]['title'] == 'Belegungstyp':
            value = int(item['data'][i]['value'])
            belegungstyp = head[i]['selectionOptions'][value]['label']
            event.add('color', colors[belegungstyp])
        elif head[i]['title'] == 'Vorname':
            vorname = item['data'][i]['value']
            summary += item['data'][i]['value'] + ' '
        elif head[i]['title'] == 'Nachname':
            nachname = item['data'][i]['value']
            summary += item['data'][i]['value']
        elif head[i]['title'] == 'Buchungstyp':
            if belegungstyp != 'Eigenbelegung':
                value = int(item['data'][i]['value'])
                buchungstyp = head[i]['selectionOptions'][value]['label']
    if belegungstyp == 'Eigenbelegung':
        summary = 'Eigenbelegung'
        description += 'Eigenbelegung'
    else:
        description += 'Gast: ' + vorname + ' ' + nachname + '\n'
        description += 'Buchungstyp: ' + buchungstyp
    event.add('summary', summary)
    event.add('description', description)
    cal.add_component(event)
    calendar.add_event(cal.to_ical())