import streamlit.components.v1 as components
from streamlit.components.v1 import html


def display_page():
    graph_html = open("graph.html", "r", encoding="utf-8").read()        
    components.html(graph_html, height=600)
