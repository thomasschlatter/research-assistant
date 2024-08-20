
statistician_prompt_existing_data = """Your goal is to come up with a suitable statistical method for the paper with the title: {title}.

The data of the experiment are as follows: 

{data}

You are given a total of up to {max_runs} runs to suggest a suitable statistical method for the data at hand. You do not need to use all {max_runs}.

You can then implement the next thing on your list."""

statistician_prompt_nonexisting_data = """Your goal is to come up with a suitable experiment for the paper with the title: {title}.

The idea of the experiment are as follows: 

{idea}

You are given a total of up to {max_runs} runs to suggest a suitable experimental method for the idea at hand. You do not need to use all {max_runs}.

You can then implement the next thing on your list."""


