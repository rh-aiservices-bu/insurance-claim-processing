import os

from langchain.llms import HuggingFaceTextGenInference
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.evaluation import load_evaluator
from langchain.embeddings import HuggingFaceEmbeddings

INFERENCE_SERVER_URL = "http://llm.ic-shared-llm.svc.cluster.local:3000"
MAX_NEW_TOKENS = 512
TOP_K = 10
TOP_P = 0.95
TYPICAL_P = 0.95
TEMPERATURE = 0.01
REPETITION_PENALTY = 1.03

def infer_with_template(input_text, template):
    llm = HuggingFaceTextGenInference(
        inference_server_url=INFERENCE_SERVER_URL,
        max_new_tokens=MAX_NEW_TOKENS,
        top_k=TOP_K,
        top_p=TOP_P,
        typical_p=TYPICAL_P,
        temperature=TEMPERATURE,
        repetition_penalty=REPETITION_PENALTY,
        streaming=True,
        verbose=False,
    )
    
    PROMPT = PromptTemplate.from_template(template)
    
    llm_chain = LLMChain(llm=llm, prompt=PROMPT)
    
    return llm_chain.run(input_text)
    
def similarity_metric(predicted_text, reference_text):
    embedding_model = HuggingFaceEmbeddings()
    evaluator = load_evaluator("embedding_distance", embeddings=embedding_model)
    distance_score = evaluator.evaluate_strings(prediction=predicted_text, reference=reference_text)
    return 1-distance_score["score"]
    
if __name__ == '__main__':
    with open('example_text.txt') as f:
        input_text = f.read()
    
    with open('template.txt') as f:
        template = f.read()
    
    infer_with_template(input_text, template)