import streamlit.components.v1 as components
from streamlit.components.v1 import html
import streamlit as st

def display_page():
    graph_html = open("graph.html", "r", encoding="utf-8").read()        
    components.html(graph_html, height=600)


    if st.button("Let's Chat"):
        st.session_state.page == "chat"
