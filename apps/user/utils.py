from pathlib import Path
import os, json

base_dir = Path(__file__).parent.parent
base_dir = os.path.join(base_dir, "user/fixtures/")

def get_countries_from_file():
    countries = []
    with open(base_dir+"country.json", "r") as output_file:
        responses = json.loads(output_file.read())
        countries = responses
    return responses

def get_state_by_country_code_from_file(country_code):
    country_code = country_code.upper()
    states = []
    with open(base_dir+"states.json", "r") as output_file:
        responses = json.loads(output_file.read())
    for response in responses:
        if response["country_code"] == country_code:
            states = response["states"]
    return states



