
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_journal():
    """
    Generates journal recommendations based on the research field and content.
    Returns a recommended journal name.
    """
    system_prompt = """You are an expert academic publisher with extensive knowledge of scientific journals across disciplines.
    Your task is to recommend the most suitable journal for publication based on:
    1. Journal impact factor and reputation
    2. Scope alignment with the research
    3. Publication timeline
    4. Open access options
    5. Target audience reach
    
    Provide a single journal name that would be the best fit for this research.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Based on the research field of Linguistics and Sound Symbolism, recommend a highly suitable journal for publication. Return only the journal name without any explanation."}
        ],
        temperature=0.7,
        max_tokens=256
    )
    
    return response.choices[0].message.content.strip()
