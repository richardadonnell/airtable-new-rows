import json
import os
import pickle
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


class AirtableWatcher:
    def __init__(self, base_id, table_id, api_key, webhook_url):
        self.base_id = base_id
        self.table_id = table_id
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.api_url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Load last check time from file
        self.last_check_file = Path('last_check.pickle')
        self.last_check_time = self._load_last_check_time()
        print(f"Last check time loaded: {self.last_check_time}")

    def _load_last_check_time(self):
        """Load the last check time from file, or return a default time if file doesn't exist"""
        try:
            if self.last_check_file.exists():
                with open(self.last_check_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Error loading last check time: {e}")
        # If file doesn't exist or there's an error, return current time
        return datetime.now()

    def _save_last_check_time(self, check_time):
        """Save the last check time to file"""
        try:
            with open(self.last_check_file, 'wb') as f:
                pickle.dump(check_time, f)
        except Exception as e:
            print(f"Error saving last check time: {e}")

    def get_records(self):
        try:
            # Modified filter formula to check for empty Score AND empty Proposal
            params = {
                'filterByFormula': 'AND({Score} = "", {Proposal} = "")',
                'sort[0][field]': 'Created',
                'sort[0][direction]': 'desc'
            }
            
            # Add debug logging for the API request
            print(f"Fetching records with params: {json.dumps(params, indent=2)}")
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                print(f"API Response Status: {response.status_code}")
                print(f"API Response Body: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            records = data.get('records', [])
            
            # Add debug logging for the response
            print(f"Successfully fetched {len(records)} unscored records")
            if records:
                print("First record fields:")
                print(json.dumps(records[0]['fields'], indent=2))
            
            return records
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error fetching records: {e.response.status_code} - {e.response.text}")
            else:
                print(f"Error fetching records: {e}")
            return []

    def send_to_webhook(self, record):
        try:
            webhook_data = {
                'airtable_record_id': record['id'],
                'created_time': record['createdTime'],
                'url': record['fields'].get('url', ''),
                'title': record['fields'].get('title', ''),
                'description': record['fields'].get('description', ''),
                'budget': record['fields'].get('budget', 'N/A'),
                'hourly_range': record['fields'].get('hourlyRange', 'N/A'),
                'estimated_time': record['fields'].get('estimatedTime', 'N/A'),
                'skills': record['fields'].get('skills', ''),
                'created_date': record['fields'].get('Created', ''),
                'proposal': record['fields'].get('Proposal', '')  # Added Proposal field
            }
            
            response = requests.post(
                self.webhook_url,
                json=webhook_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            print(f"Successfully sent unscored job listing to Make.com webhook: {record['id']}")
            print(f"Data sent: {json.dumps(webhook_data, indent=2)}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending to webhook: {e}")
            return False

    def check_new_records(self):
        """Single run to check and process unscored records"""
        print(f"Checking for unscored records")
        current_time = datetime.now()
        records = self.get_records()  # This will now only get unscored records
        records_processed = False
        
        if records:
            for record in records:
                print(f"Processing unscored record: {record['id']}")
                if self.send_to_webhook(record):
                    records_processed = True
        
        if records_processed:
            self._save_last_check_time(current_time)
            print(f"Updated last check time to: {current_time}")
        else:
            print("No unscored records found")

def main():
    load_dotenv()
    
    BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    TABLE_ID = os.getenv("AIRTABLE_TABLE_ID")
    API_KEY = os.getenv("AIRTABLE_API_KEY")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    if not all([BASE_ID, TABLE_ID, API_KEY, WEBHOOK_URL]):
        print("Please set all required environment variables")
        return

    watcher = AirtableWatcher(BASE_ID, TABLE_ID, API_KEY, WEBHOOK_URL)
    watcher.check_new_records()

if __name__ == "__main__":
    main()
