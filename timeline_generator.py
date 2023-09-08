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
    return config.get(operation, {"name": "Unknown Event", "description": "No description for this event.",
                                  "source": "Unknown Source"})


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
    consecutive_operation_count = 1
    last_operation = ""
    start_time_of_consecutive_operations = None

    for event in events:
        date, operation, ip_address, extended_details = event

        if last_operation == "builtin\\date change":
            last_operation = operation

        # If we're on a new day, add the date header.
        if current_date != date.date():
            timeline += "{}\n".format(date.strftime('%B %d, %Y'))
            current_date = date.date()

            timeline += format_operation(date, operation, ip_address, extended_details, config["events"],
                                         consecutive_operation_count, start_time_of_consecutive_operations)
            consecutive_operation_count = 1
            start_time_of_consecutive_operations = date
            last_operation = "builtin\\date change"

        # If we are on the same day/same kind of event as last, don't add, just count
        elif current_date == date.date() and last_operation == operation and not extended_details:
            consecutive_operation_count += 1

        # If we are on same day but different op, stop count and add op to timeline
        elif current_date == date.date() and (last_operation != operation or extended_details):
            timeline += format_operation(date, operation, ip_address, extended_details, config["events"],
                                         consecutive_operation_count, start_time_of_consecutive_operations)

            consecutive_operation_count = 1
            start_time_of_consecutive_operations = date
            last_operation = operation

    # Ensure to add the last entry if needed
    if consecutive_operation_count > 1 or (
            consecutive_operation_count == 1 and last_operation != "builtin\\date change"):
        timeline += format_operation(date, last_operation, ip_address, extended_details, config["events"],
                                     consecutive_operation_count, start_time_of_consecutive_operations)

    return timeline


def format_operation(date, operation, ip_address, extended_details, config, operation_count, start_time):
    if operation_count > 1:
        time_str = "{}-{}".format(start_time.strftime('%H:%M'), date.strftime('%H:%M'))
    else:
        time_str = date.strftime('%H:%M')

    event_info = get_event_info(operation, config)
    combined_name = "[{}] {}".format(event_info["source"], event_info["name"])
    description = event_info["description"].format(IP=ip_address, count=operation_count)

    # If extended details exist for the event, append it to the description.
    if extended_details:
        description += " ({})".format(extended_details)

    return "{}\t{}\t{}\n".format(time_str, combined_name, description)


if __name__ == "__main__":
    config = load_config()

    parser = argparse.ArgumentParser(description="Generate a timeline from a CSV file and copy it to the clipboard.")
    parser.add_argument("filename", help="Path to the CSV file.")
    args = parser.parse_args()

    events = process_csv_file(args.filename)
    timeline = generate_timeline(events)
    pyperclip.copy(timeline)
    print("Timeline copied to clipboard!")
