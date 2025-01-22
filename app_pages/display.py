import streamlit.components.v1 as components
from streamlit.components.v1 import html
import streamlit as st
from .. import agents 


def display_page():
    st.set_page_config(
    page_title="results page",
    page_icon="👋",
    )

    graph_html = open("graph.html", "r", encoding="utf-8").read()        
    components.html(graph_html, height=600)


    if st.button("Let's Chat"):
        st.session_state.page == "chat"
