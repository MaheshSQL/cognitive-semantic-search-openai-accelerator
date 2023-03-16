import os
import json
import logging

import openai
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    """OpenAI request"""

    logging.info('Python HTTP trigger function has started processing a request.')

    # Extract text from request payload
    req_body = req.get_body().decode('utf-8')
    # logging.info(f'req_body:{req_body}')
    request = json.loads(req_body)
    # logging.info(f'request:{request}')
    text = request['values'][0]['data']['text']
    # logging.info(f'text:{text}')

    # Get OpenAI summary
    summary = get_summary(text)
    logging.info("Summary retrieved.")

    # Create the response object
    response_body = {
        "values": [
            {
                "recordId": request['values'][0]['recordId'],
                "data": {
                    "summary": summary
                },
                "errors": None,
                "warnings": None
            }
        ]
    }

    # logging.info(response_body)
    # Serialize the response object to JSON and return it
    response = func.HttpResponse(json.dumps(response_body))
    response.headers['Content-Type'] = 'application/json'
    
    logging.info('Python HTTP trigger function has completed processing a request.')

    return response


def get_summary(text):
    """Summarise the input using Azure OpenAI prompt completion"""

    openai.api_type = "azure"
    openai.api_base = os.environ["OPENAI_ENDPOINT"]
    openai.api_version = os.environ["OPENAI_API_VERSION"]
    openai.api_key = os.environ["AZURE_OPENAI_KEY"]

    response = openai.Completion.create(
    engine = os.environ["OPENAI_DEPLOYMENT_NAME"],
    prompt = f'{os.environ["OPENAI_PROMPT"]} {text}',
    temperature = 0.6,
    max_tokens = int(os.environ["OPENAI_MAX_TOKENS"]),
    top_p = 1,
    frequency_penalty = 0,
    presence_penalty = 0,
    best_of = 1,
    stop = None)

    if response.object == 'text_completion':
        if response['choices'][0]['finish_reason'] == 'stop':
            summary = response['choices'][0]['text']
        else:
            summary = None
    else:
        summary = None

    return summary
