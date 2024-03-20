from llm_usage import infer_with_template, similarity_metric
import json


def test_response_quality():
    with open('example_text.txt') as f:
        input_text = f.read()
        
    with open('summary_template.txt') as f:
        template = f.read()

    expected_response = """On October 15, 2023, at around 2:30 PM, John Smith was involved in a car accident at the intersection of Elm Street and Maple Avenue in Springfield, Illinois (coordinates: 39.7476° N, 89.6960° W). He was driving his Honda Accord with a green light when a Ford Escape, which ran a red light, collided with the front passenger side of his vehicle. The accident occurred in overcast weather with light rain, and the road was wet. No serious injuries were reported, but both vehicles sustained significant damage. A police report was filed, and the officer's badge number is 12345. Witnesses to the accident include Sarah Johnson, Mark Williams, and Lisa Anderson, and their contact information has been provided. Photos of the accident scene, including the damage to both vehicles, traffic signals, and road conditions, have also been taken. John is requesting that a claim be initiated under his policy (ABC12345) for the damages to his vehicle and is asking for guidance on the claim process and required documentation."""

    response = infer_with_template(input_text, template)
    print(f"Response: {response}")
    
    similarity = similarity_metric(response, expected_response)
    print(similarity)

    if similarity <= 0.8:
        raise Exception("Output is not similar enough to expected output")
        
    print("Response Quality OK")

    with open("quality_result.json", "w") as f:
        json.dump({
            "quality_test_response": response,
            "quality_test_similarity": similarity
        }, f)

if __name__ == '__main__':
    test_response_quality()