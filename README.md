# Fewo-Calendar
Read holiday apartment (Ferienwohung \[Fewo\]) bookings from Nextcloud Table and import them in a calendar via CalDav.

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
Usually, the view is shared as read-only with a special account created specifically for this task (e.g., the account is named 'fewo').

In the Calendar app, you need an empty calendar, which you will use for pushing the booking dates into.