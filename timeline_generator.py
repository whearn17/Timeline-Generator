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
            config = json.load(f)
            return config['events']  # Dive into the 'events' key
    except FileNotFoundError:
        print(f"Config file {filename} not found!")
        exit(1)


def get_event_info(event_name, config):
    details = config.get(event_name)  # Directly look up the event using its name.
    if details:
        return details
    # If no matching event details found, return a default.
    return {
        "name": "Unknown Event",
        "description": "No description for this event.",
        "source": "Unknown Source"
    }


def process_csv_file(filename):
    events = []

    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row["Time"]
                try:
                    date = datetime.strptime(date_str, DATE_FORMAT_24HR)
                except ValueError:
                    date = datetime.strptime(date_str, DATE_FORMAT_12HR)

                operation = row["Event"]
                args = {k: v for k, v in row.items() if k.startswith('arg')}
                events.append((date, operation, args))
    except FileNotFoundError:
        print(f"CSV file {filename} not found!")
        exit(1)

    events.sort(key=lambda x: x[0])
    return events


def get_event_name(operation, event_config):
    return event_config.get(operation, {}).get("name", "Unknown Event")


def generate_timeline(events):
    timeline = ""
    current_date = None

    for event in events:
        date, operation, args = event

        # If we're on a new day, add the date header.
        if current_date != date.date():
            timeline += "{}\n".format(date.strftime('%B %d, %Y'))
            current_date = date.date()

        timeline += format_operation(date, operation, args, config)

    return timeline


def format_operation(date, operation, args, config):
    time_str = date.strftime('%H:%M')
    event_info = get_event_info(operation, config)
    combined_name = "[{}] {}".format(event_info["source"], event_info["name"])
    description = event_info["description"].format(**args)  # This line dynamically inserts args.

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
