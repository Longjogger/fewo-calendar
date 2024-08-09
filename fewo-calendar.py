import os
from dotenv import load_dotenv
import pycurl
import certifi
import json
from io import BytesIO
import caldav
from datetime import datetime
from icalendar import Calendar, Event
import uuid
import pytz

# Load .env file
load_dotenv()
# Load environment variables
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TABLESHEADURL = os.getenv('TABLESHEADURL')
TABLESDATAURL = os.getenv('TABLESDATAURL')
CALURL = os.getenv('CALURL')

# Calendar colors
COLORS = {
    'Eigenbelegung': 'blue',
    'Buchung': 'green',
    'Stornierung': 'silver'
}

# Function
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

# Function
# Extract dates (begin, end) from data
# Parameter: data, id
def getDates(data, id):
    for item in data:
        if item['columnId'] == id:
            date = item['value']
            year, month, day = date.split('-')
            caldavDate = datetime(int(year), int(month), int(day), 12, 0, 0, tzinfo=pytz.timezone("Europe/Berlin"))
            formattedDate = caldavDate.strftime('%d.%m.%Y')
            return caldavDate, formattedDate


# Load data from Nextcloud Tables
head = getTablesData(TABLESHEADURL, USERNAME, PASSWORD)
data = getTablesData(TABLESDATAURL, USERNAME, PASSWORD)


# Open Calendar 
client = caldav.DAVClient(CALURL, username=USERNAME, password=PASSWORD)
principal = client.principal()
calendars = principal.calendars()
calendar = calendars[0]

# Delete all events in calendar
dateStart = datetime(1900, 1, 1, 0, 0, 0)
dateEnd = datetime(2100, 1, 1, 0, 0, 0)
events = calendar.date_search(start=dateStart, end=dateEnd)
for event in events:
    event.delete()

# Create new events and save them
# Parsing throw data
for bookingItem in data:
    cal = Calendar()
    event = Event()
    random_uid = str(uuid.uuid4())
    event.add('uid', random_uid)
    summary = ''
    description = ''
    buchungstyp = ''
    for i in range(len(head)):
        match head[i]['title']:
            case 'Anreise':
                caldavDate, formattedDate = getDates(bookingItem['data'], head[i]['id'])
                event.add('dtstart', caldavDate)
                description += head[i]['title'] + ': ' + formattedDate + '\n'
            case 'Abreise':
                caldavDate, formattedDate = getDates(bookingItem['data'], head[i]['id'])
                event.add('dtend', caldavDate)
                description += head[i]['title'] + ': ' + formattedDate + '\n'
            case 'Belegungstyp':
                for detailItem in bookingItem['data']:
                    if detailItem['columnId'] == head[i]['id']:
                        for value in head[i]['selectionOptions']:
                            if value['id'] == int(detailItem['value']):
                                belegungstyp = value['label']
                                event.add('color', COLORS[belegungstyp])
                                description += head[i]['title'] + ': ' + belegungstyp + '\n'
            case 'Vorname':
                for detailItem in bookingItem['data']:
                    if detailItem['columnId'] == head[i]['id']:
                        firstname = detailItem['value']
            case 'Nachname':
                for detailItem in bookingItem['data']:
                    if detailItem['columnId'] == head[i]['id']:
                        lastname = detailItem['value']
            case 'Buchungstyp':
                for detailItem in bookingItem['data']:
                    if detailItem['columnId'] == head[i]['id']:
                        for value in head[i]['selectionOptions']:
                            if value['id'] == int(detailItem['value']):
                                buchungstyp = value['label']
    if belegungstyp == 'Eigenbelegung':
        summary = 'Eigenbelegung'
        description += 'Eigenbelegung'
    else:
        summary = firstname + ' ' + lastname
        description += 'Gast: ' + firstname + ' ' + lastname + '\n'
        description += 'Buchungstyp: ' + buchungstyp
    event.add('summary', summary)
    event.add('description', description)
    cal.add_component(event)
    calendar.add_event(cal.to_ical())