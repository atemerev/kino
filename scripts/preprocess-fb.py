import csv
import re
import sys
from datetime import datetime

def format_date(date_string):
    try:
        # Try parsing with year
        date = datetime.strptime(date_string, '%m/%d/%Y')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Try parsing without year
            date = datetime.strptime(date_string, '%m/%d')
            return date.strftime('%m-%d')
        except ValueError:
            return ''

def preprocess_facebook_data(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        csv_writer.writerow([
            'phone', 'facebook_id', 'first_name', 'last_name', 'gender', 'city', 'hometown',
            'relationship_status', 'workplace', 'timestamp', 'email', 'birthday'
        ])
        
        for line in infile:
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
                print(f"Skipping malformed line: {line.strip()}")
                continue
            
            try:
                if timestamp:
                    parsed_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')
                    year = parsed_timestamp.year
                    if 1900 <= year <= 2030:
                        formatted_timestamp = parsed_timestamp.isoformat(sep=' ', timespec='seconds')
                    else:
                        formatted_timestamp = ''
                else:
                    formatted_timestamp = ''
            except ValueError:
                formatted_timestamp = ''
            
            # Handle email and birthday
            email = parts[10]
            birthday = parts[11]
            
            # Format birthday if present
            formatted_birthday = format_date(birthday) if birthday else ''
            
            # Create row with 12 columns
            row = parts[:9] + [formatted_timestamp, email, formatted_birthday]
            
            # Write the processed row
            csv_writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess-fb.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    preprocess_facebook_data(input_file, output_file)
    print(f"Preprocessed data saved to {output_file}")
