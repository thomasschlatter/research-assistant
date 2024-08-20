import json
import os
import os.path as osp
import time
from typing import List, Dict, Union
import ollama
from ollama import Client
import requests
import backoff
from constants.prompts_brainstormer import idea_first_prompt, idea_reflection_prompt, novelty_system_msg, novelty_prompt
from constants.apis import S2_API_KEY
from components.llm import get_response_from_llm
from extraction import extract_json_between_markers

# GENERATE IDEAS
def generate_ideas(
    base_dir,
    client,
    model,
    skip_generation=False,
    max_num_generations=20,
    num_reflections=5,
):
    if skip_generation:
        # Load existing ideas from file
        try:
            with open(osp.join(base_dir, "ideas.json"), "r") as f:
                ideas = json.load(f)
            print("Loaded existing ideas:")
            for idea in ideas:
                print(idea)
            return ideas
        except FileNotFoundError:
            print("No existing ideas found. Generating new ideas.")
        except json.JSONDecodeError:
            print("Error decoding existing ideas. Generating new ideas.")

    idea_str_archive = []
    with open(osp.join(base_dir, "seed_ideas.json"), "r") as f:
        seed_ideas = json.load(f)
    for seed_idea in seed_ideas:
        idea_str_archive.append(json.dumps(seed_idea))

    with open(osp.join(base_dir, "experiment.py"), "r") as f:
        code = f.read()

    with open(osp.join(base_dir, "prompt.json"), "r") as f:
        prompt = json.load(f)

    idea_system_prompt = prompt["system"]

    for _ in range(max_num_generations):
        print()
        print(f"Generating idea {_ + 1}/{max_num_generations}")
        try:
            prev_ideas_string = "\n\n".join(idea_str_archive)

            msg_history = []
            print(f"Iteration 1/{num_reflections}")
            text, msg_history = get_response_from_llm(
                idea_first_prompt.format(
                    task_description=prompt["task_description"],
                    code=code,
                    prev_ideas_string=prev_ideas_string,
                    num_reflections=num_reflections,
                ),
                client=client,
                model=model,
                system_message=idea_system_prompt,
                msg_history=msg_history,
            )
            ## PARSE OUTPUT
            json_output = extract_json_between_markers(text)
            assert json_output is not None, "Failed to extract JSON from LLM output"
            print(json_output)

            # Iteratively improve task.
            if num_reflections > 1:
                for j in range(num_reflections - 1):
                    print(f"Iteration {j + 2}/{num_reflections}")
                    text, msg_history = get_response_from_llm(
                        idea_reflection_prompt.format(
                            current_round=j + 2, num_reflections=num_reflections
                        ),
                        client=client,
                        model=model,
                        system_message=idea_system_prompt,
                        msg_history=msg_history,
                    )
                    ## PARSE OUTPUT
                    json_output = extract_json_between_markers(text)
                    assert (
                        json_output is not None
                    ), "Failed to extract JSON from LLM output"
                    print(json_output)

                    if "I am done" in text:
                        print(f"Idea generation converged after {j + 2} iterations.")
                        break

            idea_str_archive.append(json.dumps(json_output))
        except Exception as e:
            print(f"Failed to generate idea: {e}")
            continue

    ## SAVE IDEAS
    ideas = []
    for idea_str in idea_str_archive:
        ideas.append(json.loads(idea_str))

    with open(osp.join(base_dir, "ideas.json"), "w") as f:
        json.dump(ideas, f, indent=4)

    return ideas


# GENERATE IDEAS OPEN-ENDED
def generate_next_idea(
    base_dir,
    client,
    model,
    prev_idea_archive=[],
    num_reflections=5,
    max_attempts=10,
):
    idea_archive = prev_idea_archive
    original_archive_size = len(idea_archive)

    print(f"Generating idea {original_archive_size + 1}")

    if len(prev_idea_archive) == 0:
        print(f"First iteration, taking seed ideas")
        # seed the archive on the first run with pre-existing ideas
        with open(osp.join(base_dir, "seed_ideas.json"), "r") as f:
            seed_ideas = json.load(f)
        for seed_idea in seed_ideas[:1]:
            idea_archive.append(seed_idea)
    else:
        with open(osp.join(base_dir, "experiment.py"), "r") as f:
            code = f.read()
        with open(osp.join(base_dir, "prompt.json"), "r") as f:
            prompt = json.load(f)
        idea_system_prompt = prompt["system"]

        for _ in range(max_attempts):
            try:
                idea_strings = []
                for idea in idea_archive:
                    idea_strings.append(json.dumps(idea))
                prev_ideas_string = "\n\n".join(idea_strings)

                msg_history = []
                print(f"Iteration 1/{num_reflections}")
                text, msg_history = get_response_from_llm(
                    idea_first_prompt.format(
                        task_description=prompt["task_description"],
                        code=code,
                        prev_ideas_string=prev_ideas_string,
                        num_reflections=num_reflections,
                    )
                    + """
Completed ideas have an additional "Score" field which indicates the assessment by an expert ML reviewer.
This is on a standard 1-10 ML conference scale.
Scores of 0 indicate the idea failed either during experimentation, writeup or reviewing.
""",
                    client=client,
                    model=model,
                    system_message=idea_system_prompt,
                    msg_history=msg_history,
                )
                ## PARSE OUTPUT
                json_output = extract_json_between_markers(text)
                assert json_output is not None, "Failed to extract JSON from LLM output"
                print(json_output)

                # Iteratively improve task.
                if num_reflections > 1:
                    for j in range(num_reflections - 1):
                        print(f"Iteration {j + 2}/{num_reflections}")
                        text, msg_history = get_response_from_llm(
                            idea_reflection_prompt.format(
                                current_round=j + 2, num_reflections=num_reflections
                            ),
                            client=client,
                            model=model,
                            system_message=idea_system_prompt,
                            msg_history=msg_history,
                        )
                        ## PARSE OUTPUT
                        json_output = extract_json_between_markers(text)
                        assert (
                            json_output is not None
                        ), "Failed to extract JSON from LLM output"
                        print(json_output)

                        if "I am done" in text:
                            print(
                                f"Idea generation converged after {j + 2} iterations."
                            )
                            break

                idea_archive.append(json_output)
                break
            except Exception as e:
                print(f"Failed to generate idea: {e}")
                continue

    ## SAVE IDEAS
    with open(osp.join(base_dir, "ideas.json"), "w") as f:
        json.dump(idea_archive, f, indent=4)

    return idea_archive


def on_backoff(details):
    print(
        f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries "
        f"calling function {details['target'].__name__} at {time.strftime('%X')}"
    )


@backoff.on_exception(
    backoff.expo, requests.exceptions.HTTPError, on_backoff=on_backoff
)
def search_for_papers(query, result_limit=10) -> Union[None, List[Dict]]:
    if not query:
        return None
    rsp = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        headers={"X-API-KEY": S2_API_KEY},
        params={
            "query": query,
            "limit": result_limit,
            "fields": "title,authors,venue,year,abstract,citationStyles,citationCount",
        },
    )
    print(f"Response Status Code: {rsp.status_code}")
    print(
        f"Response Content: {rsp.text[:500]}"
    )  # Print the first 500 characters of the response content
    rsp.raise_for_status()
    results = rsp.json()
    total = results["total"]
    time.sleep(1.0)
    if not total:
        return None

    papers = results["data"]
    return papers



def check_idea_novelty(
    ideas,
    base_dir,
    client,
    model,
    max_num_iterations=10,
):
    with open(osp.join(base_dir, "experiment.py"), "r") as f:
        code = f.read()
    with open(osp.join(base_dir, "prompt.json"), "r") as f:
        prompt = json.load(f)
        task_description = prompt["task_description"]

    for idx, idea in enumerate(ideas):
        if "novel" in idea:
            print(f"Skipping idea {idx}, already checked.")
            continue

        print(f"\nChecking novelty of idea {idx}: {idea['Name']}")

        novel = False
        msg_history = []
        papers_str = ""

        for j in range(max_num_iterations):
            try:
                text, msg_history = get_response_from_llm(
                    novelty_prompt.format(
                        current_round=j + 1,
                        num_rounds=max_num_iterations,
                        idea=idea,
                        last_query_results=papers_str,
                    ),
                    client=client,
                    model=model,
                    system_message=novelty_system_msg.format(
                        num_rounds=max_num_iterations,
                        task_description=task_description,
                        code=code,
                    ),
                    msg_history=msg_history,
                )
                if "decision made: novel" in text.lower():
                    print("Decision made: novel after round", j)
                    novel = True
                    break
                if "decision made: not novel" in text.lower():
                    print("Decision made: not novel after round", j)
                    break

                ## PARSE OUTPUT
                json_output = extract_json_between_markers(text)
                assert json_output is not None, "Failed to extract JSON from LLM output"

                ## SEARCH FOR PAPERS
                query = json_output["Query"]
                papers = search_for_papers(query, result_limit=10)
                if papers is None:
                    papers_str = "No papers found."

                paper_strings = []
                for i, paper in enumerate(papers):
                    paper_strings.append(
                        """{i}: {title}. {authors}. {venue}, {year}.\nNumber of citations: {cites}\nAbstract: {abstract}""".format(
                            i=i,
                            title=paper["title"],
                            authors=paper["authors"],
                            venue=paper["venue"],
                            year=paper["year"],
                            cites=paper["citationCount"],
                            abstract=paper["abstract"],
                        )
                    )
                papers_str = "\n\n".join(paper_strings)

            except Exception as e:
                print(f"Error: {e}")
                continue

        idea["novel"] = novel

    # Save results to JSON file
    results_file = osp.join(base_dir, "ideas.json")
    with open(results_file, "w") as f:
        json.dump(ideas, f, indent=4)

    return ideas


if __name__ == "__main__":
    MAX_NUM_GENERATIONS = 32
    NUM_REFLECTIONS = 5
    import argparse

    parser = argparse.ArgumentParser(description="Generate AI scientist ideas")
    # add type of experiment (nanoGPT, Boston, etc.)
    parser.add_argument(
        "--experiment",
        type=str,
        default="nanoGPT",
        help="Experiment to run AI Scientist on.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.1-8b",
        choices=[
            "llama3.1-8b"
            "llama3.1-405b",
        ],
        help="Model to use for AI Scientist.",
    )
    parser.add_argument(
        "--skip-idea-generation",
        action="store_true",
        help="Skip idea generation and use existing ideas.",
    )
    parser.add_argument(
        "--check-novelty",
        action="store_true",
        help="Check novelty of ideas.",
    )
    args = parser.parse_args()

    print(f"Using OpenAI API with {args.model}.")
    client_model = "llama3.1"
    client = Client(host='http://localhost:11434')


    base_dir = osp.join("templates", args.experiment)
    results_dir = osp.join("results", args.experiment)
    ideas = generate_ideas(
        base_dir,
        client=client,
        model=client_model,
        skip_generation=args.skip_idea_generation,
        max_num_generations=MAX_NUM_GENERATIONS,
        num_reflections=NUM_REFLECTIONS,
    )
    if args.check_novelty:
        ideas = check_idea_novelty(
            ideas,
            base_dir=base_dir,
            client=client,
            model=client_model,
        )
