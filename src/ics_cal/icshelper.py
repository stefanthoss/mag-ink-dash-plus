#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is where we retrieve events from the ICS calendar.
"""

from __future__ import print_function

import datetime as dt
import sys

import arrow
import requests
import structlog
from ics import Calendar


class IcsHelper:
    def __init__(self):
        self.logger = structlog.get_logger()

    def retrieve_events(self, ics_url, startDatetime, endDatetime, localTZ):
        # Call the ICS calendar and return a list of events that fall within the specified dates
        event_list = []

        self.logger.info("Retrieving events from ICS...")
        response = requests.get(ics_url)
        if response.ok:
            cal = Calendar(response.text)
        else:
            self.logger.error(f"Received an error when downloading ICS: {response.text}")
            sys.exit(1)

        if not cal.events:
            self.logger.info("No upcoming calendar events found.")
        for event in cal.events:
            if event.begin >= arrow.Arrow.fromdatetime(
                startDatetime
            ) and event.begin < arrow.Arrow.fromdatetime(endDatetime):
                # extracting and converting events data into a new list
                new_event = {"summary": event.name}

                if event.location:
                    new_event["location"] = event.location

                new_event["allday"] = event.all_day
                if new_event["allday"]:
                    # All-day events are always midnight UTC to midnight UTC, therefore timezone needs to be set
                    new_event["startDatetime"] = dt.datetime.fromisoformat(
                        event.begin.replace(tzinfo=localTZ).isoformat()
                    )
                    new_event["endDatetime"] = dt.datetime.fromisoformat(
                        event.end.replace(tzinfo=localTZ).isoformat()
                    )
                else:
                    # Other events need to be translated to local timezone
                    new_event["startDatetime"] = dt.datetime.fromisoformat(
                        event.begin.to(localTZ).isoformat()
                    )
                    new_event["endDatetime"] = dt.datetime.fromisoformat(
                        event.end.to(localTZ).isoformat()
                    )

                new_event["isMultiday"] = (
                    new_event["endDatetime"] - new_event["startDatetime"]
                ) > dt.timedelta(days=1)

                event_list.append(new_event)

        return event_list
