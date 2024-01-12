from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from model import Punches, Users, Departments, Employeedetails, Timecards, TimecardPunches
import streamlit as st
import pandas as pd



class DBHandler:
    """
    Database handler class for interacting with the PostgreSQL database.

    Attributes:
    - engine: SQLAlchemy database engine.
    - Session: Session class for creating database sessions.
    - Base: Declarative base class for defining database models.
    - session: Database session object.

    Methods:
    - __init__: Initialize the DBHandler object.
    - get_user: Retrieve user information based on username.
    - get_name: Retrieve the first name of the user based on username.
    - get_punchinfo: Process punch information and return it as a DataFrame.
    - get_punches: Retrieve punch information for a given username.

    Usage:
    db = DBHandler("postgresql://anush:password@localhost:5433/paytrack")
    user_info = db.get_user("username")
    user_name = db.get_name("username")
    punch_data = db.get_punches("username")
    """

    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
        self.session = self.Session()
    
    def get_user(self, username):
        """
        Retrieve user information based on username.

        Parameters:
        - username (str): User's username.

        Returns:
        model.Users: User information.
        """

        return self.session.query(Users).filter(Users.username == username).first()
    def get_name(self, username):
        """
        Retrieve the first name of the user based on username.

        Parameters:
        - username (str): User's username.

        Returns:
        str: User's first name.
        """
        user = self.get_user(username)
        return user.first_name
    
    def get_punchinfo(self, punch_list):
        """
        Process punch information and return it as a DataFrame.

        Parameters:
        - punch_list (list): List of punch information.

        Returns:
        pd.DataFrame: DataFrame containing processed punch information.
        """
        punches = []
        for data in punch_list:
            punch = data[0]
            department_name = data[1]
            temp_punch = {
                'date' : punch.punch_date,
                'punch_in' : punch.punch_in,
                'punch_out' : punch.punch_out,
                'hours_worked' : punch.hours_worked.seconds/3600,
                'rate' : punch.pay_rate,
                'type' : department_name,
            }
            punches.append(temp_punch)
        punches_df = pd.DataFrame(punches)
        return punches_df


    def get_punches(self, username):
        """
        Retrieve punch information for a given username.

        Parameters:
        - username (str): User's username.

        Returns:
        pd.DataFrame: DataFrame containing punch information.
        """

        user = self.get_user(username)
        user_id = user.id

        # Subquery to get department_ids associated with the user
        subquery = self.session.query(Employeedetails.department_id).filter(Employeedetails.user_id == user_id).subquery()

        timecards = self.session.query(Timecards).filter(Timecards.department_id.in_(subquery)).all()
        punch_list = []
        time_card_ids = [(timecard.id, timecard.department_id) for timecard in timecards]
        for data in time_card_ids:
            timecard_id = data[0]
            department_id = data[1]
            department_name = self.session.query(Departments.name).filter(Departments.id == department_id).first()[0]
            punch_ids = self.session.query(TimecardPunches.punch_id).filter(TimecardPunches.timecard_id == timecard_id).all()
            punch_ids = [punch_id[0] for punch_id in punch_ids]
            punch = self.session.query(Punches).filter(Punches.id.in_(punch_ids)).all()
            # add department name to the punch
            punch = [(punch, department_name) for punch in punch]
            punch_list.extend(punch)
        punches = self.get_punchinfo(punch_list)
        return punches           