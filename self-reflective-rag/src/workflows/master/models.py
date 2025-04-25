from pydantic import BaseModel, Field

class InferenceOrRAG(BaseModel):
    """A binary score for the relevance check of retrieved documents"""
    
    binary_score: str = Field(
        description="The prompt requires a RAG, 'yes' or 'no'"
    )

    assistant_response: str = Field(
        description="The response provided if the binary_score is 'yes', i.e the prompt requires a RAG. If the binary_score is 'no', this containes the response 'None'."
    )