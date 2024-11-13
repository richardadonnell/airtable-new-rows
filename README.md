# airtable-new-rows

Used in conunction with https://github.com/richardadonnell/Upwork-Job-Scraper

A Python automation tool that monitors Airtable for new unscored records and forwards them to Make.com webhooks. This tool is used in combination with a Make.com workflow to automatically score new records.

## Overview

This tool helps automate workflow by:

- Monitoring specified Airtable base/table for new records
- Filtering for records where both Score and Proposal fields are empty
- Sending filtered records to a Make.com webhook
- Maintaining state by tracking the last check time

## Prerequisites

- Python 3.x
- Access to Airtable API
- Make.com (formerly Integromat) webhook URL

## Installation

1. Clone the repository:

```sh
git clone https://github.com/richardadonnell/airtable-new-rows
```

2. Navigate to project directory:

```sh
cd airtable-new-rows
```

3. Install required dependencies:

```sh
pip install requests python-dotenv
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_ID=your_table_id
AIRTABLE_API_KEY=your_api_key
WEBHOOK_URL=your_make_webhook_url
```

## Usage

Run the script:

```sh
python main.py
```

The script will:

1. Check for records with empty Score and Proposal fields
2. Send matching records to your Make.com webhook
3. Store the last check time for reference

## Data Format

The webhook sends the following data for each record:

- Record ID
- Created Time
- URL
- Title
- Description
- Budget
- Hourly Range
- Estimated Time
- Skills
- Created Date
- Proposal Status

## State Management

The tool maintains state using a `last_check.pickle` file to track the last successful check time.
