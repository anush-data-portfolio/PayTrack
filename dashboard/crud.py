from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from model import Punches, Users, Departments, Employeedetails, Timecards, TimecardPunches
import streamlit as st
import pandas as pd



class DBHandler:
    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
        self.session = self.Session()
    
    def get_user(self, username):
        return self.session.query(Users).filter(Users.username == username).first()
    def get_name(self, username):
        user = self.get_user(username)
        return user.first_name
    
    def get_punchinfo(self, punch_list):
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