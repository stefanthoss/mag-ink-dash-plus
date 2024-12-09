"""
This is where we retrieve events from an ICS calendar.
"""

import datetime as dt

import structlog

from ics_cal.icshelper import IcsHelper


class IcsModule:
    def __init__(self):
        self.logger = structlog.get_logger()
        self.calHelper = IcsHelper()

    def get_short_time(self, datetimeObj):
        datetime_str = ""
        if datetimeObj.minute > 0:
            datetime_str = ".{:02d}".format(datetimeObj.minute)

        if datetimeObj.hour == 0:
            datetime_str = "12{}am".format(datetime_str)
        elif datetimeObj.hour == 12:
            datetime_str = "12{}pm".format(datetime_str)
        elif datetimeObj.hour > 12:
            datetime_str = "{}{}pm".format(str(datetimeObj.hour % 12), datetime_str)
        else:
            datetime_str = "{}{}am".format(str(datetimeObj.hour), datetime_str)
        return datetime_str

    def get_events(self, ics_url, calStartDatetime, calEndDatetime, displayTZ, numDays):
        eventList = self.calHelper.retrieve_events(
            ics_url, calStartDatetime, calEndDatetime, displayTZ
        )

        calDict = {}

        for event in eventList:
            if event["isMultiday"]:
                numDays = (event["endDatetime"].date() - event["startDatetime"].date()).days
                for day in range(0, numDays):
                    calDict.setdefault(
                        event["startDatetime"].date() + dt.timedelta(days=day), []
                    ).append(event)
            else:
                calDict.setdefault(event["startDatetime"].date(), []).append(event)

        return sorted(calDict.items(), key=lambda x: x[0])
