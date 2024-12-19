from openai import OpenAI
import os
import requests
from ast import literal_eval

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
osf_api_token = os.getenv("OSF_API_TOKEN")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")
if not osf_api_token:
    raise ValueError("OSF_API_TOKEN environment variable not set!")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

def repository_finder_agent(proposal, repos_needed):
    """
    Generate an optimized search query from the research proposal using LLM
    and search OSF repositories
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a research expert. Extract the most relevant search terms from the research proposal to create an optimal query for finding related repositories. Create a machine readable list ['',''] and start with the most general terms and move on to more specific terms"},
            {"role": "user", "content": f"Generate a focused search query (max 3-4 key terms) from this research proposal:\n\n{proposal}"}
        ],
        temperature=0.7,
    )
    query_text = response.choices[0].message.content.strip()
    print("Searching OSF with these queries: " + query_text)
    optimized_query_list = literal_eval(query_text)

    # Extract relevant data from repositories
    extracted_repos = []
    headers = {
        "Authorization": f"Bearer {osf_api_token}"
    }
    BASE_URL = "https://api.osf.io/v2/"

    for query in optimized_query_list:
        print("Query: " + query)
        response = requests.get(
            f"{BASE_URL}nodes/?filter[title][icontains]={query}", 
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            for project in data.get('data', []):
                repo_data = {
                    'title': project['attributes']['title'],
                    'description': project['attributes']['description'],
                    'date_created': project['attributes']['date_created'],
                    'date_modified': project['attributes']['date_modified'],
                    'public': project['attributes']['public'],
                    'url': project['links']['html'],
                    'id': project['id']
                }
                extracted_repos.append(repo_data)

    # Retrieve file metadata for each repository
    for repo in extracted_repos:
        repo['files'] = retrieve_files_metadata(repo['id'], headers)

    return format_repos_to_markdown(extracted_repos)

def retrieve_files_metadata(repo_id, headers):
    """
    Retrieve the list of files and their metadata for a given repository.
    Only include files with extensions hinting at quantitative study results.
    """
    BASE_URL = "https://api.osf.io/v2/"
    response = requests.get(
        f"{BASE_URL}nodes/{repo_id}/files/osfstorage/", 
        headers=headers
    )
    
    if response.status_code == 200:
        files = []
        data = response.json()
        
        for file in data.get('data', []):
            if file['attributes']['name'].lower().endswith(('.csv', '.xlsx', '.xls', '.sav', '.dta', '.rdata', '.json')):
                file_data = {
                    'name': file['attributes']['name'],
                    'size': file['attributes']['size'],
                    'date_created': file['attributes']['date_created'],
                    'date_modified': file['attributes']['date_modified'],
                    'download_url': file['links']['download']
                }
                files.append(file_data)
        
        return files
    else:
        print(f"Failed to retrieve files for repository {repo_id}. HTTP Status Code: {response.status_code}")
        return []

def format_repos_to_markdown(repos):
    """
    Convert repository data into readable markdown format
    """
    markdown_output = "# Related OSF Repositories\n\n"
    
    for repo in repos:
        # Build repository information string
        repo_info = f"## {repo['title']}\n\n"
        repo_info += f"**Repository ID:** {repo['id']}\n\n"
        repo_info += f"**Description:** {repo['description']}\n\n"
        repo_info += f"**Created:** {repo['date_created']}\n\n"
        repo_info += f"**Last Modified:** {repo['date_modified']}\n\n"
        repo_info += f"**Public:** {'Yes' if repo['public'] else 'No'}\n\n"

        # Add file metadata if available
        if repo.get('files'):
            repo_info += f"### Files\n\n"
            for file in repo['files']:
                repo_info += f"- **Name:** {file['name']}\n"
                repo_info += f"  - **Size:** {file['size']} bytes\n"
                repo_info += f"  - **Created:** {file['date_created']}\n"
                repo_info += f"  - **Last Modified:** {file['date_modified']}\n"
                repo_info += f"  - **Download Link:** [{file['download_url']}]({file['download_url']})\n\n"
        repo_info += "---\n\n"
        
        markdown_output += repo_info
    
    return markdown_output
