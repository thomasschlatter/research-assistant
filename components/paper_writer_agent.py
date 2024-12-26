from openai import OpenAI
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

def generate_section(proposal, specific_research_area, specific_research_sub_area, relevant_papers, available_tools, section_name, all_sections, previous_sections=None):
    """
    Generates and refines a cutting-edge research paper idea in a highly specific research area.
    Returns tuple of (section_content, success_status)
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
    2. Include relevant in-text citations
    3. Integrate analysis of publicly available datasets and published corpora
    4. Focus on computational/analytical methods using existing databases
    5. Avoid any reference to new data collection or human subject research
    6. Connect ideas logically with smooth transitions between paragraphs
    7. Maintain academic tone throughout the section

    IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication.
    IMPORTANT: Stick to the research objects of the proposal
    IMPORTANT: If other papers are cited, strictly base the content on the abstract provided.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                This is the research proposal:
                {proposal}
                The paper has the following sections: {all_sections}.
                Here are some papers that can be used:
                
                {relevant_papers}

                IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication. Cite as many of the papers as you can.
                write ONLY the following section: {section_name}
                """}
            ],
            temperature=0.7,
            max_tokens=8192
        )
        section_content = response.choices[0].message.content.strip()
        return section_content, True
    except Exception as e:
        print(f"Error generating section: {str(e)}")
        return "", False

def re_generate_section(field, sub_field, section_name, section_content, results_section, relevant_papers):
    """
    Regenerates paper sections incorporating the results context.
    """
    system_prompt = f"""You are a world-renowned expert researcher in {field}, specifically {sub_field}, with:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Rewrite the {section_name} section of this scientific paper to align with and reference the results section. Your writing will:
    
    1. Use proper academic writing style with formal language
    2. Include relevant in-text citations 
    3. Connect ideas logically with smooth transitions
    4. Maintain academic tone throughout
    5. Ensure the narrative flows naturally to the results section
    6. Add forward references to key findings where appropriate

    IMPORTANT: Maintain consistency with the findings presented in the results, remove any information that is not covered by the results.
    For example, if the results section does not make use of machine learning models, do not include any references to machine learning models.
    IMPORTANT: If other papers are cited, strictly base the content on the abstract provided.
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
 
def generate_final_paper(title, author_names, content, relevant_papers, journal_name, format_requirements, citation_requirements, absolute_path):
    """
    Generates the final paper following journal-specific formatting requirements.
    """
    author_markdown_string = "\n".join([f'- "{author}"' for author in author_names])
    system_prompt = f"""You are an expert academic paper formatter with deep knowledge of academic publishing standards, LaTeX, and Markdown formatting. Your task is to format this research paper following these key requirements:

1. Structure and Formatting:
- Use clear section headings with proper Markdown hierarchy (# for title, ## for main sections, ### for subsections)
- Format equations using LaTeX syntax within Markdown
- Create properly formatted tables using Markdown syntax
- Include figure references using the specified absolute path format
- Ensure consistent paragraph spacing and indentation
- Maintain proper academic writing style and tone throughout

2. Citations and References:
- Use [@key] format for in-text citations
- Place citations before punctuation marks [@key1; @key2]
- For multiple citations, separate keys with semicolons
- Ensure every claim is properly supported with relevant citations
- You DO NOT NEED to include a bibliography section, the citation keys are sufficient
- End the markdown text with "# Bibliography" for the bibliography section, the actual bibliography will be generated with pandoc

3. Content Organization:
- Begin with a clear, informative abstract
- Organize content into logical sections with smooth transitions
- Use appropriate academic language and terminology
- Maintain consistent formatting across all sections
- Include all necessary components (title, abstract, keywords, main sections, in-text-references)

4. Technical Elements:
- Format code snippets and technical terms appropriately
- Use consistent notation for mathematical expressions
- Include properly labeled and referenced figures/tables
- Ensure all cross-references are correctly formatted

5. Images:
- Make sure that the images point to {absolute_path}\\tmp\\analysis\\plots\\[IMAGE_NAME]

6. Title, Author, Date and Abstract:
- Put the following information in the YAML front matter:
---
title: {title}
{author_markdown_string}
date
abstract |
output: pdf_document
---

IMPORTANT: Be wordy!

Your output should be a complete, well-structured academic paper in Markdown format that meets high academic publishing standards while maintaining readability and professional appearance."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            Title: {title}
            
            Paper Content:
            {content}

            ============================================

            Cite papers using citation key of the following references:
            {relevant_papers}
            """
            }
        ],
        temperature=0.7,
        max_tokens=8192
    )
    
    pp = remove_markdown_formatting(response.choices[0].message.content.strip())
    pp = remove_yaml_formatting(pp)
    return pp

def clear_relevant_papers():
    """Clears the relevant papers file at startup"""
    papers_path = "tmp/proposals/relevant_papers.md"
    with open(papers_path, 'w') as f:
        f.write("")

# remove ```markdown ... ``` from the generated paper if present
def remove_markdown_formatting(paper):
    if paper.startswith("```markdown"):
        paper = paper[len("```markdown"):]  # remove the initial markdown tag
    if paper.endswith("```"):
        paper = paper[:-len("```")]  # remove the final markdown tag    
    return paper

def remove_yaml_formatting(paper):
    """
    Removes only the triple backticks and 'yaml' marker from the input text.
    
    Args:
        text (str): Input text with YAML markers.
        
    Returns:
        str: Text without the YAML markers.
    """
    # Remove ```yaml and ```
    cleaned_text = paper.replace("```yaml", "").replace("```", "")
    return cleaned_text.strip()