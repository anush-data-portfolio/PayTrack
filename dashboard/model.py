from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, DateTime, Interval, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


# Punches Model
class Punches(Base):
    __tablename__ = 'punches'

    id = Column(Integer, primary_key=True)
    punch_date = Column(Date, nullable=False)
    punch_in = Column(Time, nullable=False)
    punch_out = Column(Time)
    hours_worked = Column(Interval, server_default="0 seconds", nullable=False)
    pay_rate = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('punch_date', 'punch_in', 'punch_out', name='punches_compound_key'),
    )

# Users Model
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

# Departments Model
class Departments(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

# Employeedetails Model
class Employeedetails(Base):
    __tablename__ = 'employeedetails'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    badge_number = Column(Integer, nullable=False)
    hire_date = Column(DateTime, nullable=False)

# Timecards Model
class Timecards(Base):
    __tablename__ = 'timecards'

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id'))

# Timecard_Punches Model
class TimecardPunches(Base):
    __tablename__ = 'timecard_punches'

    id = Column(Integer, primary_key=True)
    timecard_id = Column(Integer, ForeignKey('timecards.id'))
    punch_id = Column(Integer, ForeignKey('punches.id'))

