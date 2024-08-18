def get_response_from_llm(
    msg,
    client,
    model,
    system_message,
    print_debug=False,
    msg_history=None,
    temperature=0.75,
):
    if msg_history is None:
        msg_history = []

    new_msg_history = msg_history + [{"role": "user", "content": msg}]

    response = client.chat(model='llama3.1', messages=[
                {"role": "system", "content": system_message},
                *new_msg_history,
            ],
            #temperature=temperature,
            #max_tokens=3000,
            #n=1,
            #stop=None,
            )
  
    new_msg_history = new_msg_history + [response['message']]

    return response['message']['content'], new_msg_history

