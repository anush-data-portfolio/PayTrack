import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import random


def generate_punches(num_rows=100, start_date='2023-01-01', end_date='2024-01-31', hourly_rate=14.2, job_types=['cashier', 'stocker', 'manager']):
    """
    Generate fake punch data for a specified number of rows and date range.

    Parameters:
    - num_rows (int, optional): Number of rows to generate. Defaults to 100.
    - start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to '2023-01-01'.
    - end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to '2024-01-31'.
    - hourly_rate (float, optional): Hourly rate for the punches. Defaults to 14.2.
    - job_types (list, optional): List of job types. Defaults to ['cashier', 'stocker', 'manager'].

    Returns:
    pd.DataFrame: DataFrame containing fake punch data with columns 'date', 'punch_in', 'punch_out', 'hours_worked', 'type', 'rate'.
    """
    fake = Faker()
    random.seed(42)
    # date string into datetime object
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Generate fake data for the DataFrame
    data = {
        'date': [fake.date_between(start_date=start_date, end_date=end_date) for _ in range(num_rows)],
        'punch_in': [fake.time_object() for _ in range(num_rows)]
    }
    data['punch_in'] = [datetime.combine(datetime.min, time) for time in data['punch_in']]

    # Calculate punch_out based on punch_in and add some random hours worked
    data['punch_out'] = [time + timedelta(hours=random.randint(1, 6), minutes=random.randint(0, 60)) for time in data['punch_in']]
    # convert timedelta to datetime
    # data['punch_out'] = [datetime.combine(datetime.min, time) for time in data['punch_out']]

    # Calculate hours_worked
    data['hours_worked'] = [(punch_out - punch_in).total_seconds() / 3600 for punch_in, punch_out in zip(data['punch_in'], data['punch_out'])]

    # Filter out rows where hours_worked is greater than 6
    data = {key: [value[i] for i in range(len(data['date'])) if data['hours_worked'][i] <= 6] for key, value in data.items()}

    # Create DataFrame
    df = pd.DataFrame(data)

    # Add rate, type, and format columns


    job_types = ['cashier', 'stocker', 'manager']
    df['type'] = [random.choice(job_types) for _ in range(len(df))]
    df['rate'] = 14.2


    # Format date, punch_in, and punch_out columns
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['punch_in'] = df['punch_in'].apply(lambda x: x.strftime('%H:%M:%S.%f')[:-3])
    df['punch_out'] = df['punch_out'].apply(lambda x: x.strftime('%H:%M:%S.%f')[:-3])
    # convert them to datetime objects
    df['date'] = pd.to_datetime(df['date'])
    df['punch_in'] = pd.to_datetime(df['punch_in'])
    df['punch_out'] = pd.to_datetime(df['punch_out'])
    # sort the dataframe by date
    df = df.sort_values(by=['date'])
    return df
