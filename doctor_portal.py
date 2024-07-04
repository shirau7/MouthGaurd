# doctor_portal.py

import streamlit as st
import database as db
import pandas as pd
from datetime import datetime
from dashboard import show_dashboard

def doctor_portal(user):
    st.subheader("Doctor Portal")
    
    if st.button("View My Information"):
        st.session_state.page = "view_my_information"
        st.experimental_rerun()

    if st.button("Check Patients", key="check_patients"):
        st.session_state.page = "check_patients"
    
    if st.button("Dashboards", key="dashboard"):
        st.session_state.page = "dashboard"
    
    if 'page' in st.session_state:
        if st.session_state.page == "view_my_information":
            view_my_information_page(user)
        elif st.session_state.page == "check_patients":
            check_patients_page(user)
        elif st.session_state.page == "dashboard":
            show_dashboard()

def view_my_information_page(user):
    st.subheader("My Information")
    st.write(f"Full Name: {user['full_name']}")
    st.write(f"Username: {user['username']}")
    st.write(f"Phone Number: {user['phone_number']}")
    st.write(f"Current Address: {user['location']}")
    st.write(f"ID Number: {user['id_no']}")
    if 'medical_license' in user:
        st.write(f"Medical License: {user['medical_license']}")

def check_patients_page(user):
    st.subheader("Check Patients")

    with st.expander("Filters", expanded=True):
        filter_option = st.radio("Filter Patients by Status", ("All", "Unchecked", "Checked"), horizontal=True)
        date_filter_option = st.radio("Filter by Date", ["All Dates", "Select Date Range"], horizontal=True)
        
        if date_filter_option == "Select Date Range":
            start_date = st.date_input("Start Date", max_value=datetime.today(), key="start_date", value=None)
            end_date = st.date_input("End Date", max_value=datetime.today(), key="end_date", value=None)
            
            if start_date and end_date and start_date > end_date:
                st.error("Start Date cannot be greater than End Date.")
                return
        else:
            start_date = end_date = None

        gender_filter = st.selectbox("Filter by Gender", ["All", "Male", "Female"], key="gender_filter")
        age_filter = st.slider("Filter by Age", min_value=0, max_value=150, value=(0, 150), key="age_filter")
        
        # Filter by initial assessment
        initial_assessment_filter = st.selectbox("Filter by Initial Assessment", ["All", "Caries", "Gingivitis", "Mouth Ulcers"], key="initial_assessment_filter")
    
    filters = []
    filter_query = ""

    if filter_option != "All":
        filters.append(f"pr.status = '{filter_option.lower()}'")

    if date_filter_option == "Select Date Range" and start_date and end_date:
        filters.append(f"DATE(pr.upload_date) BETWEEN '{start_date}' AND '{end_date}'")

    if gender_filter != "All":
        filters.append(f"c.gender = '{gender_filter}'")

    if age_filter:
        filters.append(f"c.age BETWEEN {age_filter[0]} AND {age_filter[1]}")

    if initial_assessment_filter != "All":
        filters.append(f"pr.initial_assessment = '{initial_assessment_filter}'")

    if filters:
        filter_query = "WHERE " + " AND ".join(filters)

    query = f"""
    SELECT pr.*, c.full_name AS username, c.gender, c.age FROM patient_records pr
    JOIN customers c ON pr.user_id = c.id
    {filter_query}
    """
    patients = db.execute_query(query)

    if not patients:
        st.write("No patients to display")
        return

    # Display patient list in a scrollable format using st.dataframe
    st.write("### Patient List")
    patient_list = [{"ID": patient['user_id'], "Name": patient['username'], "Gender": patient['gender'], "Age": patient['age'], "Status": patient['status'], "Upload Date": patient['upload_date'].date(), "Initial Assessment": patient['initial_assessment']} for patient in patients]
    
    # Convert to DataFrame for better formatting
    patient_df = pd.DataFrame(patient_list)
    
    # Set the index to start from 1
    patient_df.index = patient_df.index + 1
    
    # Set the maximum height to fit 5 rows
    st.dataframe(patient_df, height=200)

    unique_patient_ids = list(set(patient['user_id'] for patient in patients))
    selected_patient_id = st.selectbox("Select Patient ID", ["Select a patient"] + unique_patient_ids)
    
    if selected_patient_id != "Select a patient":
        patient_dates_query = "SELECT id, upload_date FROM patient_records WHERE user_id = %s"
        if filter_option == "Checked":
            patient_dates_query += " AND status = 'checked'"
        elif filter_option == "Unchecked":
            patient_dates_query += " AND status = 'unchecked'"

        if date_filter_option == "Select Date Range" and start_date and end_date:
            patient_dates_query += f" AND DATE(upload_date) BETWEEN '{start_date}' AND '{end_date}'"

        patient_dates = db.execute_query(patient_dates_query, (selected_patient_id,))
        
        selected_date_id = st.selectbox("Select Submission Date", ["All Dates"] + [f"{p['id']} - {p['upload_date'].date()}" for p in patient_dates])
        
        if selected_date_id != "All Dates":
            patient_record_id = int(selected_date_id.split(' - ')[0])
            patient = next((pat for pat in patients if pat['id'] == patient_record_id), None)
            
            if patient:
                st.subheader(f"Patient ID: {patient['user_id']}")
                st.write(f"Name: {patient['username']}")
                st.write(f"Uploaded Date: {patient['upload_date'].date()}")
                st.image(patient['image_path'], caption="Uploaded Image", use_column_width=True)
                st.write(f"Initial Assessment: {patient['initial_assessment']}")
                
                # Dropdown for final assessment
                final_assessment_options = ["Caries", "Gingivitis", "Mouth Ulcers", "None of the above"]
                final_assessment = st.selectbox("Doctor's Assessment", final_assessment_options, index=final_assessment_options.index(patient.get('final_assessment', 'None of the above')))
                
                remarks = st.text_area("Remarks", key=f"remarks_{patient['id']}", value=patient.get('remarks', ''))
                if st.button("Submit", key=f"submit_{patient['id']}"):
                    doctor_name = user['full_name']
                    query = "UPDATE patient_records SET final_assessment = %s, remarks = %s, status = %s, checked_by_doctor = %s, final_assessment_date = %s WHERE id = %s"
                    final_assessment_date = datetime.now()
                    db.execute_query(query, (final_assessment, remarks, 'checked', doctor_name, final_assessment_date, patient['id']))
                    st.success("Assessment submitted successfully.")
                    st.experimental_rerun()
        else:
            st.write("Display all submissions for the selected patient.")
