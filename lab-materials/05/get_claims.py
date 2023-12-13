import os
import requests
import json

claims_endpoint = os.environ.get("CLAIMS_ENDPOINT")+"/db/claims"

def get_unprocessed_claims():
    claims_info = requests.get(claims_endpoint).json()
    
    unprocessed_list = []
    for claim in claims_info:
        if not claim["summary"]:
            unprocessed_list.append(claim["id"])
    print(f"Found unprocessed claims: {unprocessed_list}")
    return unprocessed_list

def get_claims(claim_ids=None):
    claim_ids = claim_ids or int(os.environ.get("claim_id"))
    
    if not claim_ids:
        claim_ids = get_unprocessed_claims()
    else:
        claim_ids = [claim_ids]
        
    with open('claims.json', 'w') as f:
        json.dump({
            "claim_ids": claim_ids,
        }, f)
    
    print(f"Will process claims: {claim_ids}")
    return claim_ids
        
if __name__ == '__main__':
    get_claims()