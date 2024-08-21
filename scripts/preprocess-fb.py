import csv
import re
import sys
from datetime import datetime
from tqdm import tqdm

def format_date(date_string):
    try:
        # Only parse dates with year
        date = datetime.strptime(date_string, '%m/%d/%Y')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        return ''

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
    
    # Format birthday if present and contains a year
    formatted_birthday = format_date(birthday) if birthday and len(birthday.split('/')) == 3 else ''
    
    # Create row with 13 columns (including the raw data)
    return parts[:9] + [formatted_timestamp, email, formatted_birthday, original_line]

def preprocess_facebook_data(input_file, output_file):
    # Count the number of lines in the input file
    with open(input_file, 'r') as f:
        total_lines = sum(1 for _ in f)

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        csv_writer.writerow([
            'phone', 'facebook_id', 'first_name', 'last_name', 'gender', 'current_location', 'origin_location',
            'relationship_status', 'workplace', 'timestamp', 'email', 'birthday', 'raw'
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
