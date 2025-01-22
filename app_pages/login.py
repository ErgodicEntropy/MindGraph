import streamlit as st
import sqlite3
import secrets
from bcrypt import hashpw, gensalt, checkpw  # For password hashing
### MAIN RUN

def login_page(): #User Registration, Profile Creation and Login
    # Function to hash passwords
    def hash_password(password):
        return hashpw(password.encode(), gensalt())

    # Function to verify passwords
    def verify_password(plain_password, hashed_password):
        return checkpw(plain_password.encode(), hashed_password)


    if "user_action" not in st.session_state:
        st.session_state.user_action = None #Login or SignUp
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False


    def user_action_reset():
        st.session_state.user_action = None
        st.rerun()        


    #DATABASE MS
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    
    #User Settings    
    if st.session_state.user_action == None:
        # Title and welcome message
        st.title("MindGraph 🧠")
        st.write("Welcome to MindGraph! Make your experience visualized!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up"):    
                st.session_state.user_action = "Sign Up"
                st.rerun()
        with col2:
            if st.button("Login"):    
                st.session_state.user_action = "Login"
                st.rerun()
    if st.session_state.user_action == "Sign Up":
        ##User Authentification and Profile Creation
        st.write("## Create Account")
        new_username = st.text_input("Enter a username")
        new_password = st.text_input("Enter a password", type="password")    
        if st.button("Create Profile"):
            if new_username and new_password:
                try:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    hashed_password = hash_password(new_password)
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_password))
                    conn.commit()
                    st.success("Profile Created Successfully!")
                except sqlite3.IntegrityError:
                    st.error(f"Username {new_username} already exists. Please choose another!")
                finally:
                    conn.close()
            else:
                st.warning("Please fill in the requried forms")
        if st.button("Back"):
            user_action_reset()

    if st.session_state.user_action == "Login":

        st.write("## Sign In")
        login_username = st.text_input("Enter a username")
        login_password = st.text_input("Enter a password", type="password")    
        if st.button("Sign In"):
            if login_username and login_password:
                try:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("SELECT password FROM users WHERE username = ?", (login_username,))
                    conn.commit()
                    results = c.fetchone()
                    if results and verify_password(login_password,results[0]):
                        st.session_state.authentication_status = True
                        st.success("You are now logged in.")
                    else:
                        st.session_state.authentication_status = False
                        st.error("Invalid Username/Password")
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                finally:
                    conn.close()
            st.rerun()
        if st.button("Back"):
            user_action_reset()  # Reset user_action to None

        if st.session_state.authentication_status:

            if st.button("Start"):
                st.session_state.page = "home"
                st.rerun()
        if st.session_state.authentication_status is None:
            st.warning("Please fill in the form")
        

        if st.session_state.authentication_status:         
            if st.sidebar.button("Logout"):
                st.session_state.authentication_status = True
                st.session_state.clear()
                st.rerun()