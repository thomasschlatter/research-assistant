from tavily import TavilyClient
import os

# Retrieve the API key from the environment variable
api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise EnvironmentError("TAVILY_API_KEY environment variable is not set.")


# Initialize the Tavily client
tavily = TavilyClient(api_key)

def search_web_for_databases(query, data_types=None):
  """
  Searches the web using Tavily for downloadable databases and corpuses.

  Args:
    query: The search query describing the desired database or corpus.
    data_types: (Optional) A list of data types to filter for 
                 (e.g., ["CSV", "JSON", "SQL", "TXT"]).

  Returns:
    A list of search results.
  """
  try:
    # Construct the search query with explicit instructions
    search_query = f"{query} (downloadable OR dataset OR corpus)"
    if data_types:
      search_query += f" ({' OR '.join(data_types)})"

    response = tavily.search(search_query)
    print(response)
    # Process the response and extract relevant information
    results = []
    for result in response['results']:
      results.append({
          "title": result['title'],
          "url": result['url'],
      })
    return results
  except Exception as e:
    print(f"An error occurred: {e}")
    return None

if __name__ == "__main__":
  query = input("Enter your search query for a database or corpus: ")
  # Example usage with data type filtering:
  data_types = ["CSV", "JSON"]  
  search_results = search_web_for_databases(query, data_types)
  
  if search_results:
    for result in search_results:
      print("-" * 20)
      print(f"Title: {result['title']}")
      print(f"Snippet: {result['snippet']}")
      print(f"URL: {result['url']}")