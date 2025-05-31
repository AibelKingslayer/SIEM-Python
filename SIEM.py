import win32evtlog
import pytz
import datetime
import requests
import logging
import time

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

EVENTS_TO_MONITOR = {
    4624: ("Successful Logon", ["Account Name"], "🟢"),
    4625: ("Failed Logon Attempt", ["Account Name"], "❌"),
    4720: ("User Account Created", ["Target Account Name"], "👤"),
    4723: ("Password Change Attempt", ["Target Account Name"], "🔑"),
    4724: ("Password Reset Attempt", ["Target Account Name"], "🔓"),
    11707: ("Application Installed", ["Product"], "📦"),
    6416: ("USB Device Inserted", ["Device Name"], "🔧"),
}

IGNORED_ACCOUNTS = {
    "SYSTEM",
    "NETWORK SERVICE",
    "LOCAL SERVICE",
    "ANONYMOUS LOGON",
    "DWM",
}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

processed_events = set()

def send_discord_notification(event_title, event_id, event_time, source, details, emote):
    payload = {
        "embeds": [
            {
                "title": f"{emote} {event_title}",
                "fields": [
                    {"name": "🆔 Event ID", "value": f"`{event_id}`", "inline": True},
                    {"name": "⌚ Time", "value": f"`{event_time}`", "inline": True},
                    {"name": "💻 Source", "value": f"`{source}`", "inline": True},
                    {"name": "📜 Details", "value": f"`{details}`", "inline": False},
                ],
                "color": 0xFF0000,
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Discord notification sent for Event ID {event_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Discord notification: {e}")

def extract_event_details(event_id, event_data):
    if not event_data:
        return "No details available."
    if event_id in [4624, 4625]:
        if len(event_data) >= 5:
            account_name = event_data[5].strip()
            if account_name and account_name not in IGNORED_ACCOUNTS:
                return f"Account Name: {account_name}"
            else:
                return f"Account Name: {account_name} (ignored)"
        else:
            return "Account Name: Not found"
    
    elif event_id in [4720, 4723, 4724]:
        if len(event_data) >= 1:
            target_account = event_data[0].strip()
            if target_account and target_account not in IGNORED_ACCOUNTS:
                return f"Target Account: {target_account}"
            else:
                return f"Target Account: {target_account} (ignored)"
        else:
            return "Target Account: Not found"
    
    elif event_id == 11707:
        if len(event_data) >= 1:
            product_name = event_data[0].strip()
            return f"Installed Application: {product_name}"
        else:
            return "Installed Application: Not found"
    
    elif event_id == 6416:
        if len(event_data) >= 1:
            device_name = None
            for item in event_data:
                if isinstance(item, str) and "DeviceName" in item:
                    device_name = item.split(":")[-1].strip()
                    break
        
            if device_name:
                return f"Device Name: {device_name}"
            else:
                return "Device Name: Unknown"
        else:
            return "Device Name: Not found"


def monitor_event_logs():
    logs_to_monitor = ["Security", "Application"]
    logging.info("🚀 Starting Windows Event Log Monitor...")
    event_handles = {log: win32evtlog.OpenEventLog(None, log) for log in logs_to_monitor}
    script_start_time = datetime.datetime.now(pytz.utc)
    logging.info(f"Script start time: {script_start_time}")
    
    for log in logs_to_monitor:
        try:
            while True:
                events = win32evtlog.ReadEventLog(
                    event_handles[log],
                    win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
                    0
                )
                if not events:
                    break
        except Exception as e:
            logging.error(f"Error skipping old events in log {log}: {e}")
    
    logging.info("Finished skipping old events. Now monitoring for new events.")
    
    while True:
        for log in logs_to_monitor:
            try:
                events = win32evtlog.ReadEventLog(
                    event_handles[log],
                    win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
                    0
                )
                
                if events:
                    for event in events:
                        event_time = event.TimeGenerated.replace(tzinfo=pytz.utc)
                        event_record_number = event.RecordNumber
                        event_id = event.EventID
                        logging.debug(
                            f"Processing event - Log: {log}, RecordNumber: {event_record_number}, "
                            f"EventID: {event_id}, TimeGenerated: {event_time}"
                        )
                        if event_time < script_start_time or event_record_number in processed_events:
                            logging.debug(
                                f"Skipping event - Log: {log}, RecordNumber: {event_record_number}, "
                                f"EventID: {event_id}, TimeGenerated: {event_time}"
                            )
                            continue
                        
                        if event_id in EVENTS_TO_MONITOR:
                            event_title, _, emote = EVENTS_TO_MONITOR[event_id]
                            event_source = event.SourceName
                            event_data = event.StringInserts or []
                            details = extract_event_details(event_id, event_data)
                            if "ignored" not in details and "Not found" not in details:
                                send_discord_notification(event_title, event_id, event_time, event_source, details, emote)
                        processed_events.add(event_record_number)
            
            except Exception as e:
                logging.error(f"Error reading event log {log}: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    monitor_event_logs()
