import csv
import re
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
            parts = re.split(r':(?![/\d])', line.strip())
            
            if len(parts) < 10:
                print(f"Skipping malformed line: {line.strip()}")
                continue
            
            # Extract timestamp
            timestamp = parts[-3]
            try:
                parsed_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')
                formatted_timestamp = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_timestamp = ''
            
            # Reconstruct the row without the timestamp
            row = parts[:-3] + [formatted_timestamp] + parts[-2:]
            
            # Write the processed row
            csv_writer.writerow(row)

if __name__ == "__main__":
    input_file = "data/sample-facebook.txt"
    output_file = "data/processed-facebook.csv"
    preprocess_facebook_data(input_file, output_file)
    print(f"Preprocessed data saved to {output_file}")
