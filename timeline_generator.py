import csv
import json
from datetime import datetime
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATE_FORMAT_24HR = '%m/%d/%y %H:%M'
DATE_FORMAT_12HR = '%m/%d/%y %I:%M'


def load_config(filename="config.json"):
    """Load and return events from the config file."""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
            return config.get('events', {})  # Get the 'events' key or default to an empty dictionary
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading config file {filename}: {e}")
        exit(1)


def get_event_info(event_name, config):
    """Retrieve event details from config."""
    return config.get(event_name, {
        "name": "Unknown Event",
        "description": "No description for this event.",
        "source": "Unknown Source"
    })


def process_csv_file(filename):
    """Process a CSV file and return a sorted list of events."""
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
                args = {k.casefold(): v for k, v in row.items() if k not in ["Time", "Event"]}
                events.append((date, operation, args))
    except (FileNotFoundError, csv.Error) as e:
        logger.error(f"Error processing CSV file {filename}: {e}")
        exit(1)

    events.sort(key=lambda x: x[0])
    return events


def format_operation(date, operation, args, config):
    """Return a formatted operation string."""
    time_str = date.strftime('%H:%M')
    event_info = get_event_info(operation, config)
    combined_name = f"[{event_info['source']}] {event_info['name']}"

    # This line dynamically inserts args.
    formatted_args = {k.casefold(): v for k, v in args.items()}
    description = event_info["description"].format(**formatted_args)

    return f"{time_str}\t{combined_name}\t{description}\n"


def generate_timeline(events, config):
    """Generate a timeline from a list of events."""
    timeline = ""
    current_date = None

    for event in events:
        date, operation, args = event
        if current_date != date.date():
            timeline += f"{date.strftime('%B %d, %Y')}\n"
            current_date = date.date()
        timeline += format_operation(date, operation, args, config)

    return timeline


def save_to_file(timeline, filename="timeline.txt"):
    """Save the generated timeline to a file."""
    with open(filename, 'w') as f:
        f.write(timeline)
    logger.info(f"Timeline saved to {filename}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a timeline from a CSV file and save it to a text file.")
    parser.add_argument("filename", help="Path to the CSV file.")
    args = parser.parse_args()

    config = load_config()
    events = process_csv_file(args.filename)
    timeline = generate_timeline(events, config)
    save_to_file(timeline)
