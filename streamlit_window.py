# streamlit_app.py
import streamlit as st
import urllib.parse

results_placeholder = st.empty()
# Get the custom text passed in the URL query parameter

flag = st.query_params.get("flag", False)
if flag=='True':
    with open('example.txt', 'r') as file:
        result_text = file.read()

    print(len(result_text),0)
    # Display the custom text
    #st.write(result_text)
    results_placeholder.text(result_text)
