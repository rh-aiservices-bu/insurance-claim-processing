import requests
import os
import json

from llm_usage import infer_with_template

claims_endpoint = os.environ.get("CLAIMS_ENDPOINT")+"/db/claims"

def upload_accident_time(claim_id, accident_time):
    upload_endpoint = claims_endpoint + f"/{claim_id}/time"
    data = {
        "time": accident_time,
    }
    headers = {'accept': 'application/json'}
    response = requests.post(upload_endpoint, headers=headers, params=data)

    if response.status_code!=200:
        raise Exception(f"{response.status_code} {response.text}")
    

def get_accident_time(claim_id = None):
    claim_endpoint = claims_endpoint + f"/{claim_id}"
    claim_info = requests.get(claim_endpoint).json()
    claim_body = claim_info["body"]
    
    with open('templates/time_template.txt') as f:
        template = f.read()
    
    accident_time = infer_with_template(claim_body, template)
    print(accident_time)
    upload_accident_time(claim_id, accident_time)
    
    
def batch_get_accident_time(claim_ids = None):
    if not claim_ids:
        with open('claims.json') as f:
            claim_ids = json.load(f)["claim_ids"]
            
    print(f"processing claims: {claim_ids}")
    
    for claim_id in claim_ids:
        get_accident_time(claim_id)
    
if __name__ == '__main__':
    sentiment = batch_get_accident_time()