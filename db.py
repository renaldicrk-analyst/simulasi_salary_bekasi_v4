from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def fetch_dataframe(query, params):
    engine = create_engine(
        f"postgresql+psycopg2://{st.secrets['db']['user']}:"
        f"{st.secrets['db']['password']}@"
        f"{st.secrets['db']['host']}:"
        f"{st.secrets['db']['port']}/"
        f"{st.secrets['db']['dbname']}"
    )

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)

    return df
