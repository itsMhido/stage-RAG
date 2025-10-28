import json
import csv
import sys

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary structure.
    
    Args:
        d: Dictionary to flatten
        parent_key: Key from parent level
        sep: Separator for nested keys
    
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to JSON strings to preserve structure
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))
    
    return dict(items)

def json_to_csv(json_file, csv_file):
    """
    Convert JSON file to CSV format.
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both single object and array of objects
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            print("Error: JSON must be an object or array of objects")
            return
        
        if not data:
            print("Error: JSON file is empty")
            return
        
        # Flatten all records
        flattened_data = [flatten_dict(record) for record in data]
        
        # Get all unique keys across all records
        all_keys = set()
        for record in flattened_data:
            all_keys.update(record.keys())
        
        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)
        
        # Write to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        print(f"✓ Successfully converted {json_file} to {csv_file}")
        print(f"  Records: {len(flattened_data)}")
        print(f"  Columns: {len(fieldnames)}")
        
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Default files
    input_file = "data.json"
    output_file = "data.csv"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    json_to_csv(input_file, output_file)