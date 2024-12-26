
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_journal(field, sub_field, title):
    """
    Generates journal recommendations based on the research field and content.
    Returns a recommended journal name.
    """
    system_prompt = """You are an expert academic publisher with extensive knowledge of scientific journals across disciplines.
    Your task is to recommend the most suitable journal for publication based on:
    1. Journal impact factor and reputation
    2. Scope alignment with the research
    3. Open access options
    4. Target audience reach
    
    Provide a single journal name that would be the best fit for this research.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Based on the research field {field}, specifically {sub_field}, recommend a highly suitable journal for this paper named {title}. Return only the journal name without any explanation."}
        ],
        temperature=0.7,
        max_tokens=256
    )
    
    return response.choices[0].message.content.strip()
