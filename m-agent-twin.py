import os.path
import json
import pytz
from datetime import datetime
import time
from openai import OpenAI
from calendar_package import list_events, add_calendar_event, update_or_cancel_event
#from internet_package import search_internet
from events_package import query_ticketmaster_events
from thread_store import store_thread, check_if_thread_exists, get_all_threads
from file_store import store_file, check_if_file_exists
import pprint
import argparse
import uuid
import random

from typing import List, Dict, Tuple

from plans_package import (
    Plan,
    add_plan,
    update_plan,
    get_plan,
    delete_plan,
    find_plans_by_criteria,
    create_user_keywords,
    create_plan_prompt,
    create_plan_description
)


# flask API
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# without arguments sets this header to * by default, which is allow all origins
CORS(app)


from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# --------------------------------------------------------------
# Upload file
# --------------------------------------------------------------
def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(file=open(path, "rb"), purpose="assistants")
    return file

def get_chat_response(user_input, model=os.environ['MODEL']):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content":"You are a digital twin who embodies the captured information about your human counterpart.   Your job is to answer questions as best as possible in the voice of your human counterpart based on information provided and without information fabrication.."},
                {"role": "user", "content":user_input}
            ]
        )

        # Access and print token usage information
        if "usage" in completion:
            print(f"Prompt text: {user_input}")
            print(f"Prompt tokens: {completion['usage']['prompt_tokens']}")
            print(f"Completion tokens: {completion['usage']['completion_tokens']}")
            print(f"Total tokens used: {completion['usage']['total_tokens']}")
        else:
            print("Token usage information is not available for this completion.")

        chat_response_text = completion.choices[0].message["content"]

        return chat_response_text

    except Exception as e:
        # API request exceptions
        return f"An error occurred: {str(e)}"

def create_plan_object(keywords: List[str], dates: Tuple, plan_prompt: str, plan_description: str,
                       participants_map: Dict[str, Dict[str, bool]] = {}, executable_steps: List[Dict[str, bool]] = [],
                       status: str = '') -> str:
    """
    Creates and returns a JSON string representing a plan with specified or default settings.
    """
    plan_dict = {
        "keywords": keywords,
        "prompt": plan_prompt,
        "description": plan_description,
        "participants": participants_map,
        "executable_steps": executable_steps,
        "status": status,
        "date_range": {"start_date": dates[0].strftime('%Y-%m-%d'), "end_date": dates[1].strftime('%Y-%m-%d')}
    }
    return json.dumps(plan_dict)

list_tools=[
    {"type": "retrieval"},
    {
        "type": "function",
        "function": {
            "name": "create_plan_object",
            "description": "Creates and returns a Plan as a JSON formatted string with specified attributes such as keywords, and a description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "dates": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "format": "date-time"},
                            "end_date": {"type": "string", "format": "date-time"}
                        },
                        "required": ["start_date", "end_date"]
                    },
                    "plan_prompt": {"type": "string"},
                    "plan_description": {"type": "string"},
                    # "participants_map": {
                    #     "type": "object",
                    #     "additionalProperties": {
                    #         "type": "object",
                    #         "properties": {
                    #             "can_edit": {"type": "boolean"},
                    #             "can_execute": {"type": "boolean"}
                    #         },
                    #         "required": ["can_edit", "can_execute"]
                    #     }
                    # },
                    # "executable_steps": {
                    #     "type": "array",
                    #     "items": {
                    #         "type": "object",
                    #         "properties": {
                    #             "step": {"type": "string"},
                    #             "completed": {"type": "boolean"}
                    #         },
                    #         "required": ["step", "completed"]
                    #     }
                    # },
                    # "status": {"type": "string"}
                },
                "required": ["keywords", "dates", "plan_prompt", "plan_description"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "query_ticketmaster_events",
            "description": "Queries Ticketmaster for sports, concert and theater events based on specified criteria like keyword, location, and date range, and returns relevant event data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "location": {"type": "string"},
                    "start_date": {"type": "string", "format": "date-time"},
                    "end_date": {"type": "string", "format": "date-time"}
                },
                "required": ["keyword", "location", "start_date", "end_date"]
            }
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "search_internet",
    #         "description": "Useful to search the internet for queries that need up to date information.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "query": {"type": "string"}
    #             },
    #             "required": ["query"]
    #         }
    #     }
    # },
    # {"type":"function",
    #                     "function":{
    #                         "name": "add_calendar_event",
    #                         "description": "Add an event to Google Calendar",
    #                         "parameters": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "event_summary": {"type": "string"},
    #                                 "event_location": {"type": "string"},
    #                                 "event_description": {"type": "string"},
    #                                 "start_time": {"type": "string"},
    #                                 "end_time": {"type": "string"},
    #                                 "start_time_zone": {"type": "string"},
    #                                 "end_time_zone": {"type": "string"},
    #                             },
    #                             "required": ["event_summary", "event_location", "event_description", "start_time", "end_time", "start_time_zone", "end_time_zone"],
    #                         }
    #                     }
    #                     },
    #                    {"type":"function",
    #                     "function": {
    #                         "name": "list_events",
    #                         "description": "List past and upcoming events from Google Calendar",
    #                         "parameters": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "calendar_id": {"type": "string"},
    #                                 "max_results": {"type": "integer"},
    #                                 "start_time": {"type": "string", "format": "date-time", "description": "Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"},
    #                                 "end_time": {"type": "string", "format": "date-time", "description": "End time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"},
    #                                 "timezone": {"type": "string", "description": "Timezone in which the start and end times are specified"}
    #                             },
    #                             "required": ["calendar_id", "max_results"],
    #                             "additionalProperties": True
    #                         }
    #                     }
    #                     },
    #                    {"type":"function",
    #                     "function":{
    #                         "name": "update_or_cancel_event",
    #                         "description": "Update or cancel an event in Google Calendar",
    #                         "parameters": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "calendar_id": {"type": "string"},
    #                                 "event_id": {"type": "string"},
    #                                 "update_body": {"type": "object"}
    #                             },
    #                             "required": ["calendar_id", "event_id"]
    #                         }
    #                     }
    #                     },
                       {"type":"function",
                        "function":{
                            "name": "get_chat_response",
                            "description": "Provide chat responses to questions about the digital twin.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_input": {"type": "string", "description": "User's query"},
                                    "model": {"type": "string", "description": "GPT model to use"},
                                },
                                "required": ["user_input"]
                            }
                        }
                        }]

#list_tools=[{"type": "retrieval"}]

# define dispatch table
function_dispatch_table = {
    # "search_internet" : search_internet,
    # "add_calendar_event" : add_calendar_event,
    # "list_events" : list_events,
    # "update_or_cancel_event" : update_or_cancel_event,
    "get_chat_response" : get_chat_response,
    "query_ticketmaster_events" : query_ticketmaster_events,
    "create_plan_object" : create_plan_object
}

#function_dispatch_table = {}

def create_or_retrieve_thread(lookup_id):
    """
    Creates a new thread or retrieves an existing one based on the lookup ID.
    Adds the user's input as a message to the thread.

    :param lookup_id: The lookup identifier for the thread.
    :return: The thread object.
    """

    print(f"Using thread lookup ID: {lookup_id}")

    thread_id = check_if_thread_exists(lookup_id)
    thread = None

    if thread_id is None:
        lookup_id, thread = create_new_thread()
        print(f"Created new Lookup ID {lookup_id} and Thread ID {thread.id}")
    else:
        thread = retrieve_existing_thread(thread_id, lookup_id)
        print(f"Using existing Lookup ID {lookup_id} and Thread ID {thread.id}")

    return lookup_id, thread

def create_new_thread():
    try:
        thread = client.beta.threads.create()
        lookup_id, thread_id = store_thread(None, thread.id)  # Store and get back the lookup_id and thread_id
        return lookup_id, thread
    except Exception as e:
        print(f"Failed to create new thread: {e}")
        return None, None  # Return None for both on failure


def retrieve_existing_thread(thread_id, lookup_id):
    print(f"Retrieving existing thread with lookupId {lookup_id}")
    try:
        return client.beta.threads.retrieve(thread_id)
    except Exception as e:
        print(f"Failed to retrieve existing thread ({thread_id}): {e}")
        return None

def add_message_to_thread(thread_id, user_input):
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
    except Exception as e:
        print(f"Failed to add message to thread: {e}")

    return message

def print_thread_messages(lookup_id):
    """
    Prints a thread's messages in a human-readable format with date and time information.

    Args:
       lookup_id (int): The unique identifier for the thread.

    Raises:
       ValueError: If the lookup_id is not a valid integer.

    Prints:
       - Each message in the thread, formatted as "[timestamp] role: message content".
       - Error messages if the thread is not found or cannot be retrieved.
    """

    thread_id = check_if_thread_exists(lookup_id)

    if thread_id is None:
        print(f"Thread with lookupId {lookup_id} not found.")
        return

    thread = retrieve_existing_thread(thread_id, lookup_id)

    if thread is None:
        print(f"Failed to retrieve thread with lookupId {lookup_id}.")
        return

    messages = client.beta.threads.messages.list(thread_id=thread.id)

    color_blue = "\033[94m"
    color_yellow = "\033[93m"
    color_reset = "\033[0m"
    color_alternate = True  # Start with True to use blue first

    message_list = []
    for message in reversed(messages.data):
        timestamp = message.created_at

        # Check the type of timestamp and convert accordingly
        if isinstance(timestamp, str):
            # If it's a string, assume it's in ISO format and convert
            formatted_time = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(timestamp, int) or isinstance(timestamp, float):
            # If it's an int or float, assume it's a Unix timestamp and convert
            formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        else:
            # If it's already a datetime object, format it directly
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Set the color based on the role of the message
        color = color_yellow if message.role == 'user' else color_blue

        formatted_message = f"{color}[{formatted_time}] {message.role}: {message.content[0].text.value}{color_reset}"
        message_list.append(formatted_message)

    return message_list

def print_thread_messages_no_formatting(lookup_id):
    """
    """

    thread_id = check_if_thread_exists(lookup_id)

    if thread_id is None:
        print(f"Thread with lookupId {lookup_id} not found.")
        return

    thread = retrieve_existing_thread(thread_id, lookup_id)

    if thread is None:
        print(f"Failed to retrieve thread with lookupId {lookup_id}.")
        return

    messages = client.beta.threads.messages.list(thread_id=thread.id)

    message_list = []
    for message in reversed(messages.data):
        timestamp = message.created_at

        # Check the type of timestamp and convert accordingly
        if isinstance(timestamp, str):
            # If it's a string, assume it's in ISO format and convert
            formatted_time = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(timestamp, int) or isinstance(timestamp, float):
            # If it's an int or float, assume it's a Unix timestamp and convert
            formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        else:
            # If it's already a datetime object, format it directly
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")


        # Remove terminal color formatting since it's irrelevant for JSON output
        message_list.append({
            "type": "text",
            "text": message.content[0].text.value,
            "date": formatted_time,
            "role": message.role  # Include the role directly
        })

    return message_list

def get_upload_file_ids(upload_files=[]):
    file_ids = []
    file_dict = {}  # Initialize an empty dictionary to store file_ids and corresponding file_names

    if upload_files:
        # Check for 'retrieval' or 'code_interpreter' in list_tools if upload_files is not empty
        if not any(tool['type'] in ['retrieval', 'code_interpreter'] for tool in list_tools):
            raise ValueError("Files are only supported if 'retrieval' or 'code_interpreter' tools are enabled.")

        # Iterate through the upload_files list
        for file_path in upload_files:
            file_name = os.path.basename(file_path)  # Get the base name of the file

            # Use the package function to check if the file name already exists in the database
            existing_file_id = check_if_file_exists(file_name)
            if existing_file_id:
                # Retrieve the existing file ID and append to the list
                file_ids.append(existing_file_id)
                file_dict[existing_file_id] = file_name  # Update the dictionary
                print(f"File {file_name} already exists. Using stored file ID.")
            elif os.path.isfile(file_path):
                # Upload the file and retrieve the file id
                file = upload_file(file_path)
                # Use the package function to store the new file ID in the database
                new_file_id = store_file(file_name, file.id)
                if new_file_id:
                    # Append the file id to the file_ids list
                    file_ids.append(new_file_id)
                    file_dict[new_file_id] = file_name  # Update the dictionary
                    print(f"File {file_name} does not exist in db. Added file to db with new id {new_file_id}.")
            else:
                # Raise an error if the file does not exist
                raise FileNotFoundError(f"The file {file_path} does not exist.")

    return file_ids, file_dict

def retrieve_or_create_assistant(assistant_id, llm_instructions, list_tools=[], file_ids=[]):

    # only upload files if it's a new assistant
    if assistant_id:
        return client.beta.assistants.retrieve(assistant_id)
    else:
        return client.beta.assistants.create(
            name="ParallelFunction",
            instructions=llm_instructions,
            model=os.environ['MODEL'],
            tools=list_tools,
            file_ids=file_ids,
        )


def get_current_time_and_timezone(timezone_config):
    if not timezone_config:
        raise ValueError("Timezone configuration is not defined.")

    try:
        my_timezone = pytz.timezone(timezone_config)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"The provided timezone '{timezone_config}' is not recognized.")

    my_time = datetime.now(my_timezone).strftime('%Y-%m-%d')
    return my_time, my_timezone

def create_run_for_assistant(assistant_id, thread_id):
    return client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

def get_assistant_response(thread, run):
    """
    Monitors the status of an assistant's run and retrieves the response once completed.

    :param thread: The thread object associated with the run.
    :param run: The run object representing the assistant's execution.
    :return: The response from the completed run, if successful.

    The function performs the following actions:
    1. Continuously checks the status of the run in a loop.
    2. If the run is completed, it processes the completed run to retrieve the response.
    3. If the run requires additional action, it processes the required actions.
    4. If the run is still in progress, it waits for a specified time before rechecking.

    The function exits the loop and returns the response when the run is completed. In cases where the run requires
    action, it triggers appropriate processes to handle those actions. The function employs a delay between each status
    check to avoid overwhelming the server with requests.
    """
    while True:
        time.sleep(5)
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run_status.status == "completed":
            print(f"Run status is completed; Run ID: {run.id}, Thread ID: {thread.id}")

            print_token_usage(run_status)

            return process_completed_run(thread)

        elif run_status.status == "requires_action":
            print(f"Run status is requires action; Run ID: {run.id}, Thread ID: {thread.id}")
            process_required_action(run_status, thread, run)

        else:
            print("Waiting for the Assistant to process...")

def print_token_usage(run_status):
    if hasattr(run_status, 'usage'):
        print(f"Usage Details: {run_status.usage}")
    else:
        print("No usage details are available.")


def process_completed_run(thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages.data:
        if msg.role == "assistant":
            # Prepare a dictionary with various attributes of the message
            response_info = {
                "role": msg.role,
                "response": msg.content[0].text.value,
                "message_id": msg.id,
                "created_at": msg.created_at
            }
            # break and return on first match
            return response_info
    return {}  # Return an empty dictionary if no assistant message is found


def process_required_action(run_status, thread, run):
    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
    tool_calls_output, tools_output = process_tool_calls(required_actions)

    print(f"{tool_calls_output}")
    submit_tool_outputs(thread, run, tools_output)

def process_tool_calls(required_actions):
    tool_calls_output = {'tool_calls': []}
    tools_output = []

    for action in required_actions["tool_calls"]:
        tool_call, tool_output = process_single_tool_call(action)
        tool_calls_output['tool_calls'].append(tool_call)
        tools_output.append(tool_output)

    return tool_calls_output, tools_output

def process_single_tool_call(action):
    func_name = action["function"]["name"]
    arguments = json.loads(action["function"]["arguments"]) if isinstance(action["function"]["arguments"], str) else action["function"]["arguments"]

    tool_call = {
        'id': action['id'],
        'function': {'arguments': arguments, 'name': func_name},
        'type': 'function'
    }

    func = function_dispatch_table.get(func_name)
    if func:
        result = func(**arguments)
        output = json.dumps(result) if not isinstance(result, str) else result
    else:
        print(f"Function {func_name} not found")
        output = None

    tool_output = {"tool_call_id": action["id"], "output": output} if output else None
    return tool_call, tool_output

def submit_tool_outputs(thread, run, tools_output):
    if tools_output:
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tools_output
        )

def process_user_request(
        user_input,
        llm_instructions=None,
        assistant_id=None,
        file_ids=[],
        thread_lookup_id=None
):
    """
    Processes a user's request by interacting with an OpenAI assistant. It manages the creation or retrieval of a thread,
    sends the user's input to the assistant, and returns the assistant's response.

    :param user_input: The input provided by the user. This is mandatory.
    :param llm_instructions: Specific instructions or parameters for the LLM (Large Language Model), default is None.
    :param assistant_id: The ID of an existing assistant. If None, a default or new assistant may be created, default is None.
    :param file_ids: A list of file identifiers if files are to be used in processing the request, default is None.
    :param thread_lookup_id: The lookup identifier for the thread if an existing thread needs to be retrieved, default is None.

    :return:  A dictionary containing details of the assistant's response, including role, response content, message ID, and timestamps. Returns an empty dictionary if no assistant message is found.

    This function encapsulates the full process of handling a user request:
    1. Creating an assistant (if 'assistant_id' is provided, use the existing assistant).
    2. Creating a thread (or retrieving an existing one) based on 'thread_lookup_id'.
    3. Adding the user's message to the thread.
    4. Creating a run from the assistant and the thread.
    5. Retrieving the response from the assistant.

    If any step in the process fails, the function captures the exception, logs the error, and returns None.
    """
    try:

        # 1. Create assistant
        try:

            assistant = retrieve_or_create_assistant(assistant_id, llm_instructions, list_tools=list_tools, file_ids=file_ids)
            print(f"Assistant ID: {assistant.id}")

        except Exception as e:
            print(f"Error in retrieve_or_create_assistant: {e}")

        # 2. Creating a thread (or retrieving an existing one) based on the 'thread_lookup_id'.
        lookup_id, thread = create_or_retrieve_thread(thread_lookup_id)
        if thread is None:
            raise Exception("Failed to create thread.")

        # 3. Add message to thread
        message = add_message_to_thread(thread.id, user_input)

        if message is None:
            raise Exception("Failed to add message to thread.")
        else:
            print(f"Added message to thread with message ID: {message.id}")

        # 4. Create run from assistant and thread
        try:
            run = create_run_for_assistant(assistant.id, thread.id)
            print(f"Created run ID: {run.id}")
        except Exception as e:
            print(f"Error in create_run_for_assistant: {e}")
            return None

        if run is None:
            raise Exception("Failed to create and run assistant.")

        # begin assistant debug data collection
        assistant_info = {
            "id": getattr(assistant, "id", None),
            "model": getattr(assistant, "model", None),
            "instructions": getattr(assistant, "instructions", None)
        }

        # For lists, retrieve the entire list instead of just the type name
        file_ids = getattr(assistant, "file_ids", [])
        # Serialize lists as JSON strings or use another appropriate representation
        assistant_info["file_ids"] = json.dumps(file_ids)


        response_info = get_assistant_response(thread, run)
        from pprint import pprint
        print("response info:")
        pprint(response_info)

        # # Create the debug dictionary
        # debug_info = {
        #     "thread_lookup_id": lookup_id,
        #     "thread_id": thread.id,
        #     "run_id": run.id,
        #     "assistant_details_json": json.dumps(assistant_info, indent=2)
        # }
        #
        #
        # # Adding the debug dictionary to response_info
        # response_info['debug'] = debug_info

        # 5. Retrieving the response from the assistant.
        return response_info

    except Exception as e:
        print(f"Error in process_user_request: {e}")
        return None


def main():
    # thread_lookup_id = 129
    # assistant_id = "asst_1Jta4nfQ9g9PHPTNSHAu213g"  # Replace with a valid assistant_id if needed
    thread_lookup_id = None
    assistant_id = None

    my_time, my_timezone = get_current_time_and_timezone(os.environ['TIMEZONE'])
    instructions=f"As Alexandra Hamilton's personal AI assistant, you have access to her detailed profile and preferences through a JSON file. Your role includes maintaining her health, organization, and social connections. Today's date is {my_time}, and the timezone is {my_timezone}. Utilize this information to effectively manage her schedule, suggest healthy routines, and foster meaningful interactions with her friends and family."

    upload_files = ["./character_Alexandra_Hamilton_2024_04_17_v1.json"]

    while True:
        user_input = get_user_input()

        if user_input == 'exit':
            exit_program()
        elif user_input.startswith('print thread'):
            # Extract lookup_id from the user input
            parts = user_input.split()
            if len(parts) == 3 and parts[1] == 'thread':
                try:
                    lookup_id = int(parts[2])
                    formatted_messages = print_thread_messages(lookup_id)  # Call the print_thread function
                    for formatted_message in formatted_messages:
                        print(formatted_message)
                    break  # Exit the program after printing the thread
                except ValueError:
                    print("Invalid lookup_id. Please enter a numeric lookup_id.")
            else:
                print("Invalid command. Use 'print thread [lookup_id]' to print a thread.")
        else:
            file_ids, file_dict = get_upload_file_ids(upload_files=upload_files)

            # Print file_dict in a readable format
            import json
            print(json.dumps(file_dict, indent=4))

            response_info = process_user_request(
                user_input=user_input,
                llm_instructions=instructions,
                assistant_id=assistant_id,
                file_ids=file_ids,
                thread_lookup_id=thread_lookup_id
            )
            print(f"Role: {response_info['role']}, Created At: {response_info['created_at']}, Response: {response_info['response']}")


# API Endpoints

# API ENDPOINTS - THREADS BEGIN

@app.route('/threads_get_all', methods=['GET'])
def threads_get_all():
    all_threads = get_all_threads()
    return jsonify(all_threads)

@app.route('/thread_create', methods=['POST'])
def thread_create_api():
    lookup_id, thread = create_new_thread()
    if lookup_id is None or thread.id is None:
        return jsonify({"error": "Failed to create new thread"}), 500

    return jsonify({
        "message": "Thread created successfully",
        "lookup_id": lookup_id,
        "thread_id": thread.id
    })


@app.route('/thread_messages_get', methods=['GET'])
def thread_messages_get():
    lookup_id = request.args.get('lookup_id')
    messages = print_thread_messages_no_formatting(lookup_id)
    return jsonify(messages)

# API ENDPOINTS - THREADS END

# API ENDPOINTS - FILES BEGIN

@app.route('/file_names_from_ids', methods=['POST'])
def file_names_from_ids():
    # Retrieve a list of filenames from the request JSON body
    upload_files = request.json.get('upload_files', [])

    # Call the function to get file IDs and the file dictionary
    file_ids, file_dict = get_upload_file_ids(upload_files)

    # Return the results as JSON
    return jsonify({
        "file_ids": file_ids,
        "file_dict": file_dict
    })


@app.route('/file_upload_ids_get', methods=['POST'])
def file_upload_ids_get():
    upload_files = request.json.get('upload_files', [])
    file_ids, file_dict = get_upload_file_ids(upload_files)
    return jsonify({"file_ids": file_ids, "file_dict": file_dict})

# API ENDPOINTS - FILES END

# API ENDPOINTS - GENERAL
@app.route('/process_request', methods=['POST'])
def process_request():
    user_input = request.json.get('user_input')
    llm_instructions = request.json.get('llm_instructions', None)
    assistant_id = request.json.get('assistant_id', None)
    file_ids = request.json.get('file_ids', [])
    thread_lookup_id = request.json.get('thread_lookup_id', None)

    my_time, my_timezone = get_current_time_and_timezone(os.environ['TIMEZONE'])
    llm_instructions=f"You are a personal AI assistant designed to support a user whose profile and preferences are detailed in a JSON file. It's {my_time} in the {my_timezone} timezone. Your tasks range from managing the user's calendar schedule, health, organizational needs, and social connections to engaging in casual conversations about their daily experiences."
    response = process_user_request(user_input, llm_instructions, assistant_id, file_ids, thread_lookup_id)
    return jsonify(response)


# API ENDPOINTS - PLANS BEGIN


@app.route('/plan_metadata', methods=['GET'])
def plan_metadata():
    """
    Generate a list of plan metadata objects which does not include the plan prompt or description.
    :return:
    """
    try:
        # Number of plans to generate
        num_plans = int(request.args.get('num_plans', 1))  # Default to 1 if not specified

        #  name mappings
        user_mappings = [
            {'user_id': '001', 'name': 'Aria'},
            {'user_id': '002', 'name': 'Bryson'},
            {'user_id': '003', 'name': 'Cassandra'},
            {'user_id': '004', 'name': 'Darian'},
            {'user_id': '005', 'name': 'Elowen'},
            {'user_id': '006', 'name': 'Fletcher'},
            {'user_id': '007', 'name': 'Gwendolyn'},
        ]


        # Dummy date range (hardcoded for now)
        date_range = {"start_date": "2024-05-01", "end_date": "2024-05-31"}

        # List to hold all plan metadata
        plans = []

        for _ in range(num_plans):
            # Generate keywords using a hypothetical function
            # also, use the same user_mappings for all plans for now

            # Randomly select two unique users from the user_mappings list
            users = random.sample(user_mappings, 2)
            user1, user2 = users

            # print("Users before function call:", user1, user2)
            user_mappings_new, aggregated_keywords = create_user_keywords([user1, user2])
            # print("Users after function call:", user1, user2)

            # Create a plan metadata object
            plan_metadata = {
                "users": user_mappings_new,
                "keywords": aggregated_keywords,
                "date_range": date_range
            }

            # Append to the list of plans
            plans.append(plan_metadata)

        # Return the list of plan metadata objects
        return jsonify(plans)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/plan_prompt', methods=['POST'])
def plan_prompt():
    """
    Generate a plan prompt from a list of keywords and a date range.
    :return:
    """
    data = request.json
    keywords = data['keywords']
    start_date = datetime.strptime(data['dates'][0], '%Y-%m-%d')
    end_date = datetime.strptime(data['dates'][1], '%Y-%m-%d')
    distance = data.get('distance', 'day trip')  # Defaulting to 'day trip' if distance is not provided
    plan_prompt = create_plan_prompt(keywords, (start_date, end_date), distance)
    # description = create_plan_description(plan_prompt)
    return jsonify({'description': plan_prompt})

@app.route('/plans_list', methods=['GET'])
def plans_list():
    """
    Search for plans by user ID, status, start date, and end date.
    :return:
    """
    # Retrieve query parameters
    user_id = request.args.get('user_id', None)
    status = request.args.get('status', None)
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)

    # Convert date strings to datetime objects if they are provided
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    # Use the function from the plans package to find plans
    plans = find_plans_by_criteria(user_id=user_id, status=status, start_date=start_date, end_date=end_date)

    # Convert plans data to a serializable format
    serialized_plans = [
        {
            'plan_id': plan_id,
            'keywords': plan.keywords,
            'prompt': plan.prompt,
            'description': plan.description,
            'participants': plan.participants,
            'executable_steps': plan.executable_steps,
            'status': plan.status,
            'date_range': [plan.date_range[0].strftime('%Y-%m-%d'), plan.date_range[1].strftime('%Y-%m-%d')]
        }
        for plan_id, plan in plans
    ]

    return jsonify(serialized_plans)


# API ENDPOINTS - PLANS END

# Function to list all routes
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f"[{arg}]"

        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(str(rule))
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {url}")
        output.append(line)

    for line in sorted(output):
        print(line)



def get_user_input():
    return input("Please enter your request (or type 'exit' or 'print thread'): ").lower()

def exit_program():
    print("Exiting the program.")
    exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the script in CLI, API mode or list routes.")
    parser.add_argument("--mode", choices=["cli", "api", "list_routes"], default="api",
                        help="Run mode: 'cli' for command line interface, 'api' for API, 'list_routes' to display routes. Default is 'api'.")

    args = parser.parse_args()

    if args.mode == "cli":
        main()
    elif args.mode == "api":
        app.run(debug=True)
    elif args.mode == "list_routes":
        list_routes()

