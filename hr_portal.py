# hr_portal.py

import streamlit as st
import database as db
from datetime import datetime
from dashboard import show_dashboard

def hr_portal(user):
    st.subheader("HR Portal")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Customer Management", key="hr_customer_page"):
            st.session_state.page = "customer"
    with col2:
        if st.button("Doctor Management", key="hr_doctor_page"):
            st.session_state.page = "doctor"
    
    if st.button("Dashboards", key="dashboard"):
        st.session_state.page = "dashboard"

    if 'page' in st.session_state:
        if st.session_state.page == "customer":
            customer_page()
        elif st.session_state.page == "doctor":
            doctor_page()
        elif st.session_state.page == "dashboard":
            show_dashboard()

def customer_page():
    st.subheader("Customer Management")
    customer_menu = ["View Customers", "Add Customer", "Edit Customer", "Remove Customer"]
    customer_choice = st.selectbox("Customer Menu", customer_menu)
    
    if customer_choice == "View Customers":
        view_customers_page()
    elif customer_choice == "Add Customer":
        create_customer_page()
    elif customer_choice == "Edit Customer":
        edit_customer_page()
    elif customer_choice == "Remove Customer":
        remove_customer_page()

def doctor_page():
    st.subheader("Doctor Management")
    doctor_menu = ["View Doctors", "Add Doctor", "Edit Doctor", "Remove Doctor"]
    doctor_choice = st.selectbox("Doctor Menu", doctor_menu)
    
    if doctor_choice == "View Doctors":
        view_doctors_page()
    elif doctor_choice == "Add Doctor":
        create_doctor_page()
    elif doctor_choice == "Edit Doctor":
        edit_doctor_page()
    elif doctor_choice == "Remove Doctor":
        remove_doctor_page()

def edit_customer_page():
    st.subheader("Edit Customer")
    customers = get_customers()
    customer_names = [customer['full_name'] for customer in customers]
    selected_customer = st.selectbox("Select Customer", customer_names)
    
    if selected_customer:
        customer = next((cust for cust in customers if cust['full_name'] == selected_customer), None)
        if customer:
            st.write("Customer Details")
            full_name = st.text_input("Full Name", customer.get('full_name', ''))
            username = st.text_input("Username", customer.get('username', ''))
            phone_number = st.text_input("Phone Number", customer.get('phone_number', ''))
            location = st.text_input("Current Address", customer.get('location', ''))
            id_no = st.text_input("ID Number/Passport Number", customer.get('id_no', ''))
            nationality = st.text_input("Nationality", customer.get('nationality', ''))
            dob = st.date_input("Date of Birth", customer.get('dob', datetime.today()), max_value=datetime.today())
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(customer.get('gender', 'Male')))
            age = st.number_input("Age", min_value=0, max_value=150, value=customer.get('age', 0))
            
            if st.button("Update Customer"):
                query = """
                UPDATE customers SET full_name = %s, username = %s, phone_number = %s, location = %s, id_no = %s, nationality = %s, dob = %s, gender = %s, age = %s WHERE id = %s
                """
                db.execute_query(query, (full_name, username, phone_number, location, id_no, nationality, dob, gender, age, customer['id']))
                st.success("Customer updated successfully")
                st.experimental_rerun()

def edit_doctor_page():
    st.subheader("Edit Doctor")
    doctors = get_doctors()
    doctor_names = [doctor['full_name'] for doctor in doctors]
    selected_doctor = st.selectbox("Select Doctor", doctor_names)
    
    if selected_doctor:
        doctor = next((doc for doc in doctors if doc['full_name'] == selected_doctor), None)
        if doctor:
            st.write("Doctor Details")
            full_name = st.text_input("Full Name", doctor.get('full_name', ''))
            username = st.text_input("Username", doctor.get('username', ''))
            phone_number = st.text_input("Phone Number", doctor.get('phone_number', ''))
            location = st.text_input("Current Address", doctor.get('location', ''))
            id_no = st.text_input("ID Number/Passport Number", doctor.get('id_no', ''))
            medical_license = st.text_input("Medical License", doctor.get('medical_license', ''))
            
            if st.button("Update Doctor"):
                query = """
                UPDATE doctors SET full_name = %s, username = %s, phone_number = %s, location = %s, id_no = %s, medical_license = %s WHERE id = %s
                """
                db.execute_query(query, (full_name, username, phone_number, location, id_no, medical_license, doctor['id']))
                st.success("Doctor updated successfully")
                st.experimental_rerun()

def view_customers_page():
    st.subheader("View Customers")
    customers = get_customers()
    customer_names = ["Select a customer"] + [customer['full_name'] for customer in customers]
    selected_customer = st.selectbox("Select Customer", customer_names)
    
    if selected_customer != "Select a customer":
        customer = next((cust for cust in customers if cust['full_name'] == selected_customer), None)
        if customer:
            st.write("Customer Details")
            st.write(f"Full Name: {customer['full_name']}")
            st.write(f"Username: {customer['username']}")
            st.write(f"Phone Number: {customer['phone_number']}")
            st.write(f"Location: {customer['location']}")
            st.write(f"ID Number: {customer['id_no']}")
            st.write(f"Role: {customer['role']}")
            
            st.subheader("Uploaded Records")
            query = "SELECT DISTINCT upload_date FROM patient_records WHERE user_id = %s"
            dates = db.execute_query(query, (customer['id'],))
            date_options = ["Select a date"] + [date['upload_date'] for date in dates]
            
            selected_date = st.selectbox("Select Date", date_options)
            
            if selected_date != "Select a date":
                query = "SELECT * FROM patient_records WHERE user_id = %s AND upload_date = %s"
                records = db.execute_query(query, (customer['id'], selected_date))
                if records:
                    for record in records:
                        st.write(f"Upload Date: {record['upload_date']}")
                        st.image(record['image_path'], caption="Uploaded Image", use_column_width=True)
                        st.write(f"Initial Assessment: {record['initial_assessment']}")
                        st.write(f"Final Assessment: {record['final_assessment']}")
                        st.write(f"Doctor's Remarks: {record['remarks']}")
                        if st.button("Remove Record", key=f"remove_record_{record['id']}"):
                            query = "DELETE FROM patient_records WHERE id = %s"
                            db.execute_query(query, (record['id'],))
                            st.success("Record removed successfully")
                            st.experimental_rerun()
            if st.button("Remove All Records", key=f"remove_all_records_{customer['id']}"):
                query = "DELETE FROM patient_records WHERE user_id = %s"
                db.execute_query(query, (customer['id'],))
                st.success("All records removed successfully")
                st.experimental_rerun()

def create_customer_page():
    st.subheader("Create New Customer")
    full_name = st.text_input("Full Name", key="new_customer_full_name")
    username = st.text_input("Username", key="new_customer_username")
    password = st.text_input("Password", type='password', key="new_customer_password")
    phone_number = st.text_input("Phone Number", key="new_customer_phone_number")
    location = st.text_input("Current Address", key="new_customer_location")
    id_no = st.text_input("ID Number/Passport Number", key="new_customer_id_no")
    
    if st.button("Create Customer", key="create_customer"):
        if check_user_exists(username, phone_number, id_no):
            if check_username_exists(username):
                st.warning("Username already taken. Please choose another one.")
            if check_phone_number_exists(phone_number):
                st.warning("Phone number already taken. Please choose another one.")
            if check_id_no_exists(id_no):
                st.warning("ID number already taken. Please choose another one.")
        else:
            try:
                register_user(full_name, username, password, phone_number, location, id_no, None, "patient")
                st.success("Customer account created successfully")
            except db.mysql.connector.IntegrityError as e:
                st.error("An error occurred. Please try again later.")

def remove_customer_page():
    st.subheader("Remove Customer")
    customers = get_customers()
    customer_names = ["Select a customer"] + [customer['full_name'] for customer in customers]
    selected_customer = st.selectbox("Select Customer", customer_names)
    
    if selected_customer != "Select a customer":
        customer = next((cust for cust in customers if cust['full_name'] == selected_customer), None)
        if customer:
            st.write("Customer Details")
            st.write(f"Full Name: {customer['full_name']}")
            st.write(f"Username: {customer['username']}")
            st.write(f"Phone Number: {customer['phone_number']}")
            st.write(f"Location: {customer['location']}")
            st.write(f"ID Number: {customer['id_no']}")
            st.write(f"Role: {customer['role']}")
            if st.button("Remove Customer", key="remove_customer"):
                query = "DELETE FROM customers WHERE id = %s"
                db.execute_query(query, (customer['id'],))
                query = "DELETE FROM patient_records WHERE user_id = %s"
                db.execute_query(query, (customer['id'],))
                st.success("Customer and all records removed successfully")
                st.experimental_rerun()

def view_doctors_page():
    st.subheader("View Doctors")
    doctors = get_doctors()
    doctor_names = ["Select a doctor"] + [doctor['full_name'] for doctor in doctors]
    selected_doctor = st.selectbox("Select Doctor", doctor_names)
    
    if selected_doctor != "Select a doctor":
        doctor = next((doc for doc in doctors if doc['full_name'] == selected_doctor), None)
        if doctor:
            st.write("Doctor Details")
            st.write(f"Full Name: {doctor['full_name']}")
            st.write(f"Username: {doctor['username']}")
            st.write(f"Phone Number: {doctor['phone_number']}")
            st.write(f"Location: {doctor['location']}")
            st.write(f"ID Number: {doctor['id_no']}")
            st.write(f"Medical License: {doctor['medical_license']}")
            st.write(f"Role: {doctor['role']}")

            # Modify query to count patients assessed by the doctor
            query = """
            SELECT COUNT(*) AS patient_count 
            FROM patient_records 
            WHERE checked_by_doctor = %s AND final_assessment IS NOT NULL
            """
            patient_count = db.execute_query(query, (doctor['full_name'],))
            st.write(f"Number of Patients Checked: {patient_count[0]['patient_count']}")

def create_doctor_page():
    st.subheader("Create New Doctor")
    full_name = st.text_input("Full Name", key="new_doctor_full_name")
    username = st.text_input("Username", key="new_doctor_username")
    password = st.text_input("Password", type='password', key="new_doctor_password")
    phone_number = st.text_input("Phone Number", key="new_doctor_phone_number")
    location = st.text_input("Current Address", key="new_doctor_location")
    id_no = st.text_input("ID Number/Passport Number", key="new_doctor_id_no")
    medical_license = st.text_input("Medical License", key="new_doctor_medical_license")
    
    if st.button("Create Doctor", key="create_doctor"):
        if check_user_exists(username, phone_number, id_no):
            if check_username_exists(username):
                st.warning("Username already taken. Please choose another one.")
            if check_phone_number_exists(phone_number):
                st.warning("Phone number already taken. Please choose another one.")
            if check_id_no_exists(id_no):
                st.warning("ID number already taken. Please choose another one.")
        else:
            try:
                register_user(full_name, username, password, phone_number, location, id_no, None, "doctor", medical_license)
                st.success("Doctor account created successfully")
            except db.mysql.connector.IntegrityError as e:
                st.error("An error occurred. Please try again later.")

def remove_doctor_page():
    st.subheader("Remove Doctor")
    doctors = get_doctors()
    doctor_names = ["Select a doctor"] + [doctor['full_name'] for doctor in doctors]
    selected_doctor = st.selectbox("Select Doctor", doctor_names)
    
    if selected_doctor != "Select a doctor":
        doctor = next((doc for doc in doctors if doc['full_name'] == selected_doctor), None)
        if doctor:
            st.write("Doctor Details")
            st.write(f"Full Name: {doctor['full_name']}")
            st.write(f"Username: {doctor['username']}")
            st.write(f"Phone Number: {doctor['phone_number']}")
            st.write(f"Location: {doctor['location']}")
            st.write(f"ID Number: {doctor['id_no']}")
            st.write(f"Medical License: {doctor['medical_license']}")
            st.write(f"Role: {doctor['role']}")
            if st.button("Remove Doctor", key="remove_doctor"):
                query = "DELETE FROM doctors WHERE id = %s"
                db.execute_query(query, (doctor['id'],))
                st.success("Doctor removed successfully")

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

def register_user(full_name, username, password, phone_number, location, id_no, nationality, role, medical_license=None):
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
        INSERT INTO customers (full_name, username, password, phone_number, location, id_no, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (full_name, username, password, phone_number, location, id_no, role))

def get_customers():
    query = "SELECT * FROM customers"
    return db.execute_query(query)

def get_doctors():
    query = "SELECT * FROM doctors"
    return db.execute_query(query)

def get_patient_records(user_id):
    query = "SELECT * FROM patient_records WHERE user_id = %s"
    return db.execute_query(query, (user_id,))
