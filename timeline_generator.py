import csv
from datetime import datetime
import pyperclip
import argparse
import json

DATE_FORMAT_24HR = '%m/%d/%y %H:%M'
DATE_FORMAT_12HR = '%m/%d/%y %I:%M'


def load_config(filename="config.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {filename} not found!")
        exit(1)


def get_event_info(operation, config):
    return config.get(operation, {"name": "Unknown Event", "description": "No description for this event.", "source": "Unknown Source"})


def process_csv_file(filename):
    events = []

    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row["LastAccessed"]
                ip_address = row["IP"]
                extended_details = row.get("ExtendedDetails", "")  # extract extended details

                try:
                    date = datetime.strptime(date_str, DATE_FORMAT_24HR)
                except ValueError:
                    date = datetime.strptime(date_str, DATE_FORMAT_12HR)

                operation = row["Operation"]
                events.append((date, operation, ip_address, extended_details))
    except FileNotFoundError:
        print(f"CSV file {filename} not found!")
        exit(1)

    events.sort(key=lambda x: x[0])
    return events


def get_event_name(operation, event_config):
    return event_config.get(operation, {"name": "Unknown Event"})["name"]


def generate_timeline(events):
    timeline = ""
    current_date = None

    for event in events:
        date, operation, ip_address, extended_details = event
        event_name = get_event_name(operation, config["events"])

        # If we're on a new day, add the date header.
        if current_date != date.date():
            timeline += "{}\n".format(date.strftime('%B %d, %Y'))
            current_date = date.date()

        # Directly format each operation as its own line
        timeline += format_operation(date, operation, ip_address, extended_details, config["events"])

    return timeline


def format_operation(date, operation, ip_address, extended_details, config):
    time_str = date.strftime('%H:%M')

    event_info = get_event_info(operation, config)
    combined_name = "[{}] {}".format(event_info["source"], event_info["name"])
    description = event_info["description"].format(IP=ip_address)

    # If extended details exist for the event, append it to the description.
    if extended_details:
        description += " ({})".format(extended_details)

    return "{}\t{}: {}\n".format(time_str, combined_name, description)


if __name__ == "__main__":
    config = load_config()

    parser = argparse.ArgumentParser(description="Generate a timeline from a CSV file and copy it to the clipboard.")
    parser.add_argument("filename", help="Path to the CSV file.")
    args = parser.parse_args()

    events = process_csv_file(args.filename)
    timeline = generate_timeline(events)
    pyperclip.copy(timeline)
    print("Timeline copied to clipboard!")
