from llm_usage import infer_with_template, similarity_metric
import json


def test_response_quality():
    with open('example_text.txt') as f:
        input_text = f.read()
        
    with open('summary_template.txt') as f:
        template = f.read()

    expected_response = """A car insurance claim has been initiated by John Smith for a recent accident involving his Honda Accord and a Ford Escape. The accident occurred on October 15, 2023, at approximately 2:30 PM, at the intersection of Elm Street and Maple Avenue, near Smith Park, in Springfield, Illinois. The other party ran a red light and collided with the front passenger side of John's vehicle, causing significant damage to both vehicles. John sustained no serious injuries, but there were witnesses to the accident, and he has photos of the scene and the other party's insurance information. He is requesting that the insurance company initiate a claim under his policy for the damages to his vehicle and has provided the necessary documentation and information."""

    response = infer_with_template(input_text, template)
    print(f"Response: {response}")
    
    similarity = similarity_metric(response, expected_response)
    print(similarity)

    if similarity <= 0.9:
        raise Exception("Output is not similar enough to expected output")
        
    print("Response Quality OK")

    with open("quality_result.json", "w") as f:
        json.dump({
            "quality_test_response": response,
            "quality_test_similarity": similarity
        }, f)

if __name__ == '__main__':
    test_response_quality()