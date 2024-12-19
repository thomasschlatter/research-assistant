import os
from components.paper_finder_agent import paper_finder_agent
from components.generate_proposal_agent import generate_research_proposal, refine_proposal_based_on_tools
from components.paper_writer_agent import generate_section
from components.repository_finder_agent import repository_finder_agent
from components.statistician_agent import display_folder_tree, generate_analysis_script, generate_results_section, parse_analysis_results, run_analysis_script
from components.helper_agents import analyze_downloaded_files, download_osf_data
from constants.available_tools import available_tools
from constants.paths import VENV_PATH
from constants.sections import sections
import subprocess

def main():
    print("=================================")
    print("Scientific Writer Assistant")
    print("=================================")
    
    field = "Linguistics"
    sub_field = "Sound Symbolism"
    max_iterations = 3
    
    # print(f"\nGenerating and refining ideas for {field} - {sub_field}")
    
    # # Generate initial proposal
    # initial_proposal = generate_research_proposal(field, sub_field, max_iterations=max_iterations)
    
    # # Collect related information
    # relevant_papers = paper_finder_agent(initial_proposal, papers_needed=20)
    # relevant_repositories = repository_finder_agent(initial_proposal, repos_needed=10)
    
    # # Refine proposal based on available tools and found repositories
    # final_proposal = refine_proposal_based_on_tools(initial_proposal, field, sub_field, relevant_repositories, available_tools, relevant_papers, max_iterations)
    # os.makedirs('tmp/proposals', exist_ok=True)
    
    # # Save all outputs
    # with open('tmp/proposals/proposal.md', 'w', encoding='utf-8') as f:
    #     f.write(final_proposal)
    
    # with open('tmp/proposals/relevant_papers.md', 'w', encoding='utf-8') as f:
    #     f.write(relevant_papers)
        
    # with open('tmp/proposals/repositories.md', 'w', encoding='utf-8') as f:
    #     f.write(relevant_repositories)

    # print("\nFinal Research Proposal:")
    # print("=====================")
    # print(final_proposal)
    # print("\nAll files saved in tmp/proposals/")

    # # =================================================

    # previous_sections = {}
    
    # # Generate sections up to methods
    # sections_to_generate = ['abstract', 'introduction', 'methods']
    
    # for section in sections_to_generate:
    #     print(f"\nGenerating {section}...")
    #     section_content = generate_section(final_proposal, field, sub_field, relevant_papers, available_tools, section, sections, max_iterations, previous_sections)
    #     # full_paper += section_content
    #     # previous_sections[section] = section_content
    #     with open(f'tmp/write_up/{section}.md', 'w', encoding='utf-8') as f:
    #         f.write(section_content)
    

    # # After repositories are found:
    # downloaded_data = download_osf_data()
    # print(downloaded_data)

    # meta_data = analyze_downloaded_files(download_report_path='tmp/analysis/data/download_report.json')
    
    # folder_Tree = display_folder_tree("tmp/")

    # analysis_script = generate_analysis_script(
    #     folder_structure=folder_Tree,
    #     proposal=final_proposal,
    #     research_area=field,
    #     data_description=meta_data, 
    #     available_tools=available_tools
    # )

    # run_analysis_script(venv=VENV_PATH, max_retries=3)

    # Parse results and generate the results section
    results = parse_analysis_results()
    results_section = generate_results_section(results, research_area="your research area")
if __name__ == "__main__":
    main()