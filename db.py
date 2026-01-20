from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st

@st.cache_data
def fetch_dataframe(query, params=None):
    db = st.secrets["db"]

    DATABASE_URL = (
        f"postgresql+psycopg2://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['dbname']}"
    )

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)

    return df
