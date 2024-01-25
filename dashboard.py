import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
import datetime
import matplotlib.pyplot as plt
import re

def checking_for_columns(df):
    columns_to_check = ['Details', 'Ammount', 'type ', 'entry_type', 'date']
    df_columns_lower = [col.lower() for col in df.columns]
    if all(col.lower() in df_columns_lower for col in columns_to_check):
        return True
    else:
        return False

def loading_and_processing(df):
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%B")
    return df

def latest_transactions(df:pd.DataFrame):
    df_sorted = df.sort_values(by="date",ascending=False)
    latest_debit = df_sorted[df_sorted['entry_type'] == 'debit'].iloc[0].iloc[1]
    latest_debit_reason = df_sorted[df_sorted['entry_type'] == 'debit'].iloc[0].iloc[0]

    latest_credit = df_sorted[df_sorted['entry_type'] == 'credit'].iloc[0][1]
    latest_credit_reason = df_sorted[df_sorted['entry_type'] == 'credit'].iloc[0][0]

    return {"latest_credit":[latest_credit,latest_credit_reason],
            "latest_debit":[latest_debit,latest_debit_reason]}

def calculate_sum_by_type(filtered_df):
    filtered_df = filtered_df.groupby('type ')['Ammount'].sum()
    return filtered_df

def getting_months(df,type):
    filtered_df = df[df["entry_type"]==type]
    return filtered_df["month"].unique().tolist()

def getting_months_line(df):
    return df["month"].unique().tolist()

st.title('Your Financial Dashboard')

google_sheets_link = st.text_input('Google Sheet Link')
if google_sheets_link == "":
    st.write("Enter Google Sheets link")
else:
    link = re.sub(r'/edit\?usp=sharing$', '/export?format=csv', google_sheets_link)
    try:
        df = pd.read_csv(link)
        if df is None:
            st.text("Data is not loaded")
        else:
            if checking_for_columns(df):
                # Assuming you have a function loading_and_processing(df)
                df = loading_and_processing(df)
                data_load_state = st.text('Loaded Data Successfully')
                #recent transactions
                st.subheader("Recent Transactions")
                latest = latest_transactions(df)

                col1,col2 = st.columns(2,gap="small")
                col1.metric(label="Debit", value=latest["latest_debit"][0], delta=f"+ {latest['latest_debit'][1]}" )
                style_metric_cards(background_color="#0100",border_radius_px=10,box_shadow=True)
                col2.metric(label="Credit", value=latest["latest_credit"][0], delta=f"- {latest['latest_credit'][1]}")

                container = st.container()
                with container:
                    st.write("Check Transactions")
                    date = st.date_input("Search transactions for", datetime.date.today(),format="YYYY.MM.DD")
                    filtered_df = df[df["date"]==str(date)]
                    st.dataframe(filtered_df,use_container_width=True)

                style_metric_cards(background_color="#0000",border_radius_px=10,box_shadow=True)


                tab1, tab2 = st.tabs(["Expenses", "Income"])

                with tab1: 
                   drop_down = getting_months(df,"credit")
                   month = st.selectbox('Select month',drop_down)
                   tab3,tab4 = st.tabs(["Bar","Pie"])

                   with tab3:
                    st.subheader("Expenses")
                    filtered_df = df[(df["month"]==month) & (df["entry_type"]=="credit")]
                    group_by = calculate_sum_by_type(filtered_df)
                    st.bar_chart(group_by,y="Ammount",color="#FF0000",width=0)

                    with tab4:
                        st.subheader("Expenses")
                        exp_dict = filtered_df.groupby('type ')['Ammount'].sum().to_dict()
                        fig, ax = plt.subplots()
                        ax.pie(exp_dict.values(),autopct='%1.1f%%')
                        ax.legend(labels=exp_dict.keys(), title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                        st.pyplot(fig)


                with tab2:
                   drop_down = getting_months(df,"credit")
                   month = st.selectbox('Select month',drop_down,key="!2")
                   tab5,tab6 = st.tabs(["Bar","Pie"])

                   with tab5:
                    st.subheader("Income")
                    filtered_df = df[(df["month"]==month) & (df["entry_type"]=="debit")]
                    group_by = calculate_sum_by_type(filtered_df)
                    st.bar_chart(group_by,y="Ammount",color="#0000FF")

                    with tab6:
                        st.subheader("Income")
                        exp_dict = filtered_df.groupby('type ')['Ammount'].sum().to_dict()
                        fig, ax = plt.subplots()
                        ax.pie(exp_dict.values(),autopct='%1.1f%%')
                        ax.legend(labels=exp_dict.keys(), title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                        st.pyplot(fig)

                container = st.container()
                with container:
                    st.write("Monthly Transactions")
                    tab1, tab2 = st.tabs(["Expenses", "Income"])

                    with tab1:
                        drop_down = getting_months_line(df)
                        month_ = st.selectbox('Select month',drop_down,key="123")
                        data_credit = df[(df["month"]==month_) & (df["entry_type"]=="credit")]
                        st.line_chart(data_credit,x="date",y="Ammount")

                    with tab2:
                        drop_down = getting_months_line(df)
                        month_ = st.selectbox('Select month',drop_down,key="23")
                        data_debit = df[(df["month"]==month_) & (df["entry_type"]=="debit")]
                        st.line_chart(data_debit,x="date",y="Ammount")

                container = st.container()
                with container:
                   filtered_df = df[(df["month"]==month) & (df["entry_type"]=="credit")]
                   filtered_df = calculate_sum_by_type(filtered_df)

                   fig, ax = plt.subplots()
            else:
                st.write("One or more columns are missing.")


    except FileNotFoundError:
       st.text("File Does Not Exist")

