
from openai import OpenAI
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

def review_proposal_feasibility(proposal, repositories=None, tools=None):
    """
    Reviews research proposal focusing on feasibility with available datasets
    Returns detailed feasibility analysis and dataset recommendations
    """
    system_prompt = """You are a data-focused research proposal reviewer specializing in feasibility analysis. 
    Your goal is to thoroughly evaluate if the proposed research can be executed with the available datasets and tools.

    """

    review_content = f"Review this research proposal's feasibility:\n\n{proposal}"
    if repositories:
        review_content += f"\n\nAvailable datasets and repositories:\n{repositories}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": review_content}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content