import streamlit as st
# from pages.login import login_page
# from pages.home import home_page
# from pages.display import display_page
# from pages.chat import chat_page
from app_pages import login, home, display, chat


#Session Storage Variables:

##page tracker (using session states)
if "page" not in st.session_state:
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
    


custom_css = f"""
        <style>
            .stApp {{
                background-color: {"#1E1E1E" if st.session_state.theme == "dark" else "#FFFFFF"};
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
            }}
            .stButton>button {{
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
                background-color: {"#2E2E2E" if st.session_state.theme == "dark" else "#F0F2F6"};
            }}
            .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
                background-color: {"#2E2E2E" if st.session_state.theme == "dark" else "#FFFFFF"};
            }}
        </style>
    """

#Mode Settings
st.markdown(custom_css, unsafe_allow_html=True)


#Multi-Page Simulation in SPA using Mutli-Level Function Calling: Route Url - Action/Request Handler pairs (1-n)
def main():
    if st.session_state.page == "login":
        login.login_page()
    elif st.session_state.page == "home":
        home.home_page()
    elif st.session_state.page == "chat":
        chat.chat_page()
    
if __name__ == "__main__":
    main()

