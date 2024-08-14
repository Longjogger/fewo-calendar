# Fewo-Calendar
Read holiday apartment (Ferienwohnung \[Fewo\]) bookings from the Nextcloud Tables app and import them into a (Nextcloud) calendar via CalDav.

## Prerequisites

### Nextcloud
First, you need a running Nextcloud installation with the Tables app and Calendar app installed.

In the Tables app, you need a view with the following columns:
* Arrival (Anreise, format: date)
* Departure (Abreise, format: date)
* Type of Occupancy (Belegungstyp, format: selection between Buchung, Stornierung, Eigenbelegung)
* Firstname (Vorname, format: text)
* Lastname (Nachname, format: text)
* Type of Booking (Buchungstyp, format: selection between the possible sources of booking)
Usually, the view is shared as read-only with a special account created specifically for this project (e.g., the account is named 'fewo').

In the Calendar app, you need an empty calendar, which you will use for pushing the booking dates into. I recommend that you create the calendar with your personal Nextcloud account and share it with the special account created specifically for this project.

### Python
For development, I used Python 3.10. Install Python 3.10 in your Linux distribution (Debian/Ubuntu) with the following command:

    sudo apt install python3

After this, install the required Python dependencies:

    pip install python-dotenv pycurl certifi caldav icalendar pytz

## Installation & Configuration

First, clone this repository:

    git clone https://github.com/Longjogger/fewo-calendar.git

After that, rename the ```sample.env``` file into ```.env```:

    mv sample.env .env

