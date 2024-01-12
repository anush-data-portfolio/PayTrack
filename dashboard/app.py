
import streamlit as st
from generate_data import generate_punches
from utils import (
    set_page_config, load_data, calculate_kpis, display_kpi_metrics, 
    display_total_charts, display_charts, display_table, display_sidebar,
    prepare_df, display_title, display_total_pie_chart)
from auth import Auth
from crud import DBHandler



def login():
    # Create an empty container
    placeholder = st.empty()

    actual_username = "username"
    actual_password = "password"

    # Insert a form in the container
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    
    auth = Auth()
    session = auth.get_session(username, password)
    if submit and session:
        placeholder.empty()
        db = DBHandler("POSTGRES_URI")
        user = db.get_name(username)
        st.success(f"Welcome {user}")
        return username, password
    elif session is None:
        st.error("Login failed")
        st.write("Please check your credentials")
        return None, None
    return None, None

    

def load_dashboard_data(username, fake):
    POSTGRES_URI = 
    db = DBHandler(POSTGRES_URI)
    if fake:
        main_df= generate_punches(num_rows=300, start_date='2023-01-01', end_date='2023-12-31')
    else:
        main_df = db.get_punches(username)

    display_title()

    main_df = prepare_df(main_df)
    data = main_df.copy()


    df = display_sidebar(data)

    kpi_names = ["Money Earned","Hours worked","Hours Remaining", "Total Money earned so far"]
    


    kpis = calculate_kpis(df)

    
    display_kpi_metrics(kpis, kpi_names)

    display_charts(df)
    col1, col2 = st.columns(2)
    with col1:
        display_table(df)
    with col2:
        display_total_pie_chart(df)

    display_total_charts(df)






def main():
    set_page_config()
    username, password = None, None
    if st.sidebar.checkbox("Login"):
        username, password = login()
        if username is not None and password is not None:
            load_dashboard_data(username, fake=False)

    if username is None or password is  None:
        load_dashboard_data(username,fake=True)

        






if __name__ == '__main__':
    main()