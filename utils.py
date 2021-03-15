import json
import datetime

def load_etherscan_api_key():
    with open('env.json') as file:
        payload = json.load(file)
        return payload['etherscan-api-key']

def load_contacts():
    with open('data/contracts.json') as file:
        return json.load(file)

def write_results(output_json):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d at %H.%M.%S')
    result_filepath = f'./output/{current_datetime}.json'
    with open(result_filepath, 'w') as jsonFile:
        json.dump(output_json, jsonFile)
        jsonFile.close()
    print(f'Emissions results saved to file: "{result_filepath}"')