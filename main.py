import os
from components.citation_file_finder import download_citation_file, get_citation_styles, select_citation_style
from components.journal_format_finder_agent import get_journal_citation_requirements, get_journal_format_requirements
from components.paper_finder_agent import paper_finder_agent, re_paper_finder_agent
from components.proposal_agent import generate_research_proposal, refine_proposal_based_on_tools
from components.paper_writer_agent import generate_conclusion_section, generate_discussion_section, generate_final_paper, generate_section, generate_title, re_generate_section
from components.repository_finder_agent import repository_finder_agent
from components.reviewer_agent import review_proposal_feasibility
from components.statistician_agent import display_folder_tree, generate_analysis_script, generate_results_section, run_analysis_script
from components.helper_agents import analyze_downloaded_files, download_osf_data
from components.journal_finder_agent import generate_journal
from constants.available_tools import available_tools
from constants.other import AUTHOR_NAMES, DEFAULT_CITATION_STYLE, FIELD, FINAL_PROPOSAL_MAX_ITERATIONS, INITIAL_PROPOSAL_MAX_ITERATIONS, SECTION_CONTENT_MAX_ITERATIONS, ADJUSTED_SECTION_CONTENT_MAX_ITERATIONS, GENERATE_ANALYSIS_SCRIPT_MAX_RETRIES, NUMBER_OF_PAPERS_TO_EXTRACT, RE_NUMBER_OF_PAPERS_TO_EXTRACT, SUB_FIELD
from constants.paths import VENV_PATH
from constants.sections import sections
import subprocess

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    print(ABSOLUTE_PATH)
    print("==========================")
    print("Scientific Writer Assistant")
    print("==========================")
    
    field = FIELD
    sub_field = SUB_FIELD
    author_names = AUTHOR_NAMES

    # Clears the relevant papers file at startup
    papers_path = "tmp/citations/references.bib"
    with open(papers_path, 'w') as f:
        f.write("")

    # Create necessary directory for the analysis
    os.makedirs('tmp/analysis', exist_ok=True)
    
    # Create empty analysis.json
    with open('tmp/analysis/analysis.json', 'w') as f:
        f.write('{}')
    
    # Create empty analysis.py
    with open('tmp/analysis/analysis.py', 'w') as f:
        f.write('')

    ####################
    # PROPOSAL SECTION #
    ####################
    
    print(f"Finding papers for {field} - {sub_field}")

    # Collect related information
    relevant_papers = paper_finder_agent(field, sub_field, number_of_papers=NUMBER_OF_PAPERS_TO_EXTRACT)

    with open('tmp/citations/references.bib', 'w', encoding='utf-8') as f:
        f.write(relevant_papers)
    print(f"Generating proposal for {field} - {sub_field}")

    # Generate initial proposal
    initial_proposal = generate_research_proposal(field, sub_field, max_iterations=INITIAL_PROPOSAL_MAX_ITERATIONS)

    with open('tmp/proposals/proposal.md', 'w', encoding='utf-8') as f:
        f.write(initial_proposal)

    current_proposal = initial_proposal
    iteration = 0

    while iteration < FINAL_PROPOSAL_MAX_ITERATIONS:
        print(f"\nProposal refinement iteration {iteration + 1}/{FINAL_PROPOSAL_MAX_ITERATIONS}")

        relevant_repositories = repository_finder_agent(current_proposal, repos_needed=10)

        # Pass the previous review feedback to refine_proposal_based_on_tools
        refined_proposal = refine_proposal_based_on_tools(
            current_proposal, 
            field, 
            sub_field, 
            relevant_repositories, 
            available_tools, 
            relevant_papers,
            review_feedback if iteration > 0 else None  # Pass previous review feedback starting from second iteration
        )

        review_feedback = review_proposal_feasibility(refined_proposal, relevant_repositories, available_tools)
        print(f"\nReview feedback - Iteration {iteration + 1}:")
        print(review_feedback)

        # Save current iteration
        with open(f'tmp/proposals/final_proposal.md', 'w', encoding='utf-8') as f:
            f.write(refined_proposal)

        with open(f'tmp/proposals/final_review.md', 'w', encoding='utf-8') as f:
            f.write(review_feedback)

        current_proposal = refined_proposal
        iteration += 1

    if iteration == FINAL_PROPOSAL_MAX_ITERATIONS:
        print("Maximum iterations reached for revisions. Final proposal saved. Continuing to paper generation...")

    # =================================================

    # Load the final proposal
    with open('tmp/proposals/final_proposal.md', 'r', encoding='utf-8') as f:
        current_proposal = f.read()

    # Load the relevant papers
    with open('tmp/citations/references.bib', 'r', encoding='utf-8') as f:
        relevant_papers = f.read()

    previous_sections = {}
    # Generate sections up to methods
    sections_to_generate = ['abstract', 'introduction', 'methods']

    for section in sections_to_generate:
        print(f"\nGenerating {section}...")
        iteration = 0
        success = False

        while iteration < SECTION_CONTENT_MAX_ITERATIONS and not success:
            section_content, success = generate_section(
                current_proposal, 
                field, 
                sub_field, 
                relevant_papers, 
                available_tools, 
                section, 
                sections, 
                previous_sections
            )
    
            if success:
                with open(f'tmp/write_up/{section}.md', 'w', encoding='utf-8') as f:
                    f.write(section_content)
                previous_sections[section] = section_content
            else:
                print(f"Attempt {iteration + 1} failed, retrying...")
        
            iteration += 1

        if not success:
            print(f"Failed to generate {section} after {SECTION_CONTENT_MAX_ITERATIONS} attempts")
            exit()

    # After repositories are found:
    downloaded_data = download_osf_data()
    print(downloaded_data)

    meta_data = analyze_downloaded_files(download_report_path='tmp/analysis/data/download_report.json')
    
    folder_Tree = display_folder_tree("tmp/")

    analysis_script = generate_analysis_script(
        folder_structure=folder_Tree,
        proposal=current_proposal,
        research_area=field,
        data_description=meta_data, 
        available_tools=available_tools,
    )
    
    run_analysis_script(venv=VENV_PATH, max_retries=GENERATE_ANALYSIS_SCRIPT_MAX_RETRIES)

    import json
    # Parse results and generate the results section
    with open("tmp/analysis/analysis.json", 'r') as f:
                results = json.load(f)

    results_section = generate_results_section(results, proposal=current_proposal)
    with open(f'tmp/write_up/results.md', 'w', encoding='utf-8') as f:
        f.write(results_section)

    # UNETHICAL?, but due to limitation of available data
    sections_to_rewrite = ['abstract', 'introduction', 'methods']

    # REFINEMENT
    for i in range(ADJUSTED_SECTION_CONTENT_MAX_ITERATIONS):
        print(f"\nIteration {i+1}/{ADJUSTED_SECTION_CONTENT_MAX_ITERATIONS} of paper refinement")
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
                relevant_papers
            )
            
            # Write to next iteration folder
            os.makedirs(f"tmp/write_up", exist_ok=True)
            with open(f"tmp/write_up/{section}.md", 'w', encoding='utf-8') as f:
                f.write(adjusted_section_content)

        # find more relevant papers
        additional_papers = re_paper_finder_agent(whole_paper_integrated, RE_NUMBER_OF_PAPERS_TO_EXTRACT)

        # Append new papers with iteration number
        with open('tmp/citations/references.bib', 'a', encoding='utf-8') as f:
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
    journal = generate_journal(field, sub_field, title)

    with open(f'tmp/write_up/title.md', 'w', encoding='utf-8') as f:
        f.write(title)
        # After generating the journal recommendation
        format_requirements = get_journal_format_requirements(journal)
        citation_requirements = get_journal_citation_requirements(journal)

        whole_paper_integrated += conclusion_section

        # Generate the final paper with proper formatting
        final_paper = generate_final_paper(title, author_names, whole_paper_integrated, relevant_papers, journal, format_requirements, citation_requirements, absolute_path=ABSOLUTE_PATH)

    # Save the formatted paper
    with open(f'tmp/write_up/final_paper.md', 'w', encoding='utf-8') as f:
        f.write(final_paper)

    csl_files = get_citation_styles()

    try:
        style_file = select_citation_style(journal, csl_files)
    except Exception as e:
        print(f"Error selecting citation style: {e}")
        print("Using default style 'apa.csl'")
        style_file = DEFAULT_CITATION_STYLE

    # Download the selected citation style
    try:
        style_file = download_citation_file(style_file)
    except Exception as e:
        print(f"Error downloading citation style: {e}")
        print("Using default style specified in DEFAULT_CITATION_STYLE")
        style_file = f"tmp/citation/{DEFAULT_CITATION_STYLE}"

    # Convert the Markdown to PDF using Pandoc
    command = [
            "pandoc",
            "--verbose",
            "--citeproc",
            "-s", 'tmp/write_up/final_paper.md',
            "-o", 'tmp/write_up/final_paper.pdf',
            "--csl", style_file,
            "--bibliography", "tmp/citations/references.bib"
        ]
    subprocess.run(command, check=True, capture_output=True, text=True)

    print("DONE")
    print("The paper is ready to be submitted to: " + journal)

if __name__ == "__main__":
    main()

