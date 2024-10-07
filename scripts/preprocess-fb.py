import csv
import re
import sys
from uuid_extensions import uuid7str
from datetime import datetime
from tqdm import tqdm

SENTINEL_DATE = ''
SENTINEL_DATETIME = ''

def format_date(date_string):
    try:
        # Only parse dates with year
        date = datetime.strptime(date_string, '%m/%d/%Y')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        return SENTINEL_DATE

def generate_uuid():
    return uuid7str()

def convert_line(line):
    original_line = line.strip()
    # Use regex to find the timestamp pattern at the end of the line
    match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)', line)
    if match:
        timestamp = match.group(1)
        # Remove the timestamp from the line, but keep the rest
        line = line[:match.start()].strip() + line[match.end():].strip()
    else:
        timestamp = ''
    
    # Split the remaining line by colon
    parts = line.split(':')
    
    if len(parts) != 12:
        return None
    
    try:
        if timestamp:
            parsed_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')
            year = parsed_timestamp.year
            if 1900 <= year <= 2299:
                formatted_timestamp = parsed_timestamp.isoformat(sep=' ', timespec='milliseconds')
            else:
                formatted_timestamp = SENTINEL_DATETIME
        else:
            formatted_timestamp = SENTINEL_DATETIME
    except ValueError:
        formatted_timestamp = SENTINEL_DATETIME
    
    # Handle email, birthday, and workplace
    email = parts[10]
    birthday = parts[11]
    workplace = parts[8]
    
    # Format birthday if present and contains a year
    formatted_birthday = format_date(birthday) if birthday and len(birthday.split('/')) == 3 else SENTINEL_DATE
    
    # Create row with ClickHouse table structure
    return [
        generate_uuid(),  # uuid
        'facebook',  # origin
        'facebook_breach_2019',  # dataset
        datetime.now().isoformat(sep=' ', timespec='milliseconds'),  # ingestion_time
        formatted_timestamp,  # origin_time
        'person',  # type
        original_line,  # raw
        f"{parts[2]} {parts[3]}",  # name
        parts[2],  # first_name
        parts[3],  # last_name
        parts[0],  # phone
        email,  # email
        parts[1],  # origin_id (facebook_id)
        parts[5],  # current_location
        parts[6],  # birth_location
        formatted_birthday,  # date_of_birth
        parts[7],  # relationship_status
        workplace,  # workplace
    ]

def preprocess_facebook_data(input_file, output_file):
    # Count the number of lines in the input file
    with open(input_file, 'r') as f:
        total_lines = sum(1 for _ in f)

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        csv_writer.writerow([
            'uuid', 'origin', 'dataset', 'ingestion_time', 'origin_time', 'type', 'raw',
            'name', 'first_name', 'last_name', 'phone', 'email', 'origin_id',
            'current_location', 'birth_location', 'date_of_birth', 'relationship_status',
            'workplace'
        ])
        
        # Create progress bar
        pbar = tqdm(total=total_lines, desc="Processing", unit="line")
        
        for line in infile:
            pbar.update(1)  # Update progress bar
            row = convert_line(line)
            if row:
                csv_writer.writerow(row)
            else:
                print(f"Skipping malformed line: {line.strip()}")
        
        pbar.close()  # Close the progress bar

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess-fb.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    preprocess_facebook_data(input_file, output_file)
    print(f"Preprocessed data saved to {output_file}")
