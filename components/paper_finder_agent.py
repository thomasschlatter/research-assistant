from openai import OpenAI
from semanticscholar import SemanticScholar
import os
from ast import literal_eval

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)
sch = SemanticScholar()

def paper_finder_agent(proposal, papers_needed):
    """
    Generate an optimized search query from the research proposal using LLM
    and search Semantic Scholar
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": """You are a specialized research librarian and bibliographic expert in academic search optimization. Your task is to:
        1. Conduct comprehensive analysis of the research proposal's core concepts, methodology, and theoretical foundations
        2. Extract high-value one-word or two-word search terms including:
            - Primary research concepts and their variations
            - Domain-specific terminology and jargon
            - Methodological approaches and techniques
            - Theoretical frameworks and paradigms
            - Related sub-fields and intersecting domains
        3. Start with broad, foundational queries and gradually narrow down to more specific terms related to the research proposal. You can skip the most general ones.
        IMPORTANT: Return ONLY a list (5 itemns) of one-word or two-word search strings in the following format: ['term1', 'term2', ...]"""
         },
            {"role": "user", "content": f"Generate a list of search queries from this research proposal:\n\n{proposal}"}
        ],
        temperature=0.7,    )
    query_text = response.choices[0].message.content.strip()
    print("Searching Semantic Scholar with these queries: " + query_text)
    optimized_query_list = literal_eval(query_text)
    # Extract relevant data from papers
    extracted_papers = []
    for query in optimized_query_list:
        print("Query: " + query)
        papers = sch.search_paper(
            query, 
            limit=5, 
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        for i in range(0,len(papers)):
            paper_data = {
                'title': papers[i].title,
                'abstract': papers[i].abstract,
                'year': papers[i].year,
                'authors': [author.name for author in papers[i].authors] if papers[i].authors else [],
                'url': papers[i].url,
                'citation_count': papers[i].citationCount
            }
            extracted_papers.append(paper_data)

    return format_papers_to_markdown(extracted_papers)

def re_paper_finder_agent(draft):
    """
    Generate an optimized search query from the research draft using LLM
    and search Semantic Scholar
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a specialized research librarian and citation analyst expert in academic search optimization. Your task is to:
            1. Perform detailed analysis of the research paper draft to identify:
                - Gaps in papers already cited
                - Areas needing theoretical reinforcement
                - Sections requiring methodological validation
                - Potential counterarguments to address
            2. Generate strategic search one-word or two-word terms targeting:
                - Supporting evidence and validation studies
                - Contrasting viewpoints and critiques
                - Methodological precedents and innovations
                - Recent developments and future directions
            3. Start with broad, foundational queries and gradually narrow down to more specific terms related to the research paper draft. You can skip the most general ones.
            IMPORTANT: Return ONLY a list (5 items) of one-word or two-word search strings in the following format: ['term1', 'term2', ...]"""},
            {"role": "user", "content": f"Generate a list of  search queries from this research draft:\n\n{draft}"}
        ],
        temperature=0.7,
    )
    query_text = response.choices[0].message.content.strip()
    print("Searching Semantic Scholar with these queries: " + query_text)
    optimized_query_list = literal_eval(query_text)
    
    # Extract relevant data from papers
    extracted_papers = []
    for query in optimized_query_list:
        print("Query: " + query)
        papers = sch.search_paper(
            query, 
            limit=5, 
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        for i in range(0,len(papers)):
            paper_data = {
                'title': papers[i].title,
                'abstract': papers[i].abstract,
                'year': papers[i].year,
                'authors': [author.name for author in papers[i].authors] if papers[i].authors else [],
                'url': papers[i].url,
                'citation_count': papers[i].citationCount
            }
            extracted_papers.append(paper_data)

    return format_papers_to_markdown(extracted_papers)

def format_papers_to_markdown(papers):
    """
    Convert paper data into readable markdown citations
    """
    markdown_output = "# Related Research Papers\n\n"
    
    for paper in papers:
        # Format authors with proper concatenation
        authors = ""
        if paper['authors']:
            if len(paper['authors']) == 1:
                authors = paper['authors'][0]
            elif len(paper['authors']) == 2:
                authors = f"{paper['authors'][0]} and {paper['authors'][1]}"
            else:
                authors = f"{paper['authors'][0]} et al."
        
        # Build citation string
        citation = f"## {paper['title']}\n\n"
        citation += f"**Authors:** {authors}\n\n"
        citation += f"**Year:** {paper['year']}\n\n"
        citation += f"**Citations:** {paper['citation_count']}\n\n"
        citation += f"**Abstract:** {paper['abstract']}\n\n"
        citation += f"**Link:** [{paper['url']}]({paper['url']})\n\n"
        citation += "---\n\n"
        
        markdown_output += citation
    
    return markdown_output
