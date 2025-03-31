import streamlit as st
import requests

st.title("Persona Q&A Bot")

query = st.text_input("Enter your question:")
if st.button("Search"):
    if query:
        response = requests.get(f"http://127.0.0.1:5000/search?query={query}")

        results = response.json()
        
        st.write("### Results:")
        for res in results["results"]:
            st.write(f"**Rank {res['rank']}:**")
            st.write(f"Text: {res['text']}")
            st.write(f"Distance: {res['distance']}")
            st.write("---")
    else:
        st.warning("Please enter a query.")
