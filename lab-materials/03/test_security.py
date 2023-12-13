import os
import requests
import json

def test_security(endpoint, expected_model_sha, expected_serving_sha):
    response = requests.get(endpoint)

    if response.status_code==200:
        response_json = response.json()
    else:
        raise Exception(f"Response status code is {response.status_code}")

    if response_json["model_sha"] != expected_model_sha:
        raise Exception(f"Model SHA has changed, model may have been tampered with")
    if response_json["sha"] != expected_serving_sha:
        raise Exception(f"Serving SHA has changed, endpoint may have been tampered with")

    print(f"Security check OK")

    with open("security_result.json", "w") as f:
        json.dump({
            "model_sha_match": response_json["model_sha"] == expected_model_sha,
            "serving_sha_match": response_json["sha"] == expected_serving_sha
        }, f)

if __name__ == '__main__':
    info_endpoint = os.environ.get("LLM_ENDPOINT") + "/info"
    expected_model_sha = os.environ.get("MODEL_SHA")
    expected_serving_sha = os.environ.get("SERVING_SHA")
    test_security(info_endpoint, expected_model_sha, expected_serving_sha)