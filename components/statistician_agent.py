
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
                                  
            install_required_packages("tmp/analysis/analysis.py")
            
            # Use python executable from venv directly
            python_executable = "python" if venv == "python" else venv
            
            # Run the script with explicit python executable
            result = subprocess.run(
                [python_executable, "analysis.py"],
                capture_output=True,
                text=True,
                check=True,
                cwd="tmp/analysis"
            )

            check_and_fix_empty_analysis_json()

            # Check if stdout contains error keywords
            if "error" in result.stdout.lower():
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=["python", "analysis.py"],
                    output=result.stdout,
                    stderr="Error detected in stdout: " + result.stdout
                )

            print(result.stdout)
            print("Successfully executed script!")
            
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

def clean_script(script):
    """Remove docstrings and text between triple quotes from the script."""
    # Remove triple-quoted strings (both single and double quotes)
    script = re.sub(r'"""[\s\S]*?"""', '', script)
    script = re.sub(r"'''[\s\S]*?'''", '', script)
    return script

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
            
            The script can make use these libraries: {available_tools}
            
            The script should:
            1. Load and preprocess the data that is necessary to complete the statistical analysis as mentioned in the proposal 
            2. Use the absolute paths of the files that you want to analyze from the folder structure
            3. Perform relevant statistical tests
            4. Create visualizations and make sure all the variables are named accordingly
            5. Save results in a structured JSON format
            6. Include comprehensive documentation about the analysis and its results in the json file

            IMPORTANT: Keep the analysis simple!

            Workspace absolute path: {workspace_path}
            - Save results of the analysis in a structured JSON format to {workspace_path}\tmp\analysis\analysis.json
            - Save images of plots in {workspace_path}\tmp\analysis\plots folder, include them together with a detailed description in the JSON file.

            """}
        ],
        temperature=0.7
    )

    # Extract only the Python code between markers
    full_response = response.choices[0].message.content.strip()
    
    # Find the code between ```python ... ``` markers
    print(full_response)
    code_match = re.search(r'```python(.*?)```', full_response, re.DOTALL)
    if code_match:
        analysis_script = code_match.group(1).strip()
    else:
        analysis_script = full_response  # Fallback if no markers found
    
    # Clean the script before saving
    cleaned_script = clean_script(analysis_script)
    
    # Save the cleaned generated script
    with open("tmp/analysis/analysis.py", "w") as f:
        f.write(cleaned_script)
    
    return cleaned_script


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
            """}
        ],
        temperature=0.7
    )

    # Extract updated code
    updated_script = response.choices[0].message.content.strip()
    code_match = re.search(r'```python(.*?)```', updated_script, re.DOTALL)
    if code_match:
        updated_script = code_match.group(1).strip()
    
    # Save the updated script
    with open("tmp/analysis/analysis.py", "w") as f:
        f.write(updated_script)
    
    return updated_script

# Install required packages
def install_required_packages(script_path):
    """
    Detects and installs required packages from a Python script
    """
    import subprocess
    import re

    with open(script_path, 'r') as file:
        content = file.read()

    # Find import statements using regex
    import_patterns = [
        r'^import\s+(\w+)',  # matches: import numpy
        r'^from\s+(\w+)\s+import',  # matches: from pandas import
        r'import\s+(\w+)\s+as',  # matches: import numpy as np
    ]

    # Define packages to skip
    SKIP_PACKAGES = {'json', 'os'}

    packages = set()
    for pattern in import_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        # Filter out packages that should be skipped
        packages.update(pkg for pkg in (match.group(1) for match in matches) if pkg not in SKIP_PACKAGES)

    # Install each detected package
    for package in packages:
        try:
            subprocess.run(["pip", "install", package], check=True)
            print(f"Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

def check_and_fix_empty_analysis_json():
    """
    Checks if analysis.json is empty and fixes documentation export if needed.
    if updated returns True, if not False
    """
    json_path = "tmp/analysis/analysis.json"
    script_path = "tmp/analysis/analysis.py"
    
    try:
        with open(json_path, 'r') as f:
            analysis_data = json.load(f)
            
        if not analysis_data or analysis_data == {}:
            print("Empty analysis JSON detected. Fixing documentation export...")
            
            with open(script_path, 'r') as f:
                analysis_script = f.read()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in Python statistical analysis and documentation."},
                    {"role": "user", "content": f"""
                    The following analysis script is not properly exporting documentation to analysis.json:
                    
                    {analysis_script}
                    
                    Modify the script to ensure it:
                    1. Maintains all existing analysis logic
                    2. Exports comprehensive documentation about the analysis steps and results to analysis.json
                    3. Includes descriptions of any visualizations created
                    4. Documents statistical test results and their interpretation
                    5. Uses proper JSON structure for the documentation
                    
                    The documentation should ONLY be saved to: tmp/analysis/analysis.json
                    """}
                ],
                temperature=0.7
            )
            
            updated_script = response.choices[0].message.content.strip()
            code_match = re.search(r'(.*?)', updated_script, re.DOTALL)
            if code_match:
                updated_script = code_match.group(1).strip()
            
            with open(script_path, 'w') as f:
                f.write(updated_script)
                
            print("Analysis script updated with proper JSON documentation export.")
            return True
            
    except Exception as e:
        print(f"Error checking/fixing analysis JSON: {e}")
        return False

    return False
