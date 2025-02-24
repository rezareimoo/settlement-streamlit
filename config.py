import streamlit as st


# Database configuration with decryption
DB_HOST = st.secrets["db_host"]
DB_NAME = st.secrets["db_name"]
DB_USER = st.secrets["db_username"]
DB_PASSWORD = st.secrets["db_password"]
DB_PORT = st.secrets["db_port"]

# Construct database URL
if DB_USER and DB_PASSWORD:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    raise ValueError("Database credentials not properly configured or decrypted") 