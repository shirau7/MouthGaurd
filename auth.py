import streamlit as st
import database as db
from datetime import datetime
import pycountry

def show_signup():
    st.subheader("Create New Account")
    full_name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    phone_number = st.text_input("Phone Number")

    # Get list of all countries
    countries = [country.name for country in pycountry.countries]
    location = st.selectbox("Current Address (Country)", countries)

    id_no = st.text_input("ID Number/Passport Number")
    nationality = st.text_input("Nationality")
    dob = st.date_input("Date of Birth", max_value=datetime.today())
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=200)

    if st.button("Sign Up"):
        if not all([full_name, username, password, phone_number, location, id_no, nationality, dob, gender, age > 0]):
            st.warning("Please fill in all fields to sign up.")
        else:
            if check_user_exists(username, phone_number, id_no):
                if check_username_exists(username):
                    st.warning("Username already taken. Please choose another one.")
                if check_phone_number_exists(phone_number):
                    st.warning("Phone number already taken. Please choose another one.")
                if check_id_no_exists(id_no):
                    st.warning("ID number already taken. Please choose another one.")
            else:
                try:
                    register_user(full_name, username, password, phone_number, location, id_no, nationality, "patient", dob, gender, age)
                    st.success("You have successfully created an account")
                except db.mysql.connector.IntegrityError as e:
                    st.error("An error occurred. Please try again later.")

def show_login():
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.success(f"Welcome {username}")
            return user
        else:
            st.warning("Incorrect Username/Password")
    return None

def check_user_exists(username, phone_number, id_no):
    query = """
    SELECT id FROM hr WHERE username = %s OR phone_number = %s OR id_no = %s
    UNION
    SELECT id FROM doctors WHERE username = %s OR phone_number = %s OR id_no = %s
    UNION
    SELECT id FROM customers WHERE username = %s OR phone_number = %s OR id_no = %s
    """
    result = db.execute_query(query, (username, phone_number, id_no, username, phone_number, id_no, username, phone_number, id_no))
    return len(result) > 0

def check_username_exists(username):
    query = """
    SELECT id FROM hr WHERE username = %s
    UNION
    SELECT id FROM doctors WHERE username = %s
    UNION
    SELECT id FROM customers WHERE username = %s
    """
    result = db.execute_query(query, (username, username, username))
    return len(result) > 0

def check_phone_number_exists(phone_number):
    query = """
    SELECT id FROM hr WHERE phone_number = %s
    UNION
    SELECT id FROM doctors WHERE phone_number = %s
    UNION
    SELECT id FROM customers WHERE phone_number = %s
    """
    result = db.execute_query(query, (phone_number, phone_number, phone_number))
    return len(result) > 0

def check_id_no_exists(id_no):
    query = """
    SELECT id FROM hr WHERE id_no = %s
    UNION
    SELECT id FROM doctors WHERE id_no = %s
    UNION
    SELECT id FROM customers WHERE id_no = %s
    """
    result = db.execute_query(query, (id_no, id_no, id_no))
    return len(result) > 0

def login_user(username, password):
    query = """
    SELECT id, full_name, username, phone_number, location, id_no, nationality, role, dob, gender, age 
    FROM customers 
    WHERE username = BINARY %s AND password = BINARY %s
    UNION
    SELECT id, full_name, username, phone_number, location, id_no, NULL AS nationality, role, NULL AS dob, NULL AS gender, NULL AS age 
    FROM doctors 
    WHERE username = BINARY %s AND password = BINARY %s
    UNION
    SELECT id, full_name, username, phone_number, location, id_no, NULL AS nationality, role, NULL AS dob, NULL AS gender, NULL AS age 
    FROM hr 
    WHERE username = BINARY %s AND password = BINARY %s
    """
    result = db.execute_query(query, (username, password, username, password, username, password))
    return result[0] if result else None

def register_user(full_name, username, password, phone_number, location, id_no, nationality, role, dob=None, gender=None, age=None, medical_license=None):
    if role == "hr":
        query = """
        INSERT INTO hr (full_name, username, password, phone_number, location, id_no, nationality, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (full_name, username, password, phone_number, location, id_no, nationality, role))
    elif role == "doctor":
        query = """
        INSERT INTO doctors (full_name, username, password, phone_number, location, id_no, medical_license, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (full_name, username, password, phone_number, location, id_no, medical_license, role))
    elif role == "patient":
        query = """
        INSERT INTO customers (full_name, username, password, phone_number, location, id_no, nationality, role, dob, gender, age)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (full_name, username, password, phone_number, location, id_no, nationality, role, dob, gender, age))
