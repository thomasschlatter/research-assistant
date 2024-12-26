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

def paper_finder_agent(field, sub_field, number_of_papers):
    """
    Generate an optimized search query from the research field using LLM
    and search Semantic Scholar
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": """You are a specialized research librarian and bibliographic expert in academic search optimization. Your task is to:
        1. Conduct comprehensive analysis of the research field's core concepts, methodology, and theoretical foundations
        2. Extract high-value one-word or two-word search terms including:
            - Primary research concepts and their variations
            - Domain-specific terminology and jargon
            - Methodological approaches and techniques
            - Theoretical frameworks and paradigms
            - Related sub-fields and intersecting domains
        DO NOT include names of databases, repositories, or data sources in the search terms.
        3. Start with broad, foundational queries and gradually narrow down to more specific terms related to the research field. You can skip the most general ones.
        IMPORTANT: Return ONLY a list (5 itemns) of one-word or two-word search strings in the following format: ['term1', 'term2', ...]"""
         },
            {"role": "user", "content": f"Generate a list of search queries for this research area:\n\n{field} {sub_field}"}
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
            limit=number_of_papers, 
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        for i in range(0,len(papers)):
            paper_data = {
                'title': papers[i].title,
                'abstract': papers[i].abstract,
                'year': papers[i].year,
                'authors': [author.name for author in papers[i].authors] if papers[i].authors else [],
                #'url': papers[i].url,
                'citation_count': papers[i].citationCount
            }
            extracted_papers.append(paper_data)

    return format_papers_to_bib(extracted_papers)

def re_paper_finder_agent(draft, number_of_papers):
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
            limit=number_of_papers, 
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        for i in range(0,len(papers)):
            paper_data = {
                'title': papers[i].title,
                'abstract': papers[i].abstract,
                'year': papers[i].year,
                'authors': [author.name for author in papers[i].authors] if papers[i].authors else [],
                #'url': papers[i].url,
                'citation_count': papers[i].citationCount
            }
            extracted_papers.append(paper_data)

    return format_papers_to_bib(extracted_papers)

def format_papers_to_bib(papers):
    """
    Convert paper data into BibTeX citations, excluding papers with empty abstracts
    """
    bib_output = ""
    
    for paper in papers:
        # Skip papers with empty/None abstracts
        if not paper['abstract']:
            continue
            
        # Create citation key from first author's lastname and year
        first_author = paper['authors'][0].split()[-1] if paper['authors'] else 'Unknown'
        citation_key = f"{first_author.lower()}{paper['year']}"
        
        # Format authors for BibTeX
        authors = " and ".join(paper['authors']) if paper['authors'] else "Unknown"
        
        # Build BibTeX entry
        bib_entry = f"@article{{{citation_key},\n"
        bib_entry += f"  title = {{{paper['title']}}},\n"
        bib_entry += f"  author = {{{authors}}},\n"
        bib_entry += f"  year = {{{paper['year']}}},\n"
        bib_entry += f"  abstract = {{{paper['abstract']}}},\n"
        #bib_entry += f"  url = {{{paper['url']}}},\n"
        bib_entry += f"  citations = {{{paper['citation_count']}}}\n"
        bib_entry += "}\n\n"
        
        bib_output += bib_entry
    
    return bib_output