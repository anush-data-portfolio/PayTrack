from paytrack.models.schema import (
    User, Department, Timecard, Punch, Payrate
)
from paytrack.auth import Auth
from config import Config
import requests
from datetime import datetime
from datetime import timedelta
from datetime import date



class Paytrack:
    def __init__(self,is_today=False) -> None:
        """Initialize Paytrack object"""
        self.api_url: str = Config().API_URL
        self.user: User = None 
        self.session: requests.Session = None
        self.config: Config = Config()
        self.today =str(date.today())
        self.yesterday = str(date.today() - timedelta(days=1))
        self.is_today = is_today

    
    def __get_timecards(self, department:Department) -> dict:
        """Get the timecard"""
        if self.is_today:
            url = f"{self.config.TIMECARD}{department.employee_id}/{department.pay.pay_id}/{self.yesterday}/{self.today}"
        else:
            url = f"{self.config.TIMECARD}{department.employee_id}/{department.pay.pay_id}/{department.hire_date}/{self.today}"
        response = self.session.get(url)
        data = response.json()
        timecard = self.__parse_timecard(data, department)
        return timecard

        
    def __format_time(self, time: str) -> datetime.time:
        """Format the time"""
        if time == None:
            return None
        time = time[11:19]
        formatted_time = datetime.strptime(time, '%H:%M:%S')
        new_time = formatted_time - timedelta(hours=4)
        return new_time.time()  
    


    def __parse_timecard(self, data, department: Department) -> Timecard:
        punches = []
        for days in data:
            days = days['days']
            for day in days:
                if day['punches']:
                    for punch in day['punches']:
                        if punch['endreason']=='missedOut':
                            continue
                        intime = punch['in_datetime']
                        outtime = punch['out_datetime']
                        # time_worked = datetime.combine(date.today(), outtime) - datetime.combine(date.today(), intime)
                        punches.append(Punch(
                            date=day['day'].split('T')[0],
                            punch_in=str(intime),
                            punch_out=str(outtime),
                            # hours=str(time_worked).split()[-1]
                        ))
        timecard = Timecard(
            department_id=department.badge_id,
            punches=punches
        )
        return timecard

    def __parse_department_details(self, data) -> bool:
        """Set the department details"""
        data = data['list']
        if len(data) == 0:
            raise Exception("No department details found")
        first_name = data[0]['firstname']
        self.user.first_name = first_name
        jobs = []
        try:
            for dept in data:
                pay = Payrate(
                    pay_id = dept['payruleid'],
                    pay_rate = dept['basewagerate']
                )
                department = Department(
                    employee_id = dept['employeeid'],
                    name = dept['department_desc'],
                    badge_id = dept['badgenum'],
                    hire_date = dept['hiredate'].split('T')[0],
                    pay = pay
                )   
                timecard = self.__get_timecards(department)
                department.timecard = timecard
                jobs.append(department)
        except Exception as e:
            print(e)
            print("Error parsing department details")
            return False
        self.user.jobs = jobs
        return True    
    def __set_user_info(self) -> bool:
        """Set the user info"""
        try:
            self.user = User(
                username = Config().USERNAME,
                password = Config().PASSWORD
            )
        except:
            print("Error setting user info")
            return False
        return True
    
    def __get_user(self) -> User:
        """Return the user"""
        self.__set_user_info()
        return self.user

    def __get_session(self) -> requests.Session:
        print("Getting session")
        auth = Auth()
        session = auth.get_session(self.user)
        return session

    def __get_employee_info(self) -> dict:
        """Get the employee info"""
        endpoint = f"/rest/employeebyusername/{self.user.username}"
        response = self.session.get(self.api_url + endpoint)
        data = response.json()
        return data
    
    def __get_department_info(self) -> bool:
        Departmentinfo = self.__get_employee_info()
        data = self.__parse_department_details(Departmentinfo)
        if data:
            return True
        return False

    def get_pay_data(self):
        User = self.__get_user()
        self.session = self.__get_session()
        try:
            self.__get_department_info()
        except:
            print("Error setting department info")
            return False
        print(User)
        return User
