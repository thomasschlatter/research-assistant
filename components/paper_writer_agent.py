from openai import OpenAI
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

def generate_section(proposal, specific_research_area, specific_research_sub_area, relevant_papers, available_tools, section_name, all_sections, max_iterations, previous_sections=None):
    """
    Generates and refines a cutting-edge research paper idea in a highly specific research area.
    """
    system_prompt = f"""You are a world-renowned expert researcher in {specific_research_area}, specifically {specific_research_sub_area}, with:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Write a comprehensive scientific paper section that advances the state-of-the-art research. Your writing will:
    
    Present a significant unsolved problem in {specific_research_area}, specifically {specific_research_sub_area}, 
    incorporating the latest developments from 1995-2024. The research must demonstrate high potential for academic 
    impact through novel contributions. Provide in-depth technical details and clearly articulated research 
    methodology.

    Requirements:
    1. Use proper academic writing style with formal language
    2. Include relevant citations
    3. Integrate analysis of publicly available datasets and published corpora
    4. Focus on computational/analytical methods using existing databases
    5. Avoid any reference to new data collection or human subject research
    6. Connect ideas logically with smooth transitions between paragraphs
    7. Support claims with references to peer-reviewed literature
    8. Maintain academic tone throughout the section

    IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication.
    IMPORTANT: Stick to the research objects of the proposal
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            This is the research proposal:
            {proposal}
            The paper has the following sections: {all_sections}.
            Here are some papers that can be used:
            
            {relevant_papers}

            IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication. Cite as many of the papers as you can.
            write ONLY the following section: {section_name}
            """
             }
        ],
        temperature=0.7,
        max_tokens=8192  # Adjust this to the maximum your model allows (e.g., 8192 for GPT-4o)
    )
    sec = response.choices[0].message.content.strip()

    return sec

def re_generate_section(field, sub_field, section_name, section_content, results_section, relevant_papers, max_iterations):
    """
    Regenerates paper sections incorporating the results context.
    """
    system_prompt = f"""You are a world-renowned expert researcher in {field}, specifically {sub_field}, with:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Rewrite the {section_name} section of this scientific paper to align with and reference the results section. Your writing will:
    
    1. Use proper academic writing style with formal language
    2. Include relevant citations 
    3. Connect ideas logically with smooth transitions
    4. Support claims with references to literature
    5. Maintain academic tone throughout
    6. Ensure the narrative flows naturally to the results section
    7. Add forward references to key findings where appropriate

    IMPORTANT: Maintain consistency with the findings presented in the results, remove any information that is not covered by the results.
    For example, if the results section does not make use of machine learning models, do not include any references to machine learning models.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Here are the results of our study:
            {results_section}

            =========================

            This is the {section_name} section we want to rewrite:
            {section_content}

            =========================

            Rewrite the {section_name} section to naturally lead into these results while maintaining academic writing standards.
            Focus on creating a cohesive narrative that anticipates the findings.

            Here are some papers that can be used:
            
            {relevant_papers}
            """
            }
        ],
        temperature=0.7,
        max_tokens=8192
    )
    
    return response.choices[0].message.content.strip()

def generate_discussion_section(whole_paper_integrated):
    """
    Generates the discussion section based on the integrated paper content.
    """
    system_prompt = """You are a scientific writing expert tasked with creating a discussion section that:
    1. Interprets the results in context of existing literature
    2. Acknowledges limitations of the study
    3. Suggests future research directions
    4. Highlights theoretical and practical implications
    5. Maintains academic writing standards
    
    Write a comprehensive discussion section that:
    - Connects findings back to the research questions/hypotheses
    - Compares results with previous studies
    - Explains unexpected findings
    - Provides theoretical explanations for the results
    - Uses proper academic tone and style
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Here is the integrated paper content:
            {whole_paper_integrated}

            Generate a discussion section that thoroughly interprets the results and places them in the broader context 
            of the field. Ensure all major findings are discussed and connected to existing literature.
            """
            }
        ],
        temperature=0.7,
        max_tokens=8192
    )
    
    return response.choices[0].message.content.strip()

def generate_conclusion_section(whole_paper_integrated):
    """
    Generates the conclusion section based on the integrated paper content.
    """
    system_prompt = """You are a scientific writing expert tasked with creating a conclusion section that:
    1. Summarizes the key findings and contributions
    2. Reinforces the significance of the research
    3. Provides clear takeaway messages
    4. Ends with impactful closing remarks
    5. Maintains academic writing standards
    
    Write a concise conclusion section that:
    - Restates the main research objectives
    - Synthesizes the major findings
    - Emphasizes the broader implications
    - Uses proper academic tone and style
    - Avoids introducing new information
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Here is the integrated paper content:
            {whole_paper_integrated}

            Generate a conclusion section that effectively wraps up the research and reinforces its significance.
            Keep it concise but impactful, focusing on the key takeaways and broader implications.
            """
            }
        ],
        temperature=0.7,
        max_tokens=8192
    )
    
    return response.choices[0].message.content.strip()

def generate_title(whole_paper_integrated):
    """
    Generates an academic paper title based on the complete paper content.
    """
    system_prompt = """You are a scientific writing expert tasked with creating a compelling academic paper title that:
    1. Accurately reflects the paper's content and findings
    2. Is concise yet informative
    3. Uses appropriate academic terminology
    4. Captures reader interest
    5. Follows standard academic title conventions
    
    Create a title that:
    - Clearly indicates the main focus of the research
    - Includes key variables or concepts
    - Avoids unnecessary words and jargon
    - Is under 20 words
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Here is the complete paper content:
            {whole_paper_integrated}

            Generate a clear, compelling title that effectively represents this research paper.
            """
            }
        ],
        temperature=0.7,
        max_tokens=256
    )
    
    return response.choices[0].message.content.strip()

def generate_final_paper(title, content, journal_name, format_requirements, citation_requirements):
    """
    Generates the final paper following journal-specific formatting requirements.
    """
    system_prompt = f"""You are an expert academic paper formatter with deep knowledge of academic publishing standards.
    Format this paper according to the following journal requirements:
    
    {format_requirements}
    
    Add Bibliography according to the following journal requirements:
    
    {citation_requirements}

    Apply these formatting rules while maintaining:
    1. Proper section organization
    2. Citation style specified by the journal
    3. Figure and table placement
    4. Title page formatting
    5. Abstract formatting
    6. Keywords if required
    7. Word count limits
    8. Any journal-specific sections or elements
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Title: {title}
            
            Paper Content:
            {content}
            
            Please format this paper according to {journal_name}'s requirements while preserving all content and academic integrity.
            """
            }
        ],
        temperature=0.7,
        max_tokens=8192
    )
    
    return response.choices[0].message.content.strip()
