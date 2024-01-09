from faker import Faker

import datetime
import pandas as pd
from datetime import timedelta
import numpy as np

def generate_punches(start_date, end_date):
    fake = Faker()
    # Generate random dates within the given date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize an empty list to store punch data
    punches = []

    for date in date_range:
        # Generate random number of punches for the day (up to 4 punches)
        num_punches = np.random.randint(1, 2)
        
        # Initialize work hours for the day
        daily_work_hours = 0
        
        # Generate punches for the day
        for _ in range(num_punches):
            # Generate random punch-in time
            punch_in = date + timedelta(hours=np.random.randint(8, 12), minutes=np.random.randint(0, 60))
            
            # Ensure punch-out time is at least 6 hours later than punch-in
            punch_out = punch_in + timedelta(hours=np.random.randint(1, 6), minutes=np.random.randint(0, 60))
            
            # Check if adding this punch exceeds 20 hours for the week
            if daily_work_hours + (punch_out - punch_in).total_seconds() / 3600 <= 20:
                # Update daily work hours
                daily_work_hours += (punch_out - punch_in).total_seconds() / 3600
                
                # Append punch data to the list
                punches.append([date, punch_in, punch_out, daily_work_hours])
    
    # Create DataFrame from the list of punches
    columns = ['date', 'punch_in', 'punch_out', 'hours_worked']
    df = pd.DataFrame(punches, columns=columns)
    
    return df