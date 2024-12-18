import os
import json
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from openai import OpenAI
from semanticscholar import SemanticScholar
from langchain_ollama import OllamaLLM
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


def search_datasets(query, max_results=5):
    """Search Kaggle datasets and return results"""
    api = KaggleApi()
    api.authenticate()
    query = query.replace("\"", "")
    datasets = api.dataset_list(search=query, max_size=None, sort_by='published')
    details = []
    ds = datasets[0]
    for ds in datasets:
        # get subtitleNullable, totalBytes, url, description, usabilityRating, lastUpdated, title, id, ref, tags
        ds_vars = vars(ds)
        # loop through ds_vars and add each variable to details list
        details.append({k: ds_vars[k] for k in ['subtitleNullable', 'totalBytes', 'url', 'description', 'usabilityRating', 'lastUpdated', 'title', 'id', 'ref', 'tags']})
    return details

def get_timestamped_dir(base_dir):
    """Create timestamped directory name"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(base_dir, f"data_{timestamp}")

def save_dataset_info(datasets, query, output_dir="research_data"):
    """Save dataset metadata to timestamped directory"""
    timestamped_dir = get_timestamped_dir(output_dir)
    os.makedirs(timestamped_dir, exist_ok=True)
    
    dataset_info = {
        "query": query,
        "datasets": []
    }
    for dataset in datasets:
        info = {
            "description": dataset.description,  # This contains the dataset description
            "title": dataset.title,
            "ref": dataset.ref,
            "size": dataset.totalBytes,
            "lastUpdated": dataset.lastUpdated.isoformat(),
            "url": dataset.url,
            "downloadCount": dataset.downloadCount,
            "licenseName": dataset.licenseName
        }
        dataset_info["datasets"].append(info)
    
    info_path = os.path.join(timestamped_dir, "info.json")
    with open(info_path, "w") as f:
        json.dump(dataset_info, f, indent=2)
    return info_path, timestamped_dir

def download_dataset(dataset_ref, output_dir):
    """Download a Kaggle dataset"""
    api = KaggleApi()
    api.authenticate()
    os.makedirs(output_dir, exist_ok=True)
    api.dataset_download_files(dataset_ref, path=output_dir, unzip=True)

def curate_data(query, max_results=50, output_dir="research_data", model="ollama"):
    """Main function to search, save info and download datasets"""
    # Search for datasets
    datasets = search_datasets(query, max_results)

    # Filter relevant datasets
   
    # Save dataset information and get timestamped directory
    info_path, timestamped_dir = save_dataset_info(datasets, query, output_dir)

    return info_path, timestamped_dir

def filter_datasets(datasets, proposal):
    """Filter datasets based on relevance for paper proposal"""
    filtered_datasets = []
    
    # Create a relevance scoring prompt
    scoring_prompt = f"""Rate the relevance of this dataset for the following research proposal on a scale of 0-10:
    
    Research Proposal: {proposal}
    
    Dataset Title: {{title}}
    Dataset Description: {{description}}
    
    Consider:
    1. Data type alignment with research needs
    2. Variable coverage
    3. Dataset quality and size
    4. Update frequency and maintenance
    
    Return only the numeric score between 0-10."""
    
    for dataset in datasets:
        # Format the specific dataset details
        dataset_prompt = scoring_prompt.format(
            title=dataset.title,
            description=dataset.description
        )
        
        try:
            # Use Ollama if available, fallback to OpenAI
            if ollama_client:
                score_text = ollama_client.invoke(dataset_prompt)
            else:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data science expert evaluating dataset relevance."},
                        {"role": "user", "content": dataset_prompt}
                    ],
                    temperature=0.3
                )
                score_text = response.choices[0].message.content
            
            # Extract numeric score
            score = float(re.search(r'\d+(?:\.\d+)?', score_text).group())
            
            # Add datasets with score >= 7 to filtered list
            if score >= 7:
                dataset.relevance_score = score  # Add score as attribute
                filtered_datasets.append(dataset)
                
        except Exception as e:
            print(f"Error processing dataset {dataset.title}: {e}")
            continue
    
    # Sort by relevance score
    filtered_datasets.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return filtered_datasets

def get_kaggle(proposal, model="ollama", specific_research_area=None, specific_research_sub_area=None):
    """Wrapper function to call the main function"""
    if model == "ollama" and ollama_client:
        print("Using Ollama for inference.")
        dataset_query = ollama_client.invoke(
            f"""You are a data science expert. You have to create a Kaggle search string based on the **core data requirements** of this research area: {specific_research_area} and the **specific research area**: {specific_research_sub_area}
                
                1. Avoid using terms that relate to the final hypothesis, goal, or analysis outcomes. 
                2. Focus only on datasets that provide fundamental variables. 
                3. Use terms that describe measurable, observable, or existing data rather than abstract relationships or hypotheses.
                4. Ensure the query is general and does not include any specific dataset names or URLs.

                IMPORTANT: Only return a short string, without any additional text. Examples:
                - Climate change
                - Economic indicators
                - Social media data
                - Environmental factors
                - Health data
                """ 
        ).strip()
        print(dataset_query)
    else:
        dataset_query = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                "role": "system",
                "content": """You are a data science expert. Your task is to extract 2-3 key terms from the research proposal that represent the **raw data inputs or metadata** required to conduct the research. 
                
                1. Avoid using terms that relate to the final hypothesis, goal, or analysis outcomes. 
                2. Focus only on datasets that provide fundamental variables. 
                3. Use terms that describe measurable, observable, or existing data rather than abstract relationships or hypotheses.
                4. Ensure the query is general and does not include any specific dataset names or URLs.
                """
                },
                {
                "role": "user",
                "content": f"""Generate a Kaggle dataset search query based on the **core data requirements** of this proposal: {proposal}. 

               IMPORTANT: Only return the search query, without any additional text.
                """
                }
            ],
            temperature=0.7,
        )

    print(f"\nSearching for datasets with query: {dataset_query}")
    # Search for datasets
    datasets = search_datasets(dataset_query, max_results=50)
    # Filter datasets based on relevance score

    return datasets
