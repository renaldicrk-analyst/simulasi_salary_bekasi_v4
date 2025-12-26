import psycopg2
import pandas as pd
import streamlit as st

def fetch_dataframe(query, params):
    conn = psycopg2.connect(
        host=st.secrets["db"]["host"],
        port=st.secrets["db"]["port"],
        dbname=st.secrets["db"]["dbname"],
        user=st.secrets["db"]["user"],
        password=st.secrets["db"]["password"],
    )

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
