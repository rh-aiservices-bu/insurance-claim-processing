import requests
import os
import json

from llm_usage import infer_with_template

claims_endpoint = os.environ.get("CLAIMS_ENDPOINT")+"/db/claims"

def upload_sentiment(claim_id, sentiment):
    upload_endpoint = claims_endpoint + f"/{claim_id}/sentiment"
    data = {
        "sentiment": sentiment,
    }
    headers = {'accept': 'application/json'}
    response = requests.post(upload_endpoint, headers=headers, params=data)

    if response.status_code!=200:
        raise Exception(f"{response.status_code} {response.text}")
    

def get_claim_sentiment(claim_id = None):    
    claim_endpoint = claims_endpoint + f"/{claim_id}"
    claim_info = requests.get(claim_endpoint).json()
    claim_body = claim_info["body"]
    
    with open('templates/sentiment_template.txt') as f:
        template = f.read()
    
    sentiment = infer_with_template(claim_body, template)
    print(sentiment)
    upload_sentiment(claim_id, sentiment)
    
    
def batch_get_claim_sentiment(claim_ids = None):
    if not claim_ids:
        with open('claims.json') as f:
            claim_ids = json.load(f)["claim_ids"]
                
    print(f"processing claims: {claim_ids}")
    
    for claim_id in claim_ids:
        get_claim_sentiment(claim_id)
    
if __name__ == '__main__':
    sentiment = batch_get_claim_sentiment()