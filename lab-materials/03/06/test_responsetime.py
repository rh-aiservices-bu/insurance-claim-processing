import os
import requests
import json

max_response_time = 0.5

def send_request(endpoint):
    response = requests.get(endpoint)
    return response

def test_responsetime(endpoint):
    response = send_request(endpoint)

    if response.status_code==200:
        response_time = response.elapsed.total_seconds()
    else:
        raise Exception(f"Response status code is {response.status_code}")

    if response_time>max_response_time:
        raise Exception(f"Response took {response_time} which is greater than {max_response_time}")

    print(f"Response time was OK at {response_time} seconds")

    with open("responsetime_result.json", "w") as f:
        json.dump({
            "response_time": response_time
        }, f)

if __name__ == '__main__':
    health_endpoint = os.environ.get("LLM_ENDPOINT") + "/health"
    test_responsetime(health_endpoint)