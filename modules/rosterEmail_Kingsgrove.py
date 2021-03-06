import os

import yagmail

from ElvantoAPIExtensions import Enums, Helpers
from modules.__stub__ import ModuleStub


class Module(ModuleStub):
    __VERSION__ = "1.1"
    __NAME__ = "rosterEmail_Kingsgrove"
    __executeTime__ = "10:00"
    __executeDay__ = "tuesday"

    settings = {
        "email": {
            "provider": "gmail",
            "username": "",
            "password": "",
            "ssl": ""
        },
        "general": {
            "serviceName": "",
            "template": ""
        },

        "responsibilities":
            {
                "adminEmail": "",
                "roster": "",
                "metrics": "",
                "offertory": "",
            }

    }

    def validate(self):
        _templateFile = os.path.join("files", self.__NAME__, self.settings["general"]["template"])
        if os.path.isdir(_templateFile) or not os.path.exists(_templateFile):
            raise self.ModuleException("Invalid template file path")
        self._templateFile = _templateFile

    def run(self):
        _serviceDate = Helpers.NextDate(Enums.Days.SUNDAY)
        services = Helpers.ServicesOnDate(self.conn, _serviceDate, ["volunteers"])
        service = next(filter(lambda _: _.name == self.settings["general"]["serviceName"], services))
        volunteerMap = {
            "serviceLeader": "",
            "speaker": "",
            "bibleReader": "",
            "visual": "",
            "audio": "",
            "welcoming": "",
            "music": "",

            "prayer": "",
            "cleaning": "",
            "counters": ""
        }

        query = service.volunteers.byPositionName("Service leader")
        if query:
            volunteerMap["serviceLeader"] = query

        query = service.volunteers.byPositionName("Congregational prayer")
        if query:
            volunteerMap["prayer"] = query

        query = service.volunteers.byPositionName("Speaker")
        if query:
            volunteerMap["speaker"] = query

        query = service.volunteers.byPositionName("Bible reader")
        if query:
            volunteerMap["bibleReader"] = query

        query = service.volunteers.byPositionName("ProPresenter")
        if query:
            volunteerMap["visual"] = query

        query = service.volunteers.byPositionName("Sound Desk")
        if query:
            volunteerMap["audio"] = query

        query = service.volunteers.byPositionName("Welcomers")
        if query:
            volunteerMap["welcoming"] = query

        query = service.volunteers.byPositionName("Worship Leader")
        if query:
            volunteerMap["music"] = query

        query = service.volunteers.byPositionName("Church lockup")
        if query:
            volunteerMap["cleaning"] = query

        query = service.volunteers.byPositionName("Offertory counting")
        if query:
            volunteerMap["counters"] = query

        _volunteerMapResolve = {}
        for key, val in volunteerMap.items():
            _volunteerMapResolve[key] = list(map(lambda _: self.conn.findContact(id = _.id)[0], val))

        _volunteerMapName = {}
        _volunteerMapEmail = {}

        _volunteerMapNameJoin = {}
        _volunteerMapEmailJoin = []
        for position in _volunteerMapResolve:
            nameArray = ["%s %s" % (volunteer["first_name"], volunteer["last_name"]) for volunteer in
                         _volunteerMapResolve[position]]
            _volunteerMapName[position] = nameArray
            _volunteerMapNameJoin[position] = ", ".join(nameArray)

            emailArray = [volunteer["email"] for volunteer in _volunteerMapResolve[position]]
            _volunteerMapEmail[position] = emailArray
            _volunteerMapEmailJoin.extend(emailArray)

        replacements = {
            "serviceLeader": _volunteerMapNameJoin["serviceLeader"],
            "speaker": _volunteerMapNameJoin["speaker"],
            "prayer": _volunteerMapNameJoin["prayer"],

            "bibleReader": _volunteerMapNameJoin["bibleReader"],
            "welcoming": _volunteerMapNameJoin["welcoming"],

            "music": _volunteerMapNameJoin["music"],
            "audio": _volunteerMapNameJoin["audio"],
            "visual": _volunteerMapNameJoin["visual"],

            "cleaning": _volunteerMapNameJoin["cleaning"],
            "counters": _volunteerMapNameJoin["counters"],

            "Dmmyyyy": _serviceDate.strftime("%A, %#d %B %Y"),

            "metricsAdmin": self.settings["responsibilities"]["metrics"],
            "offertoryAdmin": self.settings["responsibilities"]["offertory"],
            "rosterAdmin": self.settings["responsibilities"]["roster"]
        }

        with open(self._templateFile, "r") as template:
            body = template.read()
        for key in replacements:
            body = body.replace("{" + key + "}", replacements[key])

        if self.settings["email"]["provider"].lower() == "gmail":
            customSMTPServer = False
        else:
            customSMTPServer = self.settings["email"]["provider"].split(":")[-2:] + [465]
            # Add default SSL port if the user does not add

        smtpDetails = {
            "user": self.settings["email"]["username"],
            "password": self.settings["email"]["password"],
            "host": customSMTPServer[0] if customSMTPServer else "smtp.gmail.com",
            "port": int(customSMTPServer[1]) if customSMTPServer else 465,
            "smtp_ssl": (self.settings["email"]["ssl"].lower() == "true") if customSMTPServer else True,
        }

        mailer = yagmail.SMTP(**smtpDetails)
        # mailer.send(to=_volunteerMapEmailJoin,
        #             cc=self.settings["responsibilities"]["adminEmail"],
        #             subject=self.settings["general"]["serviceName"] + " Worship Team | " + _serviceDate.strftime("%D"),
        #             contents=[yagmail.raw(body)],
        #             headers={
        #                 "Reply-To": self.settings["responsibilities"]["adminEmail"]
        #             })
        mailer.send(to = "andrew.j.wong@outlook.com",
                    # cc=self.settings["responsibilities"]["adminEmail"],
                    subject = "PRODUCTION TEST | " + self.settings["general"][
                        "serviceName"] + " Worship Team | " + _serviceDate.strftime("%D"),
                    contents = [yagmail.raw(body)],
                    headers = {
                        "Reply-To": self.settings["responsibilities"]["adminEmail"]
                    })
