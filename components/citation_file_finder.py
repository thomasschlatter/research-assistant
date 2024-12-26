import requests
import os
from openai import OpenAI

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

def get_citation_styles():
    """Fetch all available .csl files from citation-style-language/styles repository."""
    csl_files = []
    api_url = "https://api.github.com/repos/citation-style-language/styles/contents"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.csl'):
                csl_files.append(file['name'])
        return csl_files
    else:
        print(f"Failed to fetch files. Status Code: {response.status_code}, Message: {response.json()}")
        return csl_files
    

def select_citation_style(journal_name, csl_files):
    """
    Selects the most suitable citation style file based on the journal name.
    Returns the path to the citation style file (.csl)
    """
    system_prompt = """You are an expert in academic publishing formats and citation styles.
    Your task is to select the most appropriate CSL (Citation Style Language) filename from the provided list.
    Rules:
    1. You MUST ONLY select a filename that exists in the provided list
    2. Return ONLY the filename with .csl extension, nothing else
    3. If exact match not found, select the closest match from the available options"""

    # Convert list to string with clear formatting for better context
    files_formatted = "\n".join(csl_files)
    
    user_prompt = f"""Select the most appropriate citation style for '{journal_name}' from these files:

    {files_formatted}

    Return only the filename with .csl extension."""

    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=256
    )
    
    suggested_filename = response.choices[0].message.content.strip()
    
    # Validate the response is in the available files
    if suggested_filename not in csl_files:
        # Fallback to a default or raise error
        raise ValueError(f"Selected style '{suggested_filename}' not found in available files")
    
    return f"citation-styles/{suggested_filename}"

#def re_select_citation_style(journal_name, wrong_file_name, csl_files):

def download_citation_file(file_name):
    """
    Downloads a specific CSL file from citation-style-language/styles repository.
    Returns the local path to the downloaded file.
    """
    os.makedirs('tmp/citation', exist_ok=True)
    base_url = "https://raw.githubusercontent.com/citation-style-language/styles/master/"
    file_url = base_url + file_name
    local_path = f"tmp/citation/{file_name}"
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return local_path
    else:
        raise Exception(f"Failed to download citation style file. Status Code: {response.status_code}")

