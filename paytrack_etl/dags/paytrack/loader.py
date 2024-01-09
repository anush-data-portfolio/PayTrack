
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
                VALUES ('{department.name}', {department.badge_id});
            """
            departments_query += query
        return departments_query

    def __insert_paydetails(self):
        """Insert paydetails data into the database"""
        paydetails_query = ""
        for department in self.data.jobs:
            query = f"""
                INSERT INTO paydetails (id, pay_rate)
                VALUES ({department.pay.pay_id}, {department.pay.pay_rate});
            """
            paydetails_query += query
        return paydetails_query

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

    def __insert_punches(self,format_time=False):
        """Insert punches data into the database"""
        punches_query = ""
        user = self.data
        for department in user.jobs:
            for punch in department.timecard.punches:
                # convert date, punch_in, punch_out for postgres timestamp column
                date = punch.date
                punch_in = punch.punch_in
                punch_out = punch.punch_out

                if format_time:
                    query = f"""
                        INSERT INTO punches (punch_date, punch_in, punch_out)
                        VALUES (
                            TO_TIMESTAMP('{date}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ'),
                            TO_TIMESTAMP('{punch_in}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ'),
                            TO_TIMESTAMP('{punch_out}', 'YYYY-MM-DD"T"HH24:MI:SS.USZ')
                        )
                        ON CONFLICT (punch_date, punch_in, punch_out)
                        DO UPDATE SET punch_in = EXCLUDED.punch_in, punch_out = EXCLUDED.punch_out;
                    """
                else:
                    query = f"""
                        INSERT INTO punches (punch_date, punch_in, punch_out)
                        VALUES (
                            '{date}',
                            '{punch_in}',
                            '{punch_out}'
                        )
                        ON CONFLICT (punch_date, punch_in, punch_out)
                        DO UPDATE SET punch_in = EXCLUDED.punch_in, punch_out = EXCLUDED.punch_out;
                    """
                punches_query += query
        return punches_query




    def update_punches(self):
        punches = self.__insert_punches()
        return punches




    def get_query(self):
        """Generate a single query to insert all data into the database"""
        user_query = self.__insert_user()
        departments_query = self.__insert_departments()
        paydetails_query = self.__insert_paydetails()
        employeedetails_query = self.__insert_employeedetails()
        timecards_query = self.__insert_timecards()
        punches_query = self.__insert_punches(format_time=True)

        query = f"""
            {user_query}
            {departments_query}
            {paydetails_query}
            {employeedetails_query}
            {timecards_query}
            {punches_query}
        """
        return query
