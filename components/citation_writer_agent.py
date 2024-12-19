from openai import OpenAI
from semanticscholar import SemanticScholar
import os

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)
sch = SemanticScholar()

def paper_finder_agent(proposal, papers_needed=20):
    """
    Citation writer agent that searches terms sequentially from general to specific
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a citation writing expert for scientific papers."},
            {"role": "user", "content": f"Generate a focused search query (max 3-4 key terms) from this research proposal:\n\n{proposal}\n\nCreate a machine-readable list and start with more general terms and become more and more specific towards the end of the list."}
        ],
        temperature=0.7,
    )
    
    search_terms = response.choices[0].message.content.strip().replace("\"","").split('\n')
    
    all_papers = []
    
    for term in search_terms:
        print("Looking up " + term)
        if len(all_papers) >= papers_needed:
            break
            
        print(f"Searching Semantic Scholar with term: {term}")
        papers = sch.search_paper(
            term, 
            limit=papers_needed - len(all_papers),
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        
        # Extract relevant data from papers
        for paper in papers:
            if len(all_papers) >= papers_needed:
                break
                
            paper_data = {
                'title': paper.title,
                'abstract': paper.abstract,
                'year': paper.year,
                'authors': [author.name for author in paper.authors] if paper.authors else [],
                'url': paper.url,
                'citation_count': paper.citationCount
            }
            
            # Check if paper is already in our collection to avoid duplicates
            if not any(existing['title'] == paper_data['title'] for existing in all_papers):
                all_papers.append(paper_data)
    
    return all_papers