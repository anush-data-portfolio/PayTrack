# pydantic user schema

from typing import Optional
from datetime import date
from datetime import timedelta
from pydantic import BaseModel
from typing import List
from pydantic.dataclasses import dataclass

# inspector


class Punch(BaseModel):
    date: str
    punch_in: str
    punch_out: str

class Timecard(BaseModel):
    department_id: int
    punches: Optional[List[Punch]] = None

class Payrate(BaseModel):
    pay_id: int
    pay_rate: float

class Department(BaseModel):
    employee_id: int
    badge_id: int
    name: str
    pay: Payrate
    timecard: Optional[Timecard] = None
    hire_date: Optional[date] = None


class User(BaseModel):
    first_name: Optional[str] = None
    username: str
    password: str
    jobs: Optional[List[Department]] = None


