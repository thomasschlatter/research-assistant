import os
from components.journal_format_finder_agent import get_journal_citation_requirements, get_journal_format_requirements
from components.paper_finder_agent import paper_finder_agent, re_paper_finder_agent
from components.generate_proposal_agent import generate_research_proposal, refine_proposal_based_on_tools
from components.paper_writer_agent import generate_conclusion_section, generate_discussion_section, generate_final_paper, generate_section, generate_title, re_generate_section
from components.repository_finder_agent import repository_finder_agent
from components.statistician_agent import display_folder_tree, generate_analysis_script, generate_results_section, parse_analysis_results, run_analysis_script
from components.helper_agents import analyze_downloaded_files, download_osf_data
from components.journal_finder_agent import generate_journal
from constants.available_tools import available_tools
from constants.other import DRAFT_REFINEMENT_ITERATIONS
from constants.paths import VENV_PATH
from constants.sections import sections
import subprocess

def main():
    print("==========================")
    print("Scientific Writer Assistant")
    print("==========================")
    
    field = "Linguistics"
    sub_field = "Sound Symbolism"
    max_iterations = 3

    # PROPOSAL SECTION
    
    print(f"\nGenerating and refining ideas for {field} - {sub_field}")
    
    # Generate initial proposal
    initial_proposal = generate_research_proposal(field, sub_field, max_iterations=max_iterations)
    
    # Collect related information
    relevant_papers = paper_finder_agent(initial_proposal, papers_needed=20)
    relevant_repositories = repository_finder_agent(initial_proposal, repos_needed=10)
    
    # Refine proposal based on available tools and found repositories
    final_proposal = refine_proposal_based_on_tools(initial_proposal, field, sub_field, relevant_repositories, available_tools, relevant_papers, max_iterations)
    os.makedirs('tmp/proposals', exist_ok=True)
    
    # Save all outputs
    with open('tmp/proposals/proposal.md', 'w', encoding='utf-8') as f:
        f.write(final_proposal)
    
    with open('tmp/proposals/relevant_papers.md', 'w', encoding='utf-8') as f:
        f.write(relevant_papers)
        
    with open('tmp/proposals/repositories.md', 'w', encoding='utf-8') as f:
        f.write(relevant_repositories)

    print("\nFinal Research Proposal saved in tmp/proposals/")

    # =================================================

    previous_sections = {}
    
    # Generate sections up to methods
    sections_to_generate = ['abstract', 'introduction', 'methods']
    
    for section in sections_to_generate:
        print(f"\nGenerating {section}...")
        section_content = generate_section(final_proposal, field, sub_field, relevant_papers, available_tools, section, sections, max_iterations, previous_sections)
        # full_paper += section_content
        # previous_sections[section] = section_content
        with open(f'tmp/write_up/{section}.md', 'w', encoding='utf-8') as f:
            f.write(section_content)
    

    # After repositories are found:
    downloaded_data = download_osf_data()
    print(downloaded_data)

    meta_data = analyze_downloaded_files(download_report_path='tmp/analysis/data/download_report.json')
    
    folder_Tree = display_folder_tree("tmp/")

    analysis_script = generate_analysis_script(
        folder_structure=folder_Tree,
        proposal=final_proposal,
        research_area=field,
        data_description=meta_data, 
        available_tools=available_tools
    )

    run_analysis_script(venv=VENV_PATH, max_retries=3)

    # Parse results and generate the results section
    results = parse_analysis_results()

    # Read the saved proposal, can be deleted later
    with open('tmp/proposals/proposal.md', 'r', encoding='utf-8') as f:
        proposal = f.read()
    # Read the saved relevant_papers, can be deleted later
    with open('tmp/proposals/relevant_papers.md', 'r', encoding='utf-8') as f:
        relevant_papers = f.read()

    results_section = generate_results_section(results, proposal=proposal)
    with open(f'tmp/write_up/results.md', 'w', encoding='utf-8') as f:
        f.write(results_section)

    # UNETHICAL?, but due to limitation of available data
    sections_to_rewrite = ['abstract', 'introduction', 'methods']

    # DRAFT SECTION
    for i in range(DRAFT_REFINEMENT_ITERATIONS):
        print(f"\nIteration {i+1}/{DRAFT_REFINEMENT_ITERATIONS} of draft refinement")
        whole_paper_integrated = ""
        
        # load sections to rewrite
        for section in sections_to_rewrite:
            section_path = f"tmp/write_up/{section}.md"
            with open(section_path, 'r', encoding='utf-8') as f:
                section_content = f.read()
                whole_paper_integrated += section_content

            print(f"\nRewriting {section} with results context...")
            adjusted_section_content = re_generate_section(
                field,
                sub_field, 
                section,
                section_content,
                results_section,
                relevant_papers,
                max_iterations
            )
            
            # Write to next iteration folder
            os.makedirs(f"tmp/write_up", exist_ok=True)
            with open(f"tmp/write_up/{section}.md", 'w', encoding='utf-8') as f:
                f.write(adjusted_section_content)

        # find more relevant papers
        additional_papers = re_paper_finder_agent(whole_paper_integrated)

        # Append new papers with iteration number
        with open('tmp/proposals/relevant_papers.md', 'a', encoding='utf-8') as f:
            f.write(f"\n\n### Additional Relevant Papers - Iteration {i+1}\n")
            f.write(additional_papers)
            
        # Update relevant_papers for next iteration
        relevant_papers += additional_papers
    
    # adding results section to the paper
    whole_paper_integrated += results_section

    discussion_section = generate_discussion_section(whole_paper_integrated)
    with open(f'tmp/write_up/discussion.md', 'w', encoding='utf-8') as f:
        f.write(discussion_section)

    whole_paper_integrated += discussion_section
    
    # Generate the conclusion section
    conclusion_section = generate_conclusion_section(whole_paper_integrated)
    with open(f'tmp/write_up/conclusion.md', 'w', encoding='utf-8') as f:
        f.write(conclusion_section)

    # find a suitable title
    title = generate_title(whole_paper_integrated)

    # come up with a suitable journal
    journal = generate_journal()

    with open(f'tmp/write_up/title.md', 'w', encoding='utf-8') as f:
        f.write(title)
        # After generating the journal recommendation
        format_requirements = get_journal_format_requirements(journal)
        citation_requirements = get_journal_citation_requirements(journal)

        whole_paper_integrated += conclusion_section

        # Generate the final paper with proper formatting
        final_paper = generate_final_paper(title, whole_paper_integrated, journal, format_requirements, citation_requirements)

    # Save the formatted paper
    with open(f'tmp/write_up/final_paper.md', 'w', encoding='utf-8') as f:
        f.write(final_paper)
    
    # Convert the Markdown to PDF
    subprocess.run(['pandoc', '-s', '-o', 'tmp/write_up/final_paper.pdf', 'tmp/write_up/final_paper.md'])

    print("DONE")
    print("The paper is ready to be submitted to: " + journal)

if __name__ == "__main__":
    main()

