import requests
import os
import json

from llm_usage import infer_with_template

claims_endpoint = os.environ.get("CLAIMS_ENDPOINT")+"/db/claims"

def upload_location(claim_id, location):
    upload_endpoint = claims_endpoint + f"/{claim_id}/location"
    data = {
        "location": location,
    }
    headers = {'accept': 'application/json'}
    response = requests.post(upload_endpoint, headers=headers, params=data)

    if response.status_code!=200:
        raise Exception(f"{response.status_code} {response.text}")
    

def get_location(claim_id = None):    
    claim_endpoint = claims_endpoint + f"/{claim_id}"
    claim_info = requests.get(claim_endpoint).json()
    claim_body = claim_info["body"]
    
    with open('templates/location_template.txt') as f:
        template = f.read()
    
    location = infer_with_template(claim_body, template)
    print(location)
    upload_location(claim_id, location)


def batch_get_location(claim_ids = None):    
    if not claim_ids:
        with open('claims.json') as f:
            claim_ids = json.load(f)["claim_ids"]
                
    print(f"processing claims: {claim_ids}")
    
    for claim_id in claim_ids:
        get_location(claim_id)
    
if __name__ == '__main__':
    location = batch_get_location()