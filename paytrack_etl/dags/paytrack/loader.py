
from paytrack.models.schema import User
from cryptography.fernet import Fernet



class Loader:
    def __init__(self, user) -> None:
        self.data: User = user
    
    def encrypt_password(self):
        """
        Encrypt the password using the key
        The key will be use to decrypt the password later
        """
        key = Fernet.generate_key()
        password = self.data.password
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode())
        return encrypted_password.decode()

    def __insert_user(self):
        """Insert user data into the database"""
        user = self.data
        query = f"""
            INSERT INTO users (username, password, first_name)
            VALUES ( '{user.username}', '{self.encrypt_password()}', '{user.first_name}');
        """ 
        return query

    def __insert_departments(self):
        """Insert department data into the database"""
        departments_query = ""
        for department in self.data.jobs:
            query = f"""
                INSERT INTO departments (name, id)
                VALUES ('{department.name}', {department.badge_id})
                ON CONFLICT (id) DO NOTHING;

            """
            departments_query += query
        return departments_query

    def __insert_employeedetails(self):
        """Insert employeedetails data into the database"""
        employeedetails_query = ""
        
        for department in self.data.jobs:
            user_id_query = f"""
                SELECT id FROM users
                WHERE username = '{self.data.username}'
            """
            department_id_query = f"""
                SELECT id FROM departments
                WHERE id = '{department.badge_id}'
            """
            
            query = f"""
                INSERT INTO employeedetails (user_id, department_id, hire_date, badge_number)
                VALUES (({user_id_query}), ({department_id_query}), '{department.hire_date}', {department.badge_id});
            """
            
            employeedetails_query += query
        
        return employeedetails_query

    def __insert_timecards(self):
        """Insert timecards data into the database"""
        timecards_query = ""
        user = self.data
        if user.jobs:
            for department in user.jobs:
                query = f"""
                    INSERT INTO timecards (department_id)
                    VALUES ({department.badge_id});
                """
                timecards_query += query
        return timecards_query
    
    def clearn_timestamp(self, timestamp):
        # remove 
        pass

    def __insert_punches(self, format_time=False):
        """Insert punches data into the database"""
        punches_query = ""
        user = self.data
        for department in user.jobs:
            for punch in department.timecard.punches:
                # convert date, punch_in, punch_out for postgres timestamp column
                date = punch.date
                punch_in = punch.punch_in
                punch_out = punch.punch_out

                # time_format = 'HH24:MI:SS.USZ' if format_time else ''
                if format_time:
                    # combine date with time
                    punch_in = date + "T" + punch_in
                    punch_out = date  + "T" + punch_out

                query = f"""
                    INSERT INTO punches (punch_date, punch_in, punch_out,pay_rate)
                    VALUES (
                        TO_TIMESTAMP('{date}', 'YYYY-MM-DD'),
                        TO_TIMESTAMP('{punch_in}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ'),
                        TO_TIMESTAMP('{punch_out}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ'),
                        {department.pay.pay_rate}
                    )
                    ON CONFLICT (punch_date, punch_in, punch_out)
                    DO UPDATE SET punch_in = EXCLUDED.punch_in, punch_out = EXCLUDED.punch_out;
                """
                punches_query += query

        return punches_query

    def __insert_timecard_punches(self, format_time=False):
        """Insert timecard_punches data into the database"""
        timecard_punches_query = ""
        user = self.data

        for department in user.jobs:
            for punch in department.timecard.punches:
                punch_date = punch.date
                punch_in = punch.punch_in
                punch_out = punch.punch_out

                if format_time :
                    punch_in = punch_date+"T"+ punch_in
                    punch_out = punch_date+"T"+ punch_out

                date_format = "'YYYY-MM-DD'" if format_time else "'YYYY-MM-DD'"

                timecard_id_query = f"""
                    SELECT id FROM timecards
                    WHERE department_id = {department.badge_id}
                """
                # time without timezone
                # punch_in = f"TO_TIMESTAMP('{punch_in}', {punch_in_format})"

                punch_id_query = f"""
                    SELECT DISTINCT id FROM punches
                    WHERE punch_date = TO_TIMESTAMP('{punch_date}', {date_format})::date
                    AND punch_in = TO_TIMESTAMP('{punch_in}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ')::time
                    AND punch_out = TO_TIMESTAMP('{punch_out}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ')::time
                """

                query = f"""
                    INSERT INTO timecard_punches (timecard_id, punch_id)
                    VALUES (({timecard_id_query}), ({punch_id_query}));
                """



                timecard_punches_query += query

        return timecard_punches_query

    def update_punches(self):
        punches = self.__insert_punches(format_time=True)
        timecard_punches = self.__insert_timecard_punches(format_time=True)
        query = f"""
            {punches}
            {timecard_punches}
        """
        return query

    def get_query(self):
        """Generate a single query to insert all data into the database"""
        user_query = self.__insert_user()
        departments_query = self.__insert_departments()
        employeedetails_query = self.__insert_employeedetails()
        timecards_query = self.__insert_timecards()
        punches_query = self.__insert_punches(format_time=False)
        timecard_punches_query = self.__insert_timecard_punches(format_time=False)

        query = f"""
            {user_query}
            {departments_query}
            {employeedetails_query}
            {timecards_query}
            {punches_query}
            {timecard_punches_query}
        """
        return query
