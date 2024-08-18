from flask import Flask, request, jsonify
from flask_cors import CORS 
from components.generate_ideas import generate_ideas, check_idea_novelty
from components.extraction import extract_json_between_markers
from components.tool_calling import tool_calling
from components.llm import get_response_from_llm
from constants.prompts_brainstormer import idea_first_prompt, idea_reflection_prompt
import os.path as osp
import json

import ollama
from ollama import Client

app = Flask(__name__)
CORS(app) 

base_dir = 'skeletons/'
max_num_generations = 3
num_reflections = 3

# Central LangChain handling route
@app.route('/langchain', methods=['POST','GET'])
def handle_langchain_request():
    print("Handling LangChain request")
    data = request.json
    query = data.get('query', '')
    print(f"Query: {query}")
    response = tool_calling(query)
    return jsonify({'response': response})

@app.route('/get-ideas', methods=['POST','GET'])
def get_ideas():
    print("Getting ideas")
    #data = request.json
    #query = data.get('query', '')
    #print(f"Query: {query}")

    idea_str_archive = []
    with open(osp.join(base_dir, "seed_ideas.json"), "r") as f:
        seed_ideas = json.load(f)
    for seed_idea in seed_ideas:
        idea_str_archive.append(json.dumps(seed_idea))

    with open(osp.join(base_dir, "linguistics_experiment_data.csv"), "r") as f:
        code = f.read()

    with open(osp.join(base_dir, "prompt.json"), "r") as f:
        prompt = json.load(f)

    idea_system_prompt = prompt["system"]

    client_model = "meta-llama/llama-3.1-405b-instruct"
        
    client = Client(host='http://localhost:11434')

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
                model=client_model,
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
                        model=client_model,
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





    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=[expression_evaluator_tool, weather_tool, wikipedia_tool],
    )

    
    ideas = generate_ideas(
        base_dir,
        client=client,
        model=client_model,
        skip_generation=args.skip_idea_generation,
        max_num_generations=args.num_ideas,
        num_reflections=NUM_REFLECTIONS,
    )
    ideas = check_idea_novelty(
        ideas,
        base_dir=base_dir,
        client=client,
        model=client_model,
    )



    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
