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
    4. Is highly specific and technically detailed
    5. Includes clear research objectives and methodology
    6. Uses ONLY publicly available datasets and published corpora
    7. Does NOT involve human subjects or new data collection
    8. Relies exclusively on existing online databases and research repositories
    
    Your proposal must explicitly state which public datasets will be used and confirm 
    that no human subject research is required."""

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

def refine_proposal_based_on_tools(proposal, specific_research_area, specific_research_sub_area, repositories, available_tools, relevant_papers, max_iterations):
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
    4. Is highly specific and technically detailed
    5. Includes clear research objectives and methodology
    6. Uses ONLY publicly available datasets and published corpora
    7. Does NOT involve human subjects or new data collection
    8. Relies exclusively on existing online databases and research repositories
    
    Your proposal must explicitly state which public datasets will be used and confirm 
    that no human subject research is required."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
             based on the following repositories: {repositories}
             ============================================
             and the following available tools: {available_tools}
             ============================================
             and the following relevant papers: {relevant_papers}
             ============================================
             Readjust the research paper proposal."""
             }
        ],
        temperature=0.7,
    )
    proposal = response.choices[0].message.content.strip()

    return proposal