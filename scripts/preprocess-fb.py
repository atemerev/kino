import csv
import re
import sys
from datetime import datetime

def preprocess_facebook_data(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        csv_writer.writerow([
            'id', 'facebook_id', 'first_name', 'last_name', 'gender', 'city', 'hometown',
            'relationship_status', 'workplace', 'timestamp', 'email', 'birthday'
        ])
        
        for line in infile:
            # Split the line by colon, but keep the timestamp intact
            parts = line.strip().split(':')
            
            if len(parts) < 11:
                print(f"Skipping malformed line: {line.strip()}")
                continue
            
            # Extract timestamp from the end of the line
            timestamp_parts = parts[-3:]
            timestamp = ':'.join(timestamp_parts).strip()
            
            try:
                parsed_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')
                year = parsed_timestamp.year
                if 1900 <= year <= 2030:
                    formatted_timestamp = parsed_timestamp.isoformat(sep=' ', timespec='seconds')
                else:
                    formatted_timestamp = ''
            except ValueError:
                formatted_timestamp = ''
            
            # Reconstruct the row
            row = parts[:-3] + [formatted_timestamp] + parts[-1:]
            
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
