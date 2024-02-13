import os
import re
import json
import yaml
import requests
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def extract_json_from_script(script_content):
    """Extracts JSON objects from script content."""
    # Find all potential JSON objects in the script content
    matches = re.findall(r'({[^{]*?})', script_content, re.DOTALL)
    # Try to parse each match as JSON and add to the list if successful
    return [json.loads(match) for match in matches if is_valid_json(match)]

def is_valid_json(json_string):
    """Checks if a string is valid JSON."""
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

def get_domain_name(url):
    """Extracts the domain name from a URL."""
    # Parse the URL to extract the hostname
    hostname = urlparse(url).hostname or 'default_domain'
    # Return the second last part of the hostname (the domain name) if it exists, otherwise return 'default_domain'
    return hostname.split('.')[-2] if hostname else 'default_domain'

def create_output_directory(base_dir, domain_name):
    """Creates an output directory for a specific domain."""
    # Create a subdirectory for the domain within the base directory
    domain_output_dir = os.path.join(base_dir, domain_name)
    # Create the domain-specific directory if it doesn't exist
    os.makedirs(domain_output_dir, exist_ok=True)
    return domain_output_dir

def fetch_html_content(url):
    """Fetches and returns the HTML content of a URL."""
    # Send a GET request to the URL and return the response text
    response = requests.get(url)
    return response.text

def extract_json_data_from_html(html_content):
    """Extracts all JSON data from HTML content."""
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all script tags in the parsed HTML
    scripts = soup.find_all('script')
    # Try to extract JSON data from each script and add to the list if successful
    return [data for script in scripts for data in extract_json_from_script(script.text) if data]

def save_data_as_yaml(data, output_dir, domain_name):
    """Saves data as a YAML file in the specified directory."""
    # Get the current timestamp to use in the filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Convert the data to a YAML string
    yaml_data = yaml.dump(data, allow_unicode=True, indent=2, sort_keys=False, default_flow_style=False)
    # Create the filename using the domain name and timestamp
    filename = f'{domain_name}_api_data_{timestamp}.yaml'
    # Determine the full path to the output file
    full_path = os.path.join(output_dir, filename)
    # Write the YAML data to the output file
    with open(full_path, 'w') as yaml_file:
        yaml_file.write(yaml_data)
    print(f"YAML data saved to {full_path}")

def main():
    # Prompt the user to enter a URL
    url = input("Enter the URL to fetch: ")
    # Determine the base output directory based on the script's location
    base_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S4Y Output")
    # Extract the domain name from the URL
    domain_name = get_domain_name(url)
    # Create an output directory for the domain
    domain_output_dir = create_output_directory(base_output_dir, domain_name)
    # Fetch the HTML content of the URL
    html_content = fetch_html_content(url)
    # Extract all JSON data from the HTML content
    json_data = extract_json_data_from_html(html_content)
    # Save the JSON data as a YAML file in the output directory
    save_data_as_yaml(json_data, domain_output_dir, domain_name)

if __name__ == "__main__":
    main()