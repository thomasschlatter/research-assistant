from components.brainstormer import generate_research_paper_idea
import pathlib
import json
from typing import Literal
from langchain_community.llms import Ollama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from langchain_core.tools import tool
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langgraph.graph import MessageGraph, END
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from typing import List
from langchain_ollama.chat_models import ChatOllama
from prompts.system_prompt import make_system_prompt
import requests
from semanticscholar import SemanticScholar
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from langchain_community.tools.tavily_search import TavilySearchResults

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

import os

research_field = "Linguistics"
research_sub_field = "Sound Symbolism"

llm = ChatOpenAI(model="gpt-4o")

## LOAD TOKENS

# Retrieve the OSF_API_KEY from environment variables
OSF_API_TOKEN = os.getenv("OSF_API_TOKEN")
if OSF_API_TOKEN:
    print("OSF API Key retrieved successfully!")
else:
    print("OSF API Key not found. Make sure it is set.")

# Retrieve the TAVILY_API_KEY from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if TAVILY_API_KEY:
    print("Tavily API Key retrieved successfully!")
else:
    print("Tavily API Key not found. Make sure it is set.")

# Retrieve the OPENAI_API_KEY from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    print("OpenAI API Key retrieved successfully!")
else:
    print("OpenAI API Key not found. Make sure it")

# Retrieve the SEMANTIC_SCHOLAR from environment variables
# SEMANTIC_SCHOLAR_KEY = os.getenv("SEMANTIC_SCHOLAR_KEY")
# if SEMANTIC_SCHOLAR_KEY:
#     print("Semantic Scholar API Key retrieved successfully!")
# else:
#     print("Semantic Scholar API Key not found. Make sure it is set.")

sch = SemanticScholar()

#############################
###### GET_NEXT_LOGIC #######
#############################

def get_next_node(last_message: BaseMessage, goto: str):
    print("FINAL ANSWER" in last_message.content)
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return goto

#############################
########### TOOLS ###########
#############################

tavily_tool = TavilySearchResults(max_results=5)

###

@tool
def check_existing_write_ups() -> str:
    """Check if there are existing research paper write-ups in the specified research field directory"""
    
    # Create path format: research/proposals/field_subfield
    folder_name = f"{research_field.lower()}_{research_sub_field.lower().replace(' ', '_')}"
    path = pathlib.Path(f"research/proposals/{folder_name}")
    
    if path.exists():
        # Get all .json files in the directory
        papers = list(path.glob("*.json"))
        if papers:
            return f"Found {len(papers)} existing paper write-ups in {path}"
        return f"Directory {path} exists but contains no paper write-ups"
    return f"No existing paper wripte-ups found in {path}"

###


@tool
def write_proposal_to_file(
    content: Annotated[str, "The content to write to the file"],
) -> str:
    """Write research paper proposal to a markdown file in the specified research field directory"""
    
    # Create folder path
    folder_name = f"{research_field.lower()}_{research_sub_field.lower().replace(' ', '_')}"
    folder_path = pathlib.Path(f"research/proposals/{folder_name}")
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = folder_path / f"proposal_{timestamp}.md"
    
    # Write content as JSON
    # data = {
    #     "research_field": research_field,
    #     "research_sub_field": research_sub_field,
    #     "content": content,
    #     "timestamp": timestamp
    # }
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return f"Successfully wrote proposal to {file_path}"

###

@tool
def write_write_up_to_file(
    content: Annotated[str, "The content to write to the file"]
) -> str:
    """Write research paper proposal to a markdown file in the specified research field directory"""
    
    # Create folder path
    folder_name = f"{research_field.lower()}_{research_sub_field.lower().replace(' ', '_')}"
    folder_path = pathlib.Path(f"research/write_ups/{folder_name}")
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = folder_path / f"write_up_{timestamp}.md"
    
    # # Write content as JSON
    # data = {
    #     "research_field": research_field,
    #     "research_sub_field": research_sub_field,
    #     "content": content,
    #     "timestamp": timestamp
    # }
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return f"Successfully wrote proposal to {file_path}"

###

repl = PythonREPL()

@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )


@tool
def search_kaggle_by_keyword(
    kaggle_query: Annotated[str, "A query string for the kaggle API"]
) -> str:
    """Search Kaggle for relevant datasets in the specified research field and sub-field"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        # Get dataset list
        datasets = api.dataset_list(search=kaggle_query, max_size=None, sort_by='published')
        
        if not datasets:
            return "No relevant datasets found on Kaggle"
            
        # Get details of top 5 datasets
        details = []
        for ds in datasets[:5]:
            ds_vars = vars(ds)
            dataset_info = {
                k: ds_vars[k] for k in [
                    'subtitleNullable', 'totalBytes', 'url', 'description', 
                    'usabilityRating', 'lastUpdated', 'title', 'id', 'ref', 'tags'
                ]
            }
            details.append(dataset_info)
            
        # Format response
        response = "Found relevant datasets on Kaggle:\n\n"
        for idx, dataset in enumerate(details, 1):
            response += f"{idx}. {dataset['title']}\n"
            response += f"   URL: {dataset['url']}\n"
            response += f"   Last Updated: {dataset['lastUpdated']}\n"
            response += f"   Description: {dataset['description'][:200]}...\n\n"
            
        return response
        
    except Exception as e:
        return f"Error searching Kaggle datasets: {str(e)}"

@tool
def search_osf_by_keyword(keyword: str) -> dict:
    """
    Search for projects using a specific keyword and return essential project information.

    Args:
        keyword (str): Keyword to search for.

    Returns:
        dict: Filtered search results containing only essential project information.
    """
    headers = {
        "Authorization": f"Bearer {OSF_API_TOKEN}"
    }
    BASE_URL = "https://api.osf.io/v2/"
    response = requests.get(f"{BASE_URL}nodes/?filter[title][icontains]={keyword}", headers=headers)

    if response.status_code == 200:
        data = response.json()
        essential_info = []
    
        for project in data.get('data', []):
            essential_info.append({
                'id': project['id'],
                'title': project['attributes']['title'],
                'date_created': project['attributes']['date_created'],
                'date_modified': project['attributes']['date_modified'],
                'public': project['attributes']['public'],
                'description': project['attributes']['description'],
                'url': project['links']['html']
            })
        
        return {'projects': essential_info}
    else:
        return {"error": response.text}

@tool
def search_semantic_scholar_by_keyword(
    keyword: Annotated[str, "The keyword to search for in Semantic Scholar"]
) -> str:
    """Search Semantic Scholar for relevant research papers based on the keyword"""
    try:
        # Search for papers using the provided keyword
        papers = sch.search_paper(
            keyword,
            limit=5,
            fields=['title', 'abstract', 'year', 'authors', 'url', 'citationCount']
        )
        
        # Format the results into a readable string
        results = "Found relevant papers on Semantic Scholar:\n\n"
        
        for paper in papers:
            # Get author names
            authors = [author['name'] for author in paper['authors']] if paper['authors'] else ['Unknown Author']
            author_str = ', '.join(authors[:3])  # Show first 3 authors
            if len(authors) > 3:
                author_str += ' et al.'
                
            # Build paper entry
            results += f"Title: {paper['title']}\n"
            results += f"Authors: {author_str}\n"
            results += f"Year: {paper['year'] if paper['year'] else 'N/A'}\n"
            results += f"Citations: {paper['citationCount']}\n"
            results += f"URL: {paper['url']}\n"
            
            # Add abstract if available
            if paper['abstract']:
                # Truncate abstract if too long
                abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
                results += f"Abstract: {abstract}\n"
            
            results += "\n---\n\n"
            
        return results
        
    except Exception as e:
        return f"Error searching Semantic Scholar: {str(e)}"

@tool
def write_citation_to_file(
    content: Annotated[str, "The citation content to write to the file"]
) -> str:
    """Write citations to a markdown file in the specified research field directory"""
    
    # Create folder path
    folder_name = f"{research_field.lower()}_{research_sub_field.lower().replace(' ', '_')}"
    folder_path = pathlib.Path(f"research/citations/{folder_name}")
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = folder_path / f"citations_{timestamp}.md"
    
    with open(file_path, "w") as f:
        json.dump(content, f, indent=4)
    
    return f"Successfully wrote citations to {file_path}"

#############################
########### AGENTS ##########
#############################

lead_research_agent = create_react_agent(
    llm,
    tools=[write_proposal_to_file],
    state_modifier=make_system_prompt(
    f"""You are a world-renowned expert researcher in the field of {research_field}, specifically {research_sub_field}:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of the latest developments and current research gaps
    - Experience in groundbreaking research projects
    
    Generate a state-of-the-art research paper idea that:
    1. Addresses a significant unsolved problem in your field
    2. Builds upon the most recent developments (2023-2024)
    3. Has potential for high academic impact
    4. Is highly specific and technically detailed
    5. Includes clear research objectives and methodology
    6. Uses ONLY ONE of the following publicly available dataset or published corpora:
    -
    7. Does NOT involve human subjects or new data collection
    8. Relies exclusively on existing online databases and research repositories
    
    Your proposal must explicitly state which public datasets will be used and confirm 
    that no human subject research is required.
    
    You lead the direction of the research and come up with the ideas. 

    Each time you come up with a new proposal, save it to the device.

    If the paper write-up meets the above conditions, respond with FINAL ANSWER.
    """
    ),
)

scientific_writer_agent = create_react_agent(
    llm,
    tools=[check_existing_write_ups, write_write_up_to_file],
    state_modifier=make_system_prompt(
    f"""You are a world-renowned scientific author in the field of {research_field}, specifically {research_sub_field}:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of paper formatting
    - Experience in groundbreaking research projects
    
    write a state-of-the-art research paper idea that:
    1. Is highly specific and technically detailed
    2. Includes the following sections:
    - Abstract
    - Introduction
    - Methods (Methodology)
    - Results
    - Discussion
    - Conclusion
    - Literature Review (sometimes part of the Introduction)
    - References
    - Appendices (optional)
    - Keywords (optional)
    - Funding Statement (optional)
    - Conflict of Interest Statement (optional)
    3. You write in Markdown, save the file to a .md file.
    """
    ),
)


scientific_citation_writer_agent = create_react_agent(
    llm,
    tools=[write_citation_to_file],
    state_modifier=make_system_prompt(
    f"""You are a world-renowned scientific author in the field of {research_field}, specifically {research_sub_field}:
    - Multiple high-impact publications in top-tier journals
    - Deep understanding of paper formatting
    - Experience in groundbreaking research projects
    
    write a meticulously exact citation section that:
    1. confirms with APA style
    2. You write in Markdown, save the file to a .md file.
    """
    ),
)

data_curator_agent = create_react_agent(
     llm,
     tools=[search_osf_by_keyword, search_kaggle_by_keyword],
     state_modifier=make_system_prompt(
     f"""You are a senior data scientist and expert in {research_field}, specifically {research_sub_field}.

     Your role is to:
     1. Analyze the research proposal carefully
     2. Break down what type of data would be needed (text corpus, audio files, annotated datasets, etc.)
     3. Create broad, general query strings that target the DATA needed to answer the research topic rather than the specific research topic
     3. Do not explicitly use the words corpus, dataset or repository in your queries
     4. Example queries:
        - Instead of "WordNet dataset" use "WordNet"
        - Instead of "sound symbolism" use "phonetic"
        - Instead of "health patterns" use "health"
        - Instead of "semantic analysis" use "annotated text"
    
     When searching:
     - Focus on finding versatile, well-documented datasets
     - Look for datasets with clear licensing information
     - Prioritize recently updated repositories
     - Consider datasets that may serve multiple research purposes
    
     After finding datasets:
     1. Evaluate if they meet the research requirements
     2. If suitable: Explain how the dataset can be adapted for the research
     3. If not suitable: Provide specific feedback to the lead scientist about what kind of data would be more appropriate

     Remember: Cast a wide net with general queries first, then evaluate specific usefulness for the research question.
     """
     ),
)


scientific_paper_finder_agent = create_react_agent(
     llm,
     tools=[search_semantic_scholar_by_keyword],
     state_modifier=make_system_prompt(
     f"""You are a world-renowned scientific author in the field of {research_field}, specifically {research_sub_field}:
    - Multiple high-impact publications in top-tier journals
    - Experience in groundbreaking research projects
    
    Your job is to find relevant scientific papers that can be cited to support the research proposal.
    """
     ),
)
#############################
########### NODES ###########
#############################

def lead_scientist_node(
    state: MessagesState,
) -> Command[Literal["lead_scientist", END]]:
    result = lead_research_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "scientific_writer")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="lead_scientist"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )

def scientific_paper_finder_node(
    state: MessagesState,
) -> Command[Literal["scientific_paper_finder", END]]:
    result = scientific_paper_finder_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "lead_scientist")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="scientific_paper_finder"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )

def scientific_writer_node(
    state: MessagesState,
) -> Command[Literal["scientific_writer", END]]:
    result = scientific_writer_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "lead_scientist")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="scientific_writer"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )

def scientific_citation_writer_node(
    state: MessagesState,
) -> Command[Literal["scientific_citation_writer", END]]:
    result = data_curator_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "lead_scientist")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="scientific_citation_writer"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )

def data_curator_node(
    state: MessagesState,
) -> Command[Literal["data_curator", END]]:
    result = data_curator_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "lead_scientist")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="data_curator"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )



# Chart generator agent and node
# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
# chart_agent = create_react_agent(
#     llm,
#     [python_repl_tool],
#     state_modifier=make_system_prompt(
#         "You can only generate charts. You are working with a researcher colleague."
#     ),
# )

# def chart_node(state: MessagesState) -> Command[Literal["researcher", END]]:
#     result = chart_agent.invoke(state)
#     goto = get_next_node(result["messages"][-1], "researcher")
#     # wrap in a human message, as not all providers allow
#     # AI message at the last position of the input messages list
#     result["messages"][-1] = HumanMessage(
#         content=result["messages"][-1].content, name="chart_generator"
#     )
#     return Command(
#         update={
#             # share internal message history of chart agent with other agents
#             "messages": result["messages"],
#         },
#         goto=goto,
#     )
# Fixed configuration
workflow = StateGraph(MessagesState)
workflow.add_node("lead_scientist", lead_scientist_node)
workflow.add_node("scientific_writer", scientific_writer_node)
workflow.add_node("data_curator", data_curator_node)
workflow.add_node("scientific_paper_finder", scientific_paper_finder_node)
workflow.add_node("scientific_citation_writer", scientific_citation_writer_node)


# Add all necessary edges
workflow.add_edge(START, "lead_scientist")
workflow.add_edge("lead_scientist", "scientific_paper_finder")
graph = workflow.compile()

# Generate and save the PNG image
png_image = graph.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.API,
)

# Save to a file
output_file = "workflow_graph.png"
with open(output_file, "wb") as f:
    f.write(png_image)


# Create path format: research/proposals/field_subfield
folder_name = f"{research_field.lower()}_{research_sub_field.lower().replace(' ', '_')}"
path = pathlib.Path(f"research/proposals/{folder_name}")

if path.exists():
    # Get all .json files in the directory
    papers = list(path.glob("*.md"))
    if papers:
        # Sort the papers by modification time (latest first)
        latest_paper = max(papers, key=lambda p: p.stat().st_mtime)
        
        # Read the content of the latest .md file
        with open(latest_paper, 'r', encoding='utf-8') as file:
            content = file.read()
            print(content)
        instructions = f"consult Schemantic Scholar for this proposal: {content}."
    else:
        print(f"Directory {path} exists but contains no paper proposals")
        instructions = "Use scientific_paper_finder for papers on this topic. Come up with a paper proposal and save it. Then call the scientific writer to create a paper write-up. Then consult either kaggle or OSF."
else:
    print(f"Directory does not exist, creating it...")
    path.mkdir(parents=True, exist_ok=True)
    instructions = "Use scientific_paper_finder for papers on this topic. Come up with a paper proposal and save it. Then call the scientific writer to create a paper write-up. Then consult either kaggle or OSF."
    
events = graph.stream(
    {
        "messages": [
            (
                "user",
                instructions
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 15},
)

#####################################
########### VISUALIZATION ###########
#####################################

console = Console()

for s in events:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Message Type", style="yellow", width=15)
    table.add_column("Content", style="green")

    # Handle nested structure
    for agent_name, agent_data in s.items():
        if isinstance(agent_data, dict) and 'messages' in agent_data:
            for msg in agent_data['messages']:
                agent = msg.name if hasattr(msg, 'name') else agent_name
                msg_type = msg.__class__.__name__
                
                # Handle tool calls separately
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        table.add_row(
                            agent,
                            "Tool Call",
                            f"Tool: {tool_call['name']}\nArgs: {tool_call['args']}"
                        )
                else:
                    # Truncate content if too long
                    # content = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
                    content = msg.content
                    table.add_row(agent, msg_type, content)

    console.print(Panel(
        table,
        title="[bold blue]Conversation Flow[/bold blue]",
        border_style="blue"
    ))
    console.print("[dim]═══════════════════════════════════[/dim]")


