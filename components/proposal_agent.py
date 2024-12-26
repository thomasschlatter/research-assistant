from openai import OpenAI
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

def generate_research_proposal(specific_research_area, specific_research_sub_area, max_iterations=3):
    """
    Generates and refines a cutting-edge research paper idea in a highly specific research area.
    """
    system_prompt = f"""You are a world-renowned expert researcher in {specific_research_area}, specifically {specific_research_sub_area}, with:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Generate a state-of-the-art research paper idea that:
    1. Addresses a significant unsolved problem in {specific_research_area}, specifically {specific_research_sub_area}
    2. Builds upon the most recent developments (2023-2024)
    3. Has potential for high academic impact
    4. Includes clear research objectives and methodology
    5. Uses ONLY one of the mentioned datasets and repositories
    6. Does NOT involve human subjects or new data collection
    7. Relies exclusively on existing online databases and research repositories
    
    Your proposal must explicitly state which of the mentioned datasets will be used.
    
    IMPORTANT: The research can only be based on the repositories and datasets mentioned in the prompt.
    IMPORTANT: Keep the research simple!"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate a cutting-edge research paper proposal with specific technical details, methodology, and expected contributions to the field."}
        ],
        temperature=0.7,
    )
    proposal = response.choices[0].message.content.strip()

    return proposal

def refine_proposal_based_on_tools(current_proposal, field, sub_field, repositories, available_tools, relevant_papers, previous_review=None):
    # Add previous review feedback to the prompt
    review_context = ""
    if previous_review:
        review_context = f"\nPrevious review feedback:\n{previous_review}\n\nAddress all issues raised in the previous review."
    
    system_prompt = f"""Refine the research proposal based on available tools, repositories, and previous feedback. If the proposal is too complicated, simplify it.
    Field: {field}
    Sub-field: {sub_field}
    {review_context}"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
             Current proposal: {current_proposal}
             ============================================
             And the following available tools: {available_tools}
             ============================================   
             Based on the following repositories: {repositories}          
             ============================================
             Refine the research paper proposal, addressing any previous feedback if provided."""
             }
        ],
        temperature=0.7,
    )
    proposal = response.choices[0].message.content.strip()

    return proposal