
import numexpr as ne
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

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
