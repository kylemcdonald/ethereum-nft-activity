import json
import datetime

def load_etherscan_api_key():
    with open('env.json') as file:
        payload = json.load(file)
        return payload['etherscan-api-key']

def load_contacts():
    with open('data/contracts.json') as file:
        return json.load(file)

def write_results(output):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    result_filepath = f'./output/{current_datetime}.json'
    with open(result_filepath, 'w') as jsonFile:
        json.dump(output, jsonFile)
        jsonFile.close()
    print(f'Emissions results saved to {result_filepath}')