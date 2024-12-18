from openai import OpenAI
from langchain_ollama import OllamaLLM
from semanticscholar import SemanticScholar
import json
import os
import datetime
import pathlib
import json
from components.data_curator import get_kaggle, search_datasets, save_dataset_info, download_dataset, curate_data

import re

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable not set!")

# Initialize clients
openai_client = OpenAI(api_key=openai_api_key)
sch = SemanticScholar()

try:
    ollama_client = OllamaLLM(model="llama3.1")
except Exception as e:
    print(f"Failed to initialize Ollama client: {e}")
    ollama_client = None


def query_semantic_scholar_with_llm(proposal, model="ollama"):
    """
    Generate an optimized search query from the research proposal using LLM
    and search Semantic Scholar. Supports both OpenAI and Ollama.
    """
    system_prompt = "You are a research expert. Extract the most relevant search terms from the research proposal to create an optimal query for finding related papers. Do not include the original research proposal in the query. Think about what data you would want to find to support the research."
    user_prompt = f"Generate a focused search query (max 3-4 key terms) from this research proposal:\n\n{proposal}. Put the search query in <query> </query> tags."

    if model == "ollama" and ollama_client:
        response = ollama_client.invoke(
            f"{system_prompt}\n\n{user_prompt}"
        )
        query_text = response.strip()
    else:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        query_text = response.choices[0].message.content.strip()
    
    optimized_query = re.search(r'<query>(.*?)</query>', query_text).group(1)
    
    papers = sch.search_paper(
        optimized_query, 
        limit=5, 
        fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
    )
    return {'query': optimized_query, 'data': papers}


def generate_research_paper_idea(specific_research_area, specific_research_sub_area, model="ollama", num_iterations=3, initial_proposal = None):
    """

    Generates and refines a cutting-edge research paper idea using either OpenAI or Ollama
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
    7. Relies exclusively on ONE of the following public datasets:
        - Kaggle
    8. Does NOT involve human subjects or new data collection
    
    Your proposal must explicitly state which public dataset will be used and confirm 
    that no human subject research is required."""

    if initial_proposal:
            proposal = initial_proposal
    else:
        if model == "ollama" and ollama_client:
            response = ollama_client.invoke(system_prompt)
            proposal = response.strip()
        else:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate a cutting-edge research paper proposal with specific technical details, methodology, and expected contributions to the field."}
                ],
                temperature=0.7,
            )
            proposal = response.choices[0].message.content.strip()
            
        save_proposal_version(proposal, specific_research_area, specific_research_sub_area, "scholar_refinement", model=model)
        
    while True:
        print("\nCurrent proposal:\n")
        print("-" * 50)
        print(proposal)
        print("-" * 50)
        print("\nOptions:")
        print("1) Refine proposal")
        print("2) Consult Semantic Scholar")
        print("3) Retrieve Necessary Datasets")
        print("4) Exit")
        print("5) Switch Model (OpenAI/Ollama)")
    
        choice = input("\nEnter your choice (1-5): ")
    
        if choice == "1":
            refinement = input("Enter specific technical aspects to refine: ")
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
                    Enhance the following research proposal with more technical depth:
                
                    Current Proposal: {proposal}
                    Focus on: {refinement}
                
                    Ensure the refinement maintains scientific rigor and includes:
                    - Specific technical methodology
                    - Current state-of-the-art references
                    - Clear research contributions
                    """}
                ],
                temperature=0.7,
            )
            proposal = response.choices[0].message.content.strip()
            # Save refinement version
            save_proposal_version(proposal, specific_research_area, specific_research_sub_area, "refinement")
                    
        elif choice == "2":
            print("\nGenerating optimal search query and searching Semantic Scholar...")
            results = query_semantic_scholar_with_llm(proposal)
            
            print(f"\nUsing search query: {results['query']}")
            if results['data']:
                print("\nRelevant papers found:")
                for i, paper in enumerate(results['data'], 1):
                    print(f"\n{i}. {paper.title}")
                    print(f"Year: {paper.year}")
                    print(f"Citations: {paper.citationCount}")
                    if paper.abstract:
                        print(f"Abstract: {paper.abstract[:200]}...")
                    print(f"URL: {paper.url}")

                    if i >= 30:
                        break
            
            refine_input = input("\nWould you like to refine the proposal based on these papers? (y/n): ")
            if refine_input.lower() == 'y':
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"""
                        Enhance the following research proposal considering these recent papers:
                        {json.dumps([{
                            'title': p.title,
                            'abstract': p.abstract,
                            'year': p.year
                        } for p in results['data'][:3]], indent=2)}
                        
                        Current Proposal: {proposal}
                        
                        Ensure to incorporate:
                        - Latest findings from these papers
                        - Any identified research gaps
                        - Potential improvements to methodology
                        """}
                    ],
                    temperature=0.7,
                )
                proposal = response.choices[0].message.content.strip()
                # Save scholar-based version
                save_proposal_version(proposal, specific_research_area, specific_research_sub_area, "scholar_refinement")

        elif choice == "3":
            # Generate dataset search query using LLM
            kaggle_dict = get_kaggle(model=model, proposal=proposal, specific_research_area=specific_research_area, specific_research_sub_area=specific_research_sub_area)

            print(kaggle_dict)

            # Ask if user wants to refine proposal based on available datasets
            refine_input = input("\nWould you like to refine the proposal based on these datasets? (y/n): ")
            if refine_input.lower() == 'y':
                if model == "ollama" and ollama_client:
                    proposal = ollama_client.invoke(
                        "You are a research expert. Refine the research proposal to specifically utilize the available datasets while maintaining the original research objectives.\n\n" +
                        f"Enhance the following research proposal considering these available datasets:\n{json.dumps(kaggle_dict, indent=2)}\n\n" +
                        f"Current Proposal: {proposal}\n\n" +
                        "Ensure to:\n- Specify how each dataset will be used\n- Adjust methodology to match available data\n- Maintain research objectives while leveraging these datasets"
                    ).strip()
                else:
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a research expert. Refine the research proposal to specifically utilize the available datasets while maintaining the original research objectives."},
                            {"role": "user", "content": f"""
                            Enhance the following research proposal considering these available datasets:
                            {json.dumps(kaggle_dict, indent=2)}
                        
                            Current Proposal: {proposal}
                        
                            Ensure to:
                            - Specify how each dataset will be used
                            - Adjust methodology to match available data
                            - Maintain research objectives while leveraging these datasets
                            """}
                        ],
                        temperature=0.7,
                    )
                    proposal = response.choices[0].message.content.strip()
                # Save dataset-based refinement version
                save_proposal_version(proposal, specific_research_area, specific_research_sub_area, "dataset_refinement", model=model)

        elif choice == "4":
            break
        
        elif choice == "5":
            model = "ollama" if model == "ollama" else "openai"
            print(f"Switched to {model} model")
        
    return proposal



# Add this function to handle saving proposals
def save_proposal_version(proposal, specific_area, specific_sub_area, iteration_type, model="ollama"):
    # Create research_proposals directory if it doesn't exist
    base_dir = pathlib.Path("research_proposals")
    base_dir.mkdir(exist_ok=True)
    
    # Create a sanitized directory name from research area
    dir_name = f"{specific_area}_{specific_sub_area}".replace(" ", "_").lower()
    proposal_dir = base_dir / dir_name
    proposal_dir.mkdir(exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save proposal version
    proposal_data = {
        "timestamp": timestamp,
        "research_area": specific_area,
        "research_sub_area": specific_sub_area,
        "iteration_type": iteration_type,
        "proposal": proposal
    }
    
    # Save as JSON
    proposal_file = proposal_dir / f"proposal_{timestamp}.json"
    with open(proposal_file, "w") as f:
        json.dump(proposal_data, f, indent=2)
    
    # Generate write-up
    write_up = generate_writeup(proposal, model)
    writeup_file = proposal_dir / f"writeup_{timestamp}.md"
    with open(writeup_file, "w") as f:
        f.write(write_up)
    
    return proposal_file, writeup_file

def generate_writeup(proposal, model="ollama"):
    """Generate a structured write-up based on the proposal"""
    system_prompt = "You are a research paper writer. Create a structured write-up from the research proposal with sections: Introduction, Objectives, Methodology, Expected Outcomes, and Potential Impact."
    
    if model == "ollama" and ollama_client:
        response = ollama_client.invoke(
            f"{system_prompt}\n\nProposal:\n{proposal}"
        )
        return response.strip()
    else:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a detailed write-up for:\n\nProposal:\n{proposal}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()




