# models/active_users_result_model.py
from pydantic import BaseModel
from datetime import date

class ActiveUsersResult(BaseModel):
    """
    Model for the result of the active playing and paying users query.
    """
    date: date
    users: int