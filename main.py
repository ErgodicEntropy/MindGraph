import streamlit as st
import agents


st.set_page_config(
    page_title="main",
    page_icon="👋",
)

#Session Storage Variables:

##page tracker (using session states)
if "page" not in st.session_state:
    st.session_state.page = "login"
    


st.markdown(
    """
    <style>
        /* Hide the automatic sidebar navigation menu */
        div[data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
    



    

                





#CRUD THE GRAPH: Insert, Search, Update, Delete
def crud_graph(): 
    pass

def suggest_components(): #suggest nodes and edges
    pass

def version_control(): #session storage: a list of graphs
    pass

def summarize_text():
    pass

def summarize_graph():
    pass

def expand_edge(): #explanation, summarization and QA chat
    pass

def expand_node(): #explanation, summarization and QA chat
    pass 

def memory_techniques():
    pass

def anki_logic():
    pass

def Export_Save():
    pass

def Share(): #Real-Time Collaboration, Documentation and Comments (Users in same session -> Network Effects)
    pass


        
def return_home():
    pass
    if st.button("Go Home"):
        st.session_state.page = "home"
        
        
        
def main():
    pass

if __name__ == "__main__":
    main()

