import random as random
import streamlit as st
import database as db
from utils import assess_image, model
import os

def patient_portal(user):
    st.subheader("Customer Information")
    st.write(f"Full Name: {user['full_name']}")
    st.write(f"Username: {user['username']}")

    # Query to get the count of total, assessed, and unassessed submissions
    total_submissions_query = "SELECT COUNT(*) AS count FROM patient_records WHERE user_id = %s"
    assessed_submissions_query = "SELECT COUNT(*) AS count FROM patient_records WHERE user_id = %s AND status = 'checked'"
    unassessed_submissions_query = "SELECT COUNT(*) AS count FROM patient_records WHERE user_id = %s AND status = 'unchecked'"

    total_submissions = db.execute_query(total_submissions_query, (user['id'],))[0]['count']
    assessed_submissions = db.execute_query(assessed_submissions_query, (user['id'],))[0]['count']
    unassessed_submissions = db.execute_query(unassessed_submissions_query, (user['id'],))[0]['count']

    st.write(f"Total Submissions: {total_submissions}")
    st.write(f"Assessed Submissions: {assessed_submissions}")
    st.write(f"Unassessed Submissions: {unassessed_submissions}")

    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    if st.button("My Information"):
        st.session_state.page = 'My Information'
        st.experimental_rerun()

    if st.button("Get an Assessment"):
        st.session_state.page = 'Get Assessment'
        st.experimental_rerun()

    if st.button("My Records"):
        st.session_state.page = 'My Records'
        st.experimental_rerun()

    if st.button("Submit Feedback"):
        st.session_state.page = 'Submit Feedback'
        st.experimental_rerun()

    if st.session_state.page == 'My Information':
        my_information_page(user)
    elif st.session_state.page == 'Get Assessment':
        get_assessment_page(user)
    elif st.session_state.page == 'My Records':
        my_records_page(user)
    elif st.session_state.page == 'Submit Feedback':
        submit_feedback_page(user)

def my_information_page(user):
    st.subheader("My Information")
    st.write(f"Full Name: {user.get('full_name', 'N/A')}")
    st.write(f"Username: {user.get('username', 'N/A')}")
    st.write(f"Phone Number: {user.get('phone_number', 'N/A')}")
    st.write(f"Current Address: {user.get('location', 'N/A')}")
    st.write(f"ID Number: {user.get('id_no', 'N/A')}")
    st.write(f"Nationality: {user.get('nationality', 'N/A')}")
    st.write(f"Date of Birth: {user.get('dob', 'N/A')}")
    st.write(f"Gender: {user.get('gender', 'N/A')}")
    st.write(f"Age: {user.get('age', 'N/A')}")

def get_assessment_page(user):
    st.subheader("Upload Image for Assessment")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        # Save the image to the file system
        upload_folder = 'uploads/'  # Change to a relative path for Streamlit
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        image_path = os.path.join(upload_folder, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Assessing image..."):
            # Assess the image using the model
            initial_assessment = assess_image(image_path, model)  # Pass the model to the function
        
        st.image(image_path, caption="Uploaded Image", use_column_width=True)
        st.write(f"Initial Assessment: {initial_assessment}")

        # Save the assessment to the database
        query = """
        INSERT INTO patient_records (user_id, image_path, initial_assessment, status)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (user['id'], image_path, initial_assessment, 'unchecked'))

        # Provide health tips based on the assessment
        st.subheader("Health Tips")
        query = "SELECT tips FROM health_tips WHERE disease = %s"
        tips = db.execute_query(query, (initial_assessment,))
        if tips:
            st.write(tips[0]['tips'])

def my_records_page(user):
    st.subheader("My Records")
    st.markdown("<hr/>", unsafe_allow_html=True)  # Add a horizontal line for separation
    filter_option = st.radio("Filter Submissions", ["All", "Assessed", "Unassessed"], horizontal=True)
    
    if filter_option == "All":
        query = "SELECT DISTINCT upload_date FROM patient_records WHERE user_id = %s"
    elif filter_option == "Assessed":
        query = "SELECT DISTINCT upload_date FROM patient_records WHERE user_id = %s AND status = 'checked'"
    elif filter_option == "Unassessed":
        query = "SELECT DISTINCT upload_date FROM patient_records WHERE user_id = %s AND status = 'unchecked'"

    dates = db.execute_query(query, (user['id'],))
    date_options = ["All Dates"] + [date['upload_date'] for date in dates]
    selected_date = st.selectbox("Select Date", date_options)

    st.markdown("<hr/>", unsafe_allow_html=True)  # Add a horizontal line for separation

    # Additional filters
    initial_assessment_filter = st.selectbox("Filter by Initial Assessment", ["All", "Caries", "Gingivitis", "Mouth Ulcers"])
    final_assessment_filter = st.selectbox("Filter by Doctor's Assessment", ["All", "Caries", "Gingivitis", "Mouth Ulcers"])

    filters = ["user_id = %s"]
    params = [user['id']]

    if selected_date != "All Dates":
        filters.append("upload_date = %s")
        params.append(selected_date)
    
    if filter_option == "Assessed":
        filters.append("status = 'checked'")
    elif filter_option == "Unassessed":
        filters.append("status = 'unchecked'")

    if initial_assessment_filter != "All":
        filters.append("initial_assessment = %s")
        params.append(initial_assessment_filter)
    if final_assessment_filter != "All":
        filters.append("final_assessment = %s")
        params.append(final_assessment_filter)

    query = f"SELECT * FROM patient_records WHERE {' AND '.join(filters)}"
    records = db.execute_query(query, tuple(params))

    displayed_tips = set()  # Set to track displayed tips

    if records:
        for record in records:
            st.write(f"Upload Date: {record['upload_date']}")
            st.image(record['image_path'], caption="Uploaded Image", use_column_width=True)
            st.write(f"Initial Assessment: {record['initial_assessment']}")
            st.write(f"Doctor's Assessment: {record['final_assessment']}")
            st.write(f"Doctor's Remarks: {record['remarks']}")
            st.write(f"Checked by: {record['checked_by_doctor']}")
            
            # Fetch and display a random health tip that hasn't been displayed yet
            query = "SELECT tips FROM health_tips WHERE disease = %s"
            tips = db.execute_query(query, (record['initial_assessment'],))
            if tips:
                random.shuffle(tips)  # Shuffle the tips to randomize
                for tip in tips:
                    if tip['tips'] not in displayed_tips:
                        displayed_tips.add(tip['tips'])
                        st.subheader("Health Tip")
                        st.write(tip['tips'])
                        break
                
            st.markdown("<hr/>", unsafe_allow_html=True)  # Add a horizontal line between records
    else:
        st.write("No records found for the selected filters.")

def submit_feedback_page(user):
    st.subheader("Submit Feedback")
    satisfaction_rating = st.selectbox("Satisfaction Rating", [1, 2, 3, 4, 5], index=4)
    feedback_text = st.text_area("Your Feedback")
    if st.button("Submit", key="submit_feedback"):
        if not feedback_text.strip():
            st.warning("Please provide your feedback in the text area.")
        else:
            query = "INSERT INTO feedback (user_id, feedback_text) VALUES (%s, %s)"
            db.execute_query(query, (user['id'], feedback_text))
            st.success("Feedback submitted successfully")
            st.session_state.page = 'Home'
            st.experimental_rerun()
