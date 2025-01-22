import streamlit.components.v1 as components
from streamlit.components.v1 import html
import streamlit as st
import sys 
import os
from pyvis.network import Network

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agents  # Now you can import agents.py


def display_page():
    net = Network(notebook=False, height="500px", width="100%")
    graph_html = open("graph.html", "r", encoding="utf-8").read()        
    net.show("graph.html")
    components.html(graph_html, height=600)


    if st.button("Let's Chat"):
        st.session_state.page == "chat"
