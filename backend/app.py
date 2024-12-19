from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import numexpr as ne
from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import ollama

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

expression_evaluator_tool = {
        'type': 'function',
        'function': {
          'name': 'expression_evaluator',
          'description': 'Evaluates a mathematical expression following the PEMDAS/BODMAS order of operations.',
          'parameters': {
            'type': 'object',
            'properties': {
              'expression': {
                'type': 'string',
                'description': 'The mathematical expression to evaluate. The expression can include integers, decimals, parentheses, and the operators +, -, *, and /.',
              }
            },
            'required': ['expression'],
          },
        },
      }

import numexpr as ne

def expression_evaluator(expression = ""):
    try:
        result = ne.evaluate(expression)
        return f"Answer to {expression} is {result}"
    except Exception as e:
        return str(e)

wikipedia_tool = {
        'type': 'function',
        'function': {
          'name': 'wikipedia',
          'description': 'A wrapper around Wikipedia. Useful for when you need to answer general questions about people, places, companies, facts, historical events, or other subjects. Input should be a search query.',
          'parameters': {
            'type': 'object',
            'properties': {
              'query': {
                'type': 'string',
                'description': 'query to look up on wikipedia',
              }
            },
            'required': ['query'],
          },
        },
      }

from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

weather_tool = {
      'type': 'function',
      'function': {
        'name': 'weather_forecast',
        'description': 'Get the current weather for a city.',
        'parameters': {
          'type': 'object',
          'properties': {
            'city': {
              'type': 'string',
              'description': 'The name of the city',
            },
          },
          'required': ['city'],
        },
      },
    }


import requests

def weather_forecast(city):
    # Open-Meteo API URL
    geocode_url = f"https://geocode.xyz/{city}?json=1"
    geocode_response = requests.get(geocode_url)
    if geocode_response.status_code == 200:
        geocode_data = geocode_response.json()
        latitude = geocode_data['latt']
        longitude = geocode_data['longt']
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            return f"Wather of {city} today: {weather_data['current_weather']}"
            
        else:
            return ""
    else:
        return ""

import ollama
tool_history = []
def tool_calling(query):
    
    messages = [{'role': 'user', 'content': query}]

    response = ollama.chat(
        model='llama3.1',
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

# Central LangChain handling route
@app.route('/langchain', methods=['POST','GET'])
def handle_langchain_request():
    print("Handling LangChain request")
    data = request.json
    query = data.get('query', '')
    print(f"Query: {query}")
    response = tool_calling(query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
