# Timeline-Generator

Generate detailed event timelines from CSV files using dynamic configurable event descriptions.

## Table of Contents
* <ins>Running the Program</ins>
* <ins>Building Your Own Configuration File</ins>

## Running the Program
Execute the program using the following command:

```
python timeline_generator.py filename.csv
```

This will process the provided CSV and generate a timeline.txt containing the structured timeline.

## Building Your Own Configuration File
The flexibility of the Timeline Generator lies in its ability to use custom configuration files. This allows users to craft their own event descriptions with dynamic placeholders.

Here's a basic structure for the configuration file:
```
{
  "events": {
    "OPERATION_CODE": {
      "name": "Event Name",
      "description": "This event occurred due to {reason} at location {location}.",
      "source": "Event Source"
    }
    // ... More events can be added in the same format.
  }
}
```

## Explanation:

**OPERATION_CODE** is a unique identifier for an event type from the CSV.
**{placeholders}** in the description will be replaced by their corresponding values from the CSV file.

## Contributing
Interested in making improvements? Open a PR or an issue to discuss potential changes/additions.
