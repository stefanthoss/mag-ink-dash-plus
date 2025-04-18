#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is where we retrieve events from the ICS calendar.
"""

import datetime as dt
import sys

import icalendar
import pytz
import recurring_ical_events
import requests
import structlog


class IcsHelper:
    def __init__(self):
        self.logger = structlog.get_logger()

    def retrieve_events(self, ics_url, calStartDatetime, calEndDatetime, localTZ):
        # Call the ICS calendar and return a list of events that fall within the specified dates
        event_list = []

        self.logger.info("Retrieving events from ICS...")
        response = requests.get(ics_url)
        if response.ok:
            cal = icalendar.Calendar.from_ical(response.text)
        else:
            self.logger.error(f"Received an error when downloading ICS: {response.text}")
            sys.exit(1)

        events = recurring_ical_events.of(cal).between(calStartDatetime, calEndDatetime)
        local_timezone = pytz.timezone(localTZ)

        for event in events:
            new_event = {"summary": str(event.get("SUMMARY"))}

            if "LOCATION" in event:
                new_event["location"] = str(event.get("LOCATION"))

            event_start = event.get("DTSTART").dt
            event_end = event.get("DTEND").dt

            if isinstance(event_start, dt.datetime):
                new_event["allday"] = False
                new_event["startDatetime"] = event_start.astimezone(local_timezone)
                new_event["endDatetime"] = event_end.astimezone(local_timezone)
            elif isinstance(event_start, dt.date):
                new_event["allday"] = True
                # Convert date into datetime at midnight
                new_event["startDatetime"] = local_timezone.localize(
                    dt.datetime.combine(event_start, dt.time(0, 0))
                )
                new_event["endDatetime"] = local_timezone.localize(
                    dt.datetime.combine(event_end, dt.time(0, 0))
                )
            else:
                raise TypeError(f"Unknown type {type(event_start)} for DTSTART")

            new_event["isMultiday"] = (
                new_event["endDatetime"] - new_event["startDatetime"]
            ) > dt.timedelta(days=1)

            if (
                new_event["endDatetime"] >= calStartDatetime
                and new_event["startDatetime"] < calEndDatetime
            ):
                # Don't show past days for ongoing multiday event
                new_event["startDatetime"] = max(new_event["startDatetime"], calStartDatetime)

                event_list.append(new_event)

        return sorted(event_list, key=lambda k: k["startDatetime"])
