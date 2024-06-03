import shelve
from datetime import datetime
from typing import List, Dict, Tuple

class Plan:
    def __init__(self, keywords: List[str], prompt: str, description: str, participants: Dict[str, Dict[str, bool]],
                 executable_steps: List[Dict[str, bool]], status: str, date_range: Tuple):
        self.keywords = keywords
        self.prompt = prompt
        self.description = description
        self.participants = participants
        self.executable_steps = executable_steps
        self.status = status
        self.date_range = date_range


def add_plan(plan_id, plan):
    with shelve.open('plans_db', writeback=True) as db:
        db[plan_id] = plan

def update_plan(plan_id, updates):
    with shelve.open('plans_db', writeback=True) as db:
        if plan_id in db:
            for key, value in updates.items():
                setattr(db[plan_id], key, value)

def get_plan(plan_id):
    with shelve.open('plans_db') as db:
        return db.get(plan_id)

def delete_plan(plan_id):
    with shelve.open('plans_db', writeback=True) as db:
        if plan_id in db:
            del db[plan_id]

def find_plans_by_criteria(user_id=None, status=None, start_date=None, end_date=None):
    with shelve.open('plans_db') as db:
        result = []
        for plan_id, plan in db.items():
            if user_id and user_id not in plan.participants:
                continue
            if status and plan.status != status:
                continue
            if start_date and (plan.date_range[0] < start_date or plan.date_range[1] > end_date):
                continue
            result.append((plan_id, plan))
        return result

if __name__ == '__main__':
    # Example usage
    plan1 = Plan(
        keywords=["cloud", "migration"],
        prompt="Discuss steps for cloud migration",
        description="Discuss steps for cloud migration",
        participants={"Alice": {"id": "001", "messaged": False, "participating": True}},
        executable_steps=[{"url": "http://api.example.com/execute", "executed": False}],
        status="pending",
        date_range=(datetime(2023, 1, 1), datetime(2023, 1, 31))
    )
    add_plan("001", plan1)
    fetched_plan = get_plan("001")
    print(fetched_plan.prompt)  # Access attribute of the plan object
