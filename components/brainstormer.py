from openai import OpenAI
from semanticscholar import SemanticScholar
import json
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)
sch = SemanticScholar()


def query_semantic_scholar_with_llm(proposal):
    """
    Generate an optimized search query from the research proposal using LLM
    and search Semantic Scholar
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a research expert. Extract the most relevant search terms from the research proposal to create an optimal query for finding related papers."},
            {"role": "user", "content": f"Generate a focused search query (max 3-4 key terms) from this research proposal:\n\n{proposal}"}
        ],
        temperature=0.7,
    )
    
    optimized_query = response.choices[0].message.content.strip()
    papers = sch.search_paper(
        optimized_query, 
        limit=5, 
        fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
    )
    return {'query': optimized_query, 'data': papers}
def generate_research_paper_idea(specific_research_area, specific_research_sub_area, num_iterations=3):
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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate a cutting-edge research paper proposal with specific technical details, methodology, and expected contributions to the field."}
        ],
        temperature=0.7,
    )
    proposal = response.choices[0].message.content.strip()

    while True:
        print("\nCurrent proposal:\n")
        print("-" * 50)
        print(proposal)
        print("-" * 50)
        print("\nOptions:")
        print("1) Refine proposal")
        print("2) Consult Semantic Scholar")
        print("3) Exit")
    
        choice = input("\nEnter your choice (1-3): ")
    
        if choice == "1":
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
                    Enhance the following research proposal with more technical depth:
                
                    Current Proposal: {proposal}
                
                    Ensure the refinement maintains scientific rigor and includes:
                    - Specific technical methodology
                    - Current state-of-the-art references
                    - Clear research contributions
                    """}
                ],
                temperature=0.7,
            )
            proposal = response.choices[0].message.content.strip()
        
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
                response = client.chat.completions.create(
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
                
        elif choice == "3":
            break
        
    return proposal

if __name__ == "__main__":
    print("Enter a highly specific research area")
    print("Example: 'quantum error correction in topological quantum computing'")
    specific_area = input("Research area: ")
    specific_sub_area = input("Research sub-area: ")
    refined_proposal = generate_research_paper_idea(specific_area, specific_sub_area)
    print("\nFinal Research Paper Proposal:")
    print("-" * 50)
    print(refined_proposal)