import json

def summarize_results():
    results = {}
    with open('responsetime_result.json') as f1, open("security_result.json") as f2, open("quality_result.json") as f3:
        results.update(json.load(f1))
        results.update(json.load(f2))
        results.update(json.load(f3))

    print(results)
    
    with open("results.json", "w") as f:
        json.dump(results, f)

if __name__ == '__main__':
    summarize_results()