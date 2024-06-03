from datetime import datetime
from typing import List, Dict, Tuple

from .plans_store import Plan, add_plan, update_plan, get_plan, delete_plan, find_plans_by_criteria


def create_user_keywords(user_mappings: List[Dict[str, str]]) -> List[Dict]:
    """
    Accepts a list of user_id/name mappings and assigns temporary keywords to each user.
    """
    single_day_outing_keywords = [
        "picnic", "hiking", "biking", "beach day", "park visit",
        "museum trip", "zoo visit", "botanical garden", "historical site", "local festival",
        "food tour", "farmers market", "art gallery", "fishing", "birdwatching",
        "kayaking", "canoeing", "river rafting", "outdoor concert", "sporting event",
        "wine tasting", "amusement park", "farm visit", "cultural event", "photography excursion",
        "shopping excursion", "food truck hopping", "nature walk", "city exploration", "scenic drive"
    ]

    import random  # Import random module to use random.sample()

    aggregated_keywords = set()  # Using a set to ensure uniqueness of keywords
    for user in user_mappings:
        user['keywords'] = random.sample(single_day_outing_keywords, 1)  # Randomly select one unique keywords
        aggregated_keywords.update(user['keywords'])  # Aggregate keywords for each user

    return user_mappings, list(aggregated_keywords)

def create_plan_prompt(keywords: List[str], dates: tuple, distance: str) -> str:
    """
    Formats keywords, dates, and distance into a plan prompt.

    :param keywords: List of keywords related to the travel plan.
    :param dates: Tuple of start and end dates (datetime objects).
    :param distance: Describes the type of travel based on distance (e.g., 'day trip', 'out-of-town').
    :return: A formatted string that includes all input parameters for a travel plan.
    """
    date_range = f"{dates[0].strftime('%Y-%m-%d')} to {dates[1].strftime('%Y-%m-%d')}"
    return f"Create and return a Plan as a JSON formatted string using available function calls based on a local travel idea for me using on the following keywords: {', '.join(keywords)}, for the dates {date_range}, and that is based on real scheduled events.."

def create_plan_description(plan_prompt: str) -> str:
    """
    Generates a plan description based on the plan prompt.
    Placeholder for LLM query functionality.
    """
    # Placeholder for LLM call
    # return llm_query(plan_prompt)
    return f"{plan_prompt}"




if __name__ == '__main__':
    # User mappings example
    user_mappings = [
        {'user_id': '001', 'name': 'Alice'},
        {'user_id': '002', 'name': 'Bob'},
        {'user_id': '003', 'name': 'Carol'}
    ]

    # Create user keywords
    enriched_users = create_user_keywords(user_mappings)
    print("Enriched User Mappings with Keywords:")
    for user in enriched_users:
        print(user)

    # Create a plan prompt
    keywords = ["travel", "Europe", "budget"]
    dates = (datetime(2024, 4, 1), datetime(2024, 4, 15))
    plan_prompt = create_plan_prompt(keywords, dates)
    print("\nGenerated Plan Prompt:")
    print(plan_prompt)

    # Create a plan description based on the prompt
    plan_description = create_plan_description(plan_prompt)
    print("\nGenerated Plan Description:")
    print(plan_description)

    # Create a plan object
    participants_map = {
        '001': {'messaged': False, 'participating': True},
        '002': {'messaged': True, 'participating': False},
        '003': {'messaged': False, 'participating': True}
    }
    executable_steps = [
        {'url': 'http://api.example.com/start', 'executed': False},
        {'url': 'http://api.example.com/finish', 'executed': False}
    ]
    status = 'pending'
    plan = create_plan_object(keywords, dates, plan_prompt, plan_description, participants_map, executable_steps, status)

    # Display the created plan details
    print("\nCreated Plan Object:")
    print(f"Keywords: {plan.keywords}")
    print(f"Prompt: {plan.prompt}")
    print(f"Description: {plan.description}")
    print(f"Participants: {plan.participants}")
    print(f"Executable Steps: {plan.executable_steps}")
    print(f"Status: {plan.status}")
    print(f"Date Range: {plan.date_range[0].strftime('%Y-%m-%d')} to {plan.date_range[1].strftime('%Y-%m-%d')}")
