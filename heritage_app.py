import streamlit as st
import sqlite3
import google.generativeai as genai
genai.configure(api_key="AIzaSyCVx81UBXMpzSC831qULrhezJlXshJF1ts")


# Database setup
DB_NAME = 'heritage.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute("""
CREATE TABLE IF NOT EXISTS heritage_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    location TEXT,
    languages TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS narratives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER,
    language TEXT,
    narrative TEXT,
    FOREIGN KEY(site_id) REFERENCES heritage_sites(id)
)
""")
conn.commit()

def add_heritage_site(name, description, location, languages):
    c.execute("INSERT INTO heritage_sites (name, description, location, languages) VALUES (?, ?, ?, ?)",
              (name, description, location, ",".join(languages)))
    conn.commit()

def get_heritage_sites():
    c.execute("SELECT * FROM heritage_sites")
    return c.fetchall()

def add_narrative(site_id, language, narrative):
    c.execute("INSERT INTO narratives (site_id, language, narrative) VALUES (?, ?, ?)",
              (site_id, language, narrative))
    conn.commit()

def get_narratives(site_id, language):
    c.execute("SELECT narrative FROM narratives WHERE site_id=? AND language=?", (site_id, language))
    return c.fetchall()

def generate_narrative(description, language):
    prompt = f"Create an immersive narrative about this heritage site in {language}:\n{description}"
    
    model = genai.GenerativeModel("models/gemini-2.5-flash")  

    response = model.generate_content(prompt)
    
    return response.text

st.title("Indian Heritage Preservation Assistant")

st.header("Add New Heritage Site")
name = st.text_input("Site Name")
description = st.text_area("Site Description")
location = st.text_input("Location")
languages = st.multiselect("Supported Languages", ["English", "Hindi", "Tamil", "Telugu", "Bengali"])
if st.button("Add Site"):
    if name and description and location and languages:
        add_heritage_site(name, description, location, languages)
        st.success("Heritage site added successfully.")
    else:
        st.error("Please fill in all fields to add a heritage site.")

st.header("Explore Heritage Sites")
sites = get_heritage_sites()
site_options = {f"{row[1]} ({row[3]})": row for row in sites}
selected = st.selectbox("Select a heritage site", list(site_options.keys()) if site_options else ["No heritage sites added yet"])
if selected != "No heritage sites added yet":
    site = site_options[selected]
    st.subheader(site[1])
    st.write(site[2])
    st.write(f"Location: {site[3]}")
    supported_langs = site[4].split(",")
    lang = st.selectbox("Narrative Language", supported_langs)
    st.write("Generate immersive narrative using AI:")
    if st.button("Generate Narrative"):
        with st.spinner("Generating narrative..."):
            narrative = generate_narrative(site[2], lang)
            add_narrative(site[0], lang, narrative)
            st.success("Narrative generated and saved.")
            st.write(narrative)
    st.write("Existing Narratives:")
    narratives = get_narratives(site[0], lang)
    for n in narratives:
        st.info(n[0])
