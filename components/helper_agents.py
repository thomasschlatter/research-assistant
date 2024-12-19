
from openai import OpenAI
import os
import requests
import json
from pathlib import Path
def extract_json_from_response(response_text):
    """Extracts JSON content from response text by finding the first [ or { character
    and matching it with the corresponding closing bracket"""

    # Find start of JSON content
    json_start = response_text.find('[')
    if json_start == -1:
        json_start = response_text.find('{')

    if json_start == -1:
        return response_text
    
    # Track nested brackets to find proper JSON end
    bracket_count = 0
    in_string = False
    escape_char = False

    for i in range(json_start, len(response_text)):
        char = response_text[i]
    
        # Handle string literals
        if char == '"' and not escape_char:
            in_string = not in_string
        elif char == '\\' and not escape_char:
            escape_char = True
            continue
    
        if not in_string:
            if char in '[{':
                bracket_count += 1
            elif char in ']}':
                bracket_count -= 1
            
            if bracket_count == 0:
                # Found matching end bracket
                return response_text[json_start:i+1].strip()
            
        escape_char = False

    return response_text

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_osf_data(proposal_path='tmp/proposals/proposal.md', repos_path='tmp/proposals/repositories.md'):
    """
    Uses LLM to parse proposal and repository information to download relevant OSF datasets
    """
    # Read proposal and repository information
    with open(proposal_path, 'r', encoding='utf-8') as f:
        proposal = f.read()
    
    with open(repos_path, 'r', encoding='utf-8') as f:
        repositories = f.read()

    # Create prompt for LLM to identify OSF datasets
    system_prompt = """You are a research data expert who must return ONLY a JSON array containing objects with exactly these fields:
{
    "url": "direct_download_url_string",
    "local_path": "relative_path_string",
    "description": "brief_description_string"
}

Each object in the array represents one OSF file to download. No other information or text should be included in your response.

Example valid response:
[
    {
        "url": "https://osf.io/download/example1.csv",
        "local_path": "dataset1/data.csv",
        "description": "Primary behavioral experiment results"
    }
]
"""
    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Based on this research proposal and repository information:
            
            Proposal:
            {proposal}
            
            Repositories:
            {repositories}
            
            Return a JSON object containing:
            1. OSF file direct download URLs
            2. Local destination paths for each file
            3. Brief description of each dataset
            """}
        ],
        temperature=0.7
    )
    # Parse LLM response to get download information
    response_text = response.choices[0].message.content
    json_content = extract_json_from_response(response_text)
    
    # Add debug printing
    print("Raw response:", response_text)
    print("Extracted JSON:", json_content)
    
    try:
        # Try parsing with strict=False to handle potential whitespace issues
        download_info = json.loads(json_content.strip(), strict=False)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Error location: line {e.lineno}, column {e.colno}")
        print(f"Error message: {e.msg}")
        # Fallback: try cleaning the string
        cleaned_content = json_content.replace('\n', '').replace('\r', '').strip()
        download_info = json.loads(cleaned_content)

    # Create data directory
    data_dir = Path('tmp/analysis/data')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download files
    downloaded_files = {}
    for file_info in download_info:
        try:
            # Download file
            response = requests.get(file_info['url'])
            response.raise_for_status()
            
            # Save to specified path
            save_path = data_dir / file_info['local_path']
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
                
            downloaded_files[file_info['local_path']] = {
                'description': file_info['description'],
                'status': 'success'
            }
            
        except Exception as e:
            downloaded_files[file_info['local_path']] = {
                'description': file_info['description'],
                'status': 'failed',
                'error': str(e)
            }

    # Save download report
    with open(data_dir / 'download_report.json', 'w') as f:
        json.dump(downloaded_files, f, indent=4)

    return downloaded_files

def analyze_downloaded_files(download_report_path='tmp/analysis/data/download_report.json'):
    """
    Analyzes downloaded files and creates metadata for statistical analysis
    """
    import pandas as pd
    import rpy2.robjects as robjects
    from pathlib import Path
    
    # Load download report
    with open(download_report_path, 'r') as f:
        download_report = json.load(f)
    
    data_analysis = {}
    data_dir = Path('tmp/analysis/data')
    
    for filepath, info in download_report.items():
        if info['status'] == 'success':
            full_path = data_dir / filepath
            file_metadata = {
                'description': info['description'],
                'file_type': full_path.suffix.lower(),
                'variables': [],
                'num_rows': 0,
                'data_types': {},
                'missing_values': {},
                'summary_stats': {}
            }
            
            try:
                if file_metadata['file_type'] == '.csv':
                    df = pd.read_csv(full_path)
                elif file_metadata['file_type'] == '.xlsx':
                    df = pd.read_excel(full_path)
                elif file_metadata['file_type'] == '.rdata':
                    robjects.r['load'](str(full_path))
                    df = pd.DataFrame(robjects.r['data'])
                
                file_metadata.update({
                    'variables': df.columns.tolist(),
                    'num_rows': len(df),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'summary_stats': df.describe().to_dict()
                })
                
            except Exception as e:
                file_metadata['error'] = str(e)
            
            data_analysis[filepath] = file_metadata
    
    # Save analysis metadata
    metadata_path = data_dir / 'analysis_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(data_analysis, f, indent=4)
    
    return data_analysis
