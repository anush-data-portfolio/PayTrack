import datetime
import pandas as pd
from datetime import timedelta
import streamlit as st
from typing import List, Tuple
import plotly.express as px
import numpy as np


def display_title():
    temp_st = st
    temp_st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(6)
        {
            text-align: end;
        } 
    </style>
    """,unsafe_allow_html=True
)
    cols = [temp_st.columns(5)]
    with cols[0][0]:
        temp_st.title("📊 Paytrack")
    with cols[0][4]:
        # view the source code on the right end of col2
        temp_st.write("View the source code on Github")
        temp_st.link_button("Source Code", "github.com/anushkrishnav/paytrack-dashboard")
    
    


def set_page_config():
    st.set_page_config(
        page_title="PayTrack Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv('data/punches_data_sample.csv')
    data['date'] = pd.to_datetime(data['date'])
    return data

def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("Your Pay Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)

def calculate_hours_worked(data: pd.DataFrame) -> pd.DataFrame:
    data['punch_in'] = pd.to_datetime(data['punch_in'])
    data['punch_out'] = pd.to_datetime(data['punch_out'])
    data['hours_worked'] = data['punch_out'] - data['punch_in']
    data['hours_worked'] = data['hours_worked'].apply(lambda x: x.total_seconds() / 3600)
    return data

def calculate_week_id(df):
    '''give a date column in df, calculate the week id which is the week number in a year'''
    df['week_id'] = df['date'].apply(lambda x: x.isocalendar()[1])
    # convert the week id to an int
    df['week_id'] = df['week_id'].astype(int)
    return df

@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_money_earned = data['money_earned'].sum()
    # money earned for this week
    this_week = data[data['week_id'] == data['week_id'].max()]
    money_earned_this_week = this_week['money_earned'].sum()
    # hours worked for this week
    hours_worked_this_week = this_week['hours_worked'].sum()
    # hours remaining for this week
    hours_remaining_this_week = 20 - hours_worked_this_week
    data = [money_earned_this_week, hours_worked_this_week, hours_remaining_this_week, total_money_earned]
    # make sure all the floats are rounded to 2 decimal places
    data = [round(x, 2) for x in data]
    return data

def display_total_charts(data: pd.DataFrame):
    df = data.copy()
    col1, col2 = st.columns(2)
    with col1:
        st.header("Hours Worked per week")
        fig = px.bar(df, x="week_id", y="hours_worked", title="Hours worked per week", width=900, height=500,barmode='group')
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        fig.update_xaxes(categoryorder='total ascending', showgrid=False)
        fig.update_yaxes(rangemode='tozero', showgrid=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.header("Money Earned per week")
        fig = px.bar(df, x="week_id", y="money_earned", title="Money earned per week", width=900, height=500)
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        fig.update_xaxes(rangemode='tozero', showgrid=False)
        fig.update_yaxes(rangemode='tozero', showgrid=True)

        st.plotly_chart(fig, use_container_width=True)

def display_charts(data: pd.DataFrame):
    df = data.copy()
    col1, col2 = st.columns(2)
    this_week = df[df['week_id'] == df['week_id'].max()]
    with col1:
        st.header("Hours Worked this week")
        fig = px.bar(this_week, x="date", y="hours_worked", title="Hours worked this week", width=900, height=500)
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        fig.update_xaxes(categoryorder='total ascending', showgrid=False)
        fig.update_yaxes(rangemode='tozero', showgrid=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.header("Money Earned this week")
        fig = px.bar(this_week, x="date", y="money_earned", title="Money earned this week", width=900, height=500)
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        fig.update_xaxes(rangemode='tozero', showgrid=False)
        fig.update_yaxes(rangemode='tozero', showgrid=True)
        st.plotly_chart(fig, use_container_width=True)
    


def display_table(data: pd.DataFrame):
    # display the date as just date, punch_in and punch_out as time, hours_worked as float
    df = pd.DataFrame()
    df['date'] = data['date'].dt.date
    df['week'] = data['week_id'].astype(int)
    df['punch in'] = data['punch_in'].dt.time
    df['punch out'] = data['punch_out'].dt.time
    df['hours worked'] = data['hours_worked'].astype(float)
    # set the index to be the date
    df.set_index('date', inplace=True)

    st.dataframe(df, width=1000, height=500)
    st.download_button(
        label="Download CSV",
        data=df.to_csv().encode("utf-8"),
        file_name="data.csv",
        mime="text/csv",
    )

def prepare_df(df, pay_rate=14.20):
    df = calculate_week_id(df)
    df = calculate_hours_worked(df)
    df['money_earned'] = df['hours_worked'] * pay_rate
    # df.set_index('date', inplace=True)
    return df

def add_a_punch(df, st):
    # get the date
    date = st.date_input("Date")
    # get the punch in datetime
    punch_in = st.time_input("Punch in")
    # get the punch out time
    punch_out = st.time_input("Punch out")
    # convert the punch in and punch out time to datetime
    punch_in = datetime.datetime.combine(date, punch_in)
    punch_out = datetime.datetime.combine(date, punch_out)
    # conver date to datetime
    date = datetime.datetime.combine(date, datetime.datetime.min.time())

    pay_rate = st.number_input("Pay rate", 14.20)

    # check if the punch out time is after the punch in time
    if punch_out < punch_in:
        st.error("Punch out time must be after punch in time")
        return df

    # Create a button
    add_button = st.button("Add Punch")

    # Check if the button is clicked
    if add_button:
        temp_df = pd.DataFrame([[date, punch_in, punch_out, pay_rate]], columns=['date', 'punch_in', 'punch_out', 'pay_rate'])
        temp_df = prepare_df(temp_df, pay_rate)
        # combine the temp_df and df
        df = pd.concat([df, temp_df])
        df = df.sort_values(by=['date'])
        df = df.reset_index(drop=True)

    return df

def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.markdown(
    """
    <a href="https://github.com/anushkrishnav" target="_blank" style="text-decoration: none;">
        <div style="display: flex; align-items: center;">
            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/github.svg" width="50" style="border-radius: 50%;">
            <span style="font-size: 16px; margin-left: 5px; color:white"> Check my work out</span>
        </div>
    </a>
    """, unsafe_allow_html=True
    )
    st.sidebar.write("## Add a punch")
    df = add_a_punch(data, st.sidebar)
    return df

