
from openai import OpenAI
import os
import json
import re

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize clients
client = OpenAI(api_key=openai_api_key)

# Add this function to capture both output and errors
def run_analysis_script(venv, max_retries=3):
    import subprocess
    print("Running analysis script...")
    
    current_try = 0
    
    while current_try < max_retries:
        try:
            # Create required directories if they don't exist
            os.makedirs("tmp/analysis/plots", exist_ok=True)
            
            # Install required packages
            packages = ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "seaborn"]
            for package in packages:
                subprocess.run(["pip", "install", package], check=True)
            
            # Run the script
            result = subprocess.run(
                [venv, "analysis.py"],
                capture_output=True,
                text=True,
                check=True,
                cwd="tmp/analysis"
            )
            
            print("Analysis Output:")
            print(result.stdout)
            
            return {
                "success": True,
                "output": result.stdout,
                "error": None
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Analysis Error:\n{e.stderr}")
            current_try += 1
            
            if current_try < max_retries:
                print(f"Attempt {current_try} of {max_retries}: Updating script based on errors...")
                
                # Read current script
                with open("tmp/analysis/analysis.py", "r") as f:
                    current_script = f.read()
                
                # Update script based on errors
                updated_script = update_analysis_script(e.stderr, current_script)
                print("Script updated, retrying analysis...")
                continue
            
            return {
                "success": False,
                "output": e.stdout,
                "error": e.stderr
            }
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

def generate_folder_tree(folder_path, prefix=""):
    entries = sorted(os.listdir(folder_path), key=str.lower)
    parts = []
    for index, entry in enumerate(entries):
        # Check if this is the last entry
        is_last = (index == len(entries) - 1)
        # Build the current line
        connector = "└──" if is_last else "├──"
        parts.append(f"{prefix}{connector} {entry}")
        # Recurse into directories
        entry_path = os.path.join(folder_path, entry)
        if os.path.isdir(entry_path):
            sub_prefix = "    " if is_last else "│   "
            parts.append(generate_folder_tree(entry_path, prefix + sub_prefix))
    return "\n".join(parts)

def display_folder_tree(folder_path):
    folder_name = os.path.basename(folder_path) or folder_path
    tree = f"{folder_name}\n"
    tree += generate_folder_tree(folder_path)
    return tree

def generate_analysis_script(folder_structure, proposal, research_area, data_description, available_tools):
    """
    Generates a Python script for statistical analysis based on the research proposal.
    """
    # Get absolute workspace path
    workspace_path = os.path.abspath(os.getcwd())
    
    system_prompt = f"""You are a statistical analysis expert with:
    - Deep expertise in research methodology and statistical analysis
    - Extensive experience with Python statistical libraries
    - Strong background in data visualization and reporting
    
    Generate a complete Python script that will:
    1. Perform statistical analysis relevant to the research proposal
    2. Generate appropriate visualizations (if necessary)
    3. Save results in a structured JSON format
    4. Include comprehensive documentation
    
    The script can make use these libraries: {available_tools}
    
    Workspace absolute path: {workspace_path}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Create a Python script that performs statistical analysis for this research:
            
            Research Proposal: {proposal}
            
            Relevant data description:
            {data_description}
            
            Folder Structure:
            {folder_structure}
            
            Absolute Workspace Path: {workspace_path}

            The script should:
            1. Load and preprocess the data that is necessary to complete the statistical analysis as mentioned in the proposal 
            2. Use the absolute paths of the files that you want to analyze from the folder structure
            3. Perform relevant statistical tests
            4. Create visualizations
            5. Save results to tmp/analysis/analysis.json with the following keys: test_statistics, p_values, effect_sizes, confidence_intervals, plot_paths, plot_captions, summary_statistics
            6. Save visualizations to 'tmp/analysis/plots/'
            """}
        ],
        temperature=0.7
    )

    # Extract only the Python code between  and  markers
    full_response = response.choices[0].message.content.strip()
    
    # Find the code between ```···``` markers
    print(full_response)
    code_match = re.search(r'```python(.*?)```', full_response, re.DOTALL)
    if code_match:
        analysis_script = code_match.group(1).strip()
    else:
        analysis_script = full_response  # Fallback if no markers found
    
    # Save the generated script
    with open("tmp/analysis/analysis.py", "w") as f:
        f.write(analysis_script)
    
    return analysis_script

def parse_analysis_results(analysis_json_path="tmp/analysis/analysis.json"):
    """
    Reads and parses the analysis results from the JSON file.
    Creates the file with empty results if it doesn't exist.
    """
    try:
        with open(analysis_json_path, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        # Create default empty structure
        results = {
            "test_statistics": {},
            "p_values": {},
            "effect_sizes": {},
            "confidence_intervals": {},
            "plot_paths": [],
            "plot_captions": {},
            "summary_statistics": {}
        }
        # Create the file with empty results
        with open(analysis_json_path, 'w') as f:
            json.dump(results, f, indent=4)
            
    return results

def generate_results_section(analysis_results, proposal):
    """
    Generates the results section based on the statistical analysis.
    """
    system_prompt = """You are an expert in scientific writing and statistical reporting.
    Create a comprehensive results section that:
    1. Reports statistical findings clearly and accurately
    2. Describes visualizations with proper academic language
    3. Highlights significant findings
    4. Maintains proper scientific writing style
    5. Include images and captions 
    6. You write in markdown format

    IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication.
    IMPORTANT: Stick to the research objects of the proposal
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Based on these analysis results, write a results section:
            
            Analysis Results: {analysis_results}
            Proposal: {proposal}
            
            Include:
            - Statistical test results with proper notation
            - Description of visualizations
            - Effect sizes and confidence intervals
            - Key findings and their significance
            """}
        ],
        temperature=0.7
    )
    
    results_section = response.choices[0].message.content.strip()
    return results_section

def generate_section(proposal, specific_research_area, specific_research_sub_area, relevant_papers, available_tools, section_name, all_sections, max_iterations, previous_sections=None):
    """
    Generates and refines a cutting-edge research paper idea in a highly specific research area.
    """
    system_prompt = f"""You are a world-renowned expert researcher in {specific_research_area}, specifically {specific_research_sub_area}, with:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Write a comprehensive scientific paper section that advances the state-of-the-art research. Your writing will:
    
    Present a significant unsolved problem in {specific_research_area}, specifically {specific_research_sub_area}, 
    incorporating the latest developments from 1995-2024. The research must demonstrate high potential for academic 
    impact through novel contributions. Provide in-depth technical details and clearly articulated research 
    methodology.

    Requirements:
    1. Use proper academic writing style with formal language
    2. Include relevant citations in IEEE format (Author et al., YYYY)
    3. Integrate analysis of publicly available datasets and published corpora
    4. Focus on computational/analytical methods using existing databases
    5. Avoid any reference to new data collection or human subject research
    6. Connect ideas logically with smooth transitions between paragraphs
    7. Support claims with references to peer-reviewed literature
    8. Maintain academic tone throughout the section

    IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication.
    IMPORTANT: Stick to the research objects of the proposal
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
            f"""
            This is the research proposal:
            {proposal}
            The paper has the following sections: {all_sections}.
            Here are some papers that can be used:
            
            {relevant_papers}

            IMPORTANT: Do not use bullet points, instead write in a flowing narrative style appropriate for a scientific publication. Cite as many of the papers as you can.
            write ONLY the following section: {section_name}
            """
             }
        ],
        temperature=0.7,
        max_tokens=8192  # Adjust this to the maximum your model allows (e.g., 8192 for GPT-4o)
    )
    sec = response.choices[0].message.content.strip()

    return sec

def update_analysis_script(error_message, original_script):
    """
    Updates the analysis script based on error messages using LLM guidance.
    """
    system_prompt = """You are an expert Python developer specializing in data analysis and statistical computing.
    Your task is to fix code errors in statistical analysis scripts by:
    1. Analyzing error messages carefully
    2. Identifying root causes
    3. Implementing robust solutions
    4. Maintaining the original analysis objectives
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            The following analysis script encountered errors:
            
            Original Script:
            
            {original_script}
            
            
            Error Message:
            {error_message}
            
            Please provide an updated version of the script that:
            1. Fixes all identified errors
            2. Maintains the original analysis objectives
            3. Includes proper error handling
            4. Validates inputs and outputs
            5. Uses best practices for scientific computing
            """}
        ],
        temperature=0.7
    )

    # Extract updated code
    updated_script = response.choices[0].message.content.strip()
    code_match = re.search(r'(.*?)', updated_script, re.DOTALL)
    if code_match:
        updated_script = code_match.group(1).strip()
    
    # Save the updated script
    with open("tmp/analysis/analysis.py", "w") as f:
        f.write(updated_script)
    
    return updated_script
