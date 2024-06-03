# README Script for using OpenAI's Assistants API with Integrated Personalized Profile via OpenAI Assistants API File Upload

## Overview:
This script uses OpenAI's Assistants API for function calling as well as managing threads and messages. It integrates with Google Calendar API to schedule events and employs GPT-4 to process natural language scheduling requests.

## Setup

Install Required Libraries:

Ensure you have the Google API Client Library for Python installed.

    pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client

Install pytz timezone library:
    
    pip install pytz

Install OpenAI client libraries:

    pip install openai

Install API client libraries:

    pip install Flask flask-cors

Install React libs 

    cd chat-app/
    npm install axios slick-carousel react-slick




## Usage
This script can be run in two modes: Command Line Interface (CLI) mode and API mode.

### CLI Mode
To run the script in CLI mode, use the following command:

    python m-agent-twin.py --mode cli


In CLI mode, the script will execute the functionality defined in the main() function.

### API Mode
To run the script as a web API, you can use the following command:

    python m-agent-twin.py --mode api

Alternatively, since API mode is the default, you can also start the API by simply running:

    python m-agent-twin.py

When running in API mode, the Flask server will start, and the API will be accessible at the default address:

    http://127.0.0.1:5000/

Visit this URL in your web browser or use a tool like curl or Postman to interact with the API.

    curl -X POST http://127.0.0.1:5000/process_request \
     -H "Content-Type: application/json" \
     -d '{
           "user_input": "What is the capital of France?",
           "llm_instructions": "Please provide detailed information",
           "assistant_id": "asst_1Jta4nfQ9g9PHPTNSHAu213g",
           "file_ids": ["file-aWJB3NOKHiJnfKgTyKrWgjo8"],
           "thread_lookup_id": "129"
         }'

    # create new assistant and new thread with no files
    curl -X POST http://127.0.0.1:5000/process_request \
     -H "Content-Type: application/json" \
     -d '{
           "user_input": "What is the capital of France?",
           "llm_instructions": "Please provide detailed information"
         }'

    curl -X POST http://127.0.0.1:5000/get_file_ids \
     -H "Content-Type: application/json" \
     -d '{"upload_files": ["./character_Alexandra_Hamilton_2024_04_17_v1.json"]}'

### Chat App

To run a React browser-based app on port 3000:

    cd chat-app
    npm start



The script interactively prompts for event scheduling commands (e.g., "Schedule a meeting with John on January 10 at 10 am") and processes these requests to add events to your Google Calendar.  The script considers information gathered from a personalized profile to provide more personalized responses.

Note: Ensure that you have the necessary permissions and correct calendar ID before running the script.