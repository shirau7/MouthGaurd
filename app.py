import streamlit as st
import base64
from auth import show_login, show_signup
from patient_portal import patient_portal
from doctor_portal import doctor_portal
from hr_portal import hr_portal
from dashboard import show_dashboard

def main():
    if 'user' not in st.session_state:
        if 'page' not in st.session_state:
            st.session_state.page = 'Home'

        if st.session_state.page == 'Home':
            home_page()

        elif st.session_state.page == 'Login':
            login_page()

        elif st.session_state.page == 'Sign Up':
            signup_page()
    else:
        user = st.session_state.user
        st.sidebar.write(f"Logged in as {user['username']} ({user['role']})")
        role = user['role']
        if role == 'patient':
            patient_portal(user)
        elif role == 'doctor':
            doctor_portal(user)
        elif role == 'hr':
            hr_portal(user)

        if st.sidebar.button("Logout", key="sidebar_logout_main"):
            st.session_state.pop('user', None)
            st.session_state.page = 'Home'
            st.experimental_rerun()
        
        if st.session_state.page == 'Dashboard':
            show_dashboard()

def home_page():
    st.markdown(
        """
        <style>
        .center {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .rounded-image {
            border-radius: 15px;
            width: 300px;
        }
        div.stButton > button {
            height: 50px;
            font-size: 20px;
            width: 200px; /* Ensure buttons have the same width */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    image_path = "C:\\Users\\shira\\Desktop\\FYP\\MouthGaurd\\webapp3.webp"
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <div class="center">
            <img src="data:image/png;base64,{encoded_image}" class="rounded-image" alt="Logo">
            <h2>Mouth Guard</h2>
            <p>Your dental health companion.</p>
            <p>Sign up to receive free assessment for Gingivitis, Caries, and Ulcers!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Use columns to center the button container
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Login"):
            st.session_state.page = 'Login'
            st.experimental_rerun()

        if st.button("Sign Up"):
            st.session_state.page = 'Sign Up'
            st.experimental_rerun()

def login_page():
    user = show_login()
    if user:
        st.session_state.user = user
        st.experimental_rerun()
    if st.button("Home"):
        st.session_state.page = 'Home'
        st.experimental_rerun()

def signup_page():
    show_signup()
    if st.button("Home"):
        st.session_state.page = 'Home'
        st.experimental_rerun()

if __name__ == "__main__":
    main()
