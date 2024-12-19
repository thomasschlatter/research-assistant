from tavily import TavilyClient
import os

tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=tavily_api_key)

def get_journal_format_requirements(journal_name):
    """
    Searches for and extracts formatting requirements for a specific journal
    """
    search_query = f"{journal_name} formatting requirements"
    search_results = client.search(
        query=search_query,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )
    return search_results['answer']

def get_journal_citation_requirements(journal_name):
    """
    Searches for and extracts citation and bibliography formatting requirements for a specific journal
    """
    search_query = f"{journal_name} citation and bibliography requirements"
    search_results = client.search(
        query=search_query,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )
    return search_results['answer']
    