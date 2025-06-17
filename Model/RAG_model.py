import getpass
import os

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.5-flash-preview-04-17", model_provider="google_genai")

from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from retrivers import retrievers
from prompt_engg import category_prompts

def create_rag_chains(retrievers, prompts, llm):
    """
    Build RAG chains using Langchain Expression Language (LCEL)
    Structure: retriever → prompt → LLM → parser
    """
    rag_chains = {}
    
    for locality in retrievers.keys():
        locality_chains = {}
        
        for category, prompt_template in prompts.items():
            # Build LCEL chain: context retrieval + prompt + LLM + output parsing
            chain = (
                {
                    "context": retrievers[locality],  # Retrieves relevant chunks
                    "question": RunnablePassthrough()  # Passes query through unchanged
                }
                | prompt_template  # Formats context into prompt
                | llm  # Generates response
                | StrOutputParser()  # Extracts string output
            )
            
            locality_chains[category] = chain
        
        rag_chains[locality] = locality_chains
        print(f"Created {len(locality_chains)} RAG chains for {locality}")
    
    return rag_chains

# Create RAG chains for all localities and categories
rag_chains = create_rag_chains(retrievers, category_prompts, llm)

# Test a sample query
def test_rag_chain(rag_chains, locality, category, query):
    """Test RAG chain with sample query"""
    chain = rag_chains[locality][category]
    result = chain.invoke(query)
    return result

# Example test
sample_result = test_rag_chain(
    rag_chains, 
    list(rag_chains.keys())[0],  # First locality
    "community_social", 
    "What community activities happened recently? Make sure all the nitbit details are present."
)
print(f"Sample result: {sample_result}")
