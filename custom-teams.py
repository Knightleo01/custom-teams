#!/usr/bin/env python3

import sys
import json
import logging
import os
import urllib3
import ssl
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil import parser

class TeamsWebhookException(Exception):
    pass

class ConnectorCard:
    def __init__(self, hookurl, payload, http_timeout=60):
        cert_reqs = ssl.CERT_NONE
        self.http = urllib3.PoolManager(cert_reqs=cert_reqs)
        self.payload = payload
        self.hookurl = hookurl
        self.http_timeout = http_timeout

    def send(self):
        logging.debug(self.payload)
        headers = {"Content-Type": "application/json"}
        r = self.http.request(
            'POST',
            f'{self.hookurl}',
            body=json.dumps(self.payload).encode('utf-8'),
            headers=headers,
            timeout=self.http_timeout
        )
        if r.status == 200:
            now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%d/%m/%Y %H:%M:%S")
            logging.info("Sent Alert at %s", now)
            return True
        else:
            logging.fatal(r.reason)
            raise TeamsWebhookException(r.reason)

# Modo DEBUG
DEBUG = "DEBUG" in sys.argv

# Logging
logLocation = "/var/ossec/logs/microsoft-teams.log"
if DEBUG:
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.DEBUG)
else:
    if not os.path.exists(logLocation):
        open(logLocation, "w+").close()
    logging.basicConfig(filename=logLocation, level=logging.INFO)

logging.debug("Executing Microsoft Teams Plugin")

# Carrega o alerta
with open(sys.argv[1]) as f:
    alert = json.load(f)

webhook = sys.argv[3]
logging.debug(webhook)

# Função para converter timestamp UTC para UTC-3
def convert_timestamp_to_utc3(ts_str):
    if not ts_str:
        return "N/A"
    try:
        dt = parser.isoparse(ts_str)
        dt_utc3 = dt.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
        return dt_utc3.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        logging.error("Erro ao converter timestamp '%s': %s", ts_str, e)
        return ts_str

# Pega o timestamp correto
raw_ts = alert.get("timestamp") or (alert.get("fields", {}).get("timestamp") or ["N/A"])[0]
formatted_timestamp = convert_timestamp_to_utc3(raw_ts)

# Monta payload
payload = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": "",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {"type": "TextBlock", "size": "Large", "weight": "Bolder", "text": "Wazuh Alert"},
                    {"type": "TextBlock", "text": alert.get("rule", {}).get("description", "N/A"), "wrap": True},
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Alert ID", "value": alert.get("id", "N/A")},
                            {"title": "Timestamp", "value": formatted_timestamp},
                            {"title": "Agent ID", "value": alert.get("agent", {}).get("id", "N/A")},
                            {"title": "Agent Name", "value": alert.get("agent", {}).get("name", "N/A")}
                        ]
                    },
                    {
                        "type": "TextBlock", "text": "Rule", "wrap": True, "size": "Large", "weight": "Bolder"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "ID", "value": alert.get("rule", {}).get("id", "N/A")},
                            {"title": "Level", "value": alert.get("rule", {}).get("level", "N/A")},
                            {"title": "Groups", "value": ' '.join(alert.get("rule", {}).get("groups", []))}
                        ]
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.5",
            }
        }
    ]
}

# Envia para o Teams
myTeamsMessage = ConnectorCard(webhook, payload)
myTeamsMessage.send()
