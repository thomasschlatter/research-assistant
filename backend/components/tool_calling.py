import ollama
from components.tools import expression_evaluator_tool, weather_tool, wikipedia_tool
from constants.models import MODEL
from components.tools import expression_evaluator, wikipedia, weather_forecast

tool_history = []
def tool_calling(query):
    
    messages = [{'role': 'user', 'content': query}]

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=[expression_evaluator_tool, weather_tool, wikipedia_tool],
    )
    print(response['message'])
    
    messages.append(response['message'])

    if not response['message'].get('tool_calls'):
        print("The model didn't use the function. Its response was:")
        print(response['message']['content'])

    if response['message'].get('tool_calls'):
        available_functions = {
            'expression_evaluator' : expression_evaluator,
            'wikipedia' : wikipedia,
            'weather_forecast' : weather_forecast
        }
    if response['message'].get('tool_calls'):
        for tool in response['message']['tool_calls']:

            function_to_call = available_functions[tool['function']['name']]
            args = tool['function']['arguments'].values()
            function_response = function_to_call(*args)

            print("\nTool Response:\n", function_response)

            messages.append({'role': 'tool', 'content': function_response})

    final_response = ollama.chat(model='llama3.1', messages=messages)
    print("\nFinal Response:\n", final_response['message']['content'])

    return final_response['message']['content']
