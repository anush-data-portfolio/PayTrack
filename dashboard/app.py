
import streamlit as st
from generate_data import generate_punches
from utils import (
    set_page_config, load_data, calculate_kpis, display_kpi_metrics, 
    display_total_charts, display_charts, display_table, display_sidebar,
    prepare_df, display_title)















def main():
    set_page_config()
    main_df = load_data()

    # start_date = datetime.date(2023, 1, 5)
    # end_date = datetime.date(2023, 6, 30)
    # main_df = generate_punches(start_date, end_date)
    # main_df.to_csv('data/punches_data_sample.csv', index=False)
    display_title()
    

    

    main_df = prepare_df(main_df)
    data = main_df.copy()


    df = display_sidebar(data)

    kpi_names = ["Money Earned","Hours worked","Hours Remaining", "Total Money earned so far"]
    


    kpis = calculate_kpis(df)

    
    display_kpi_metrics(kpis, kpi_names)

    display_charts(df)
    display_table(df)
    display_total_charts(df)


if __name__ == '__main__':
    main()