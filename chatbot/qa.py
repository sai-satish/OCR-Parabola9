from transformers import pipeline
from pydantic import BaseModel

# Load the Question Answering pipeline
qa_pipeline = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad")

# Define the input model for the question and context (QA API)
class QARequest(BaseModel):
    question: str
    context: str

# Function to answer a question using the pipeline
def answer_question(request: QARequest):
    result = qa_pipeline(question=request.question, context=request.context)
    return {"answer": result['answer']}
