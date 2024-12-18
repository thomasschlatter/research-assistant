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

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

research_field = "Linguistics"
research_sub_field = "Sound Symbolism"

llm = ChatOllama(model="llama3.2")

def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return goto


#############################
########### TOOLS ###########
#############################



#### 

from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(max_results=5)

#### 

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
###
@tool
def check_existing_write_ups(
    research_field: Annotated[str, "The main field of research"],
    research_sub_field: Annotated[str, "The specific sub-field of research"]
) -> str:
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
    research_field: Annotated[str, "The main field of research"],
    research_sub_field: Annotated[str, "The specific sub-field of research"]
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
        json.dump(content, f, indent=4)
    
    return f"Successfully wrote proposal to {file_path}"

###


@tool
def write_write_up_to_file(
    content: Annotated[str, "The content to write to the file"],
    research_field: Annotated[str, "The main field of research"],
    research_sub_field: Annotated[str, "The specific sub-field of research"]
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
    
    # Write content as JSON
    data = {
        "research_field": research_field,
        "research_sub_field": research_sub_field,
        "content": content,
        "timestamp": timestamp
    }
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
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

    You work with the scientific writer collegue.

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
    - Conclusion (optional or integrated with Discussion)
    - Literature Review (sometimes part of the Introduction)
    - References
    - Appendices (optional)
    - Keywords (optional)
    - Funding Statement (optional)
    - Conflict of Interest Statement (optional)
    3. You write in Markdown, save the file to a .md file.

    You work with the lead scientist collegue.
    """
    ),
)

data_curator_Agent = create_react_agent(
    llm,
    tools=[check_koggle],
    state_modifier=make_system_prompt(
    f"""You are a senior data scientist, and knowledgeable in the field of {research_field}, specifically {research_sub_field}.

    - You will have to check koggle for ONE dataset or repository that can be used to answer the research question in the proposal.
    - If the available datasets or repository are not satisfactory then inform the lead scientist, so the proposal can be adjusted.
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

# Add all necessary edges
workflow.add_edge(START, "lead_scientist")
workflow.add_edge("lead_scientist", "scientific_writer")
workflow.add_edge("scientific_writer", "lead_scientist")
graph = workflow.compile()


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
        instructions = f"Improve the following proposal: {content}. Then call the scientific writer to create a paper write-up based on this proposal."
    else:
        print(f"Directory {path} exists but contains no paper proposals")
        instructions = "Come up with a paper proposal and save it. Then call the scientific writer to create a paper write-up."
else:
    print(f"Directory does not exist, creating it...")
    path.mkdir(parents=True, exist_ok=True)
    instructions = "Come up with a paper proposal and save it. Then call the scientific writer to create a paper write-up."
    
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
                    content = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
                    table.add_row(agent, msg_type, content)

    console.print(Panel(
        table,
        title="[bold blue]Conversation Flow[/bold blue]",
        border_style="blue"
    ))
    console.print("[dim]═══════════════════════════════════[/dim]")


