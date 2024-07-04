import streamlit as st
import pandas as pd
import database as db
import plotly.express as px

def fetch_data(query, params=None):
    return db.execute_query(query, params)

def show_dashboard():
    st.title("Dashboards")

    # Patients Served
    query = "SELECT COUNT(*) AS served FROM patient_records WHERE status = 'checked'"
    served = fetch_data(query)[0]['served']

    query = "SELECT COUNT(*) AS to_serve FROM patient_records WHERE status = 'unchecked'"
    to_serve = fetch_data(query)[0]['to_serve']

    st.subheader("Patients Served vs Patients to Serve")
    
    # Create a DataFrame for visualization
    served_data = {
        'Status': ['Served', 'To Serve'],
        'Count': [served, to_serve]
    }
    served_df = pd.DataFrame(served_data)
    
    # Create a bar chart
    fig = px.bar(served_df, x='Status', y='Count', title='Patients Served vs Patients to Serve')
    st.plotly_chart(fig)
    
    # Export served_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=served_df.to_csv(index=False).encode('utf-8'),
        file_name='patients_served_vs_to_serve.csv',
        mime='text/csv'
    )

    # Male to Female Patient Ratio
    query = "SELECT gender, COUNT(*) as count FROM customers GROUP BY gender"
    gender_data = fetch_data(query)
    gender_df = pd.DataFrame(gender_data)

    st.subheader("Male to Female Patient Ratio")
    fig = px.pie(gender_df, names='gender', values='count', title='Male to Female Patient Ratio')
    st.plotly_chart(fig)
    
    # Export gender_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=gender_df.to_csv(index=False).encode('utf-8'),
        file_name='male_to_female_patient_ratio.csv',
        mime='text/csv'
    )

    # Age Demographics
    query = "SELECT age, COUNT(*) as count FROM customers GROUP BY age"
    age_data = fetch_data(query)
    age_df = pd.DataFrame(age_data)

    st.subheader("Age Demographics")
    fig = px.bar(age_df, x='age', y='count', title='Age Demographics')
    st.plotly_chart(fig)
    
    # Export age_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=age_df.to_csv(index=False).encode('utf-8'),
        file_name='age_demographics.csv',
        mime='text/csv'
    )

    # Distribution of Diseases
    query = "SELECT initial_assessment, COUNT(*) as count FROM patient_records GROUP BY initial_assessment"
    disease_data = fetch_data(query)
    disease_df = pd.DataFrame(disease_data)

    st.subheader("Distribution of Diseases")
    fig = px.bar(disease_df, x='initial_assessment', y='count', title='Distribution of Diseases')
    st.plotly_chart(fig)
    
    # Export disease_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=disease_df.to_csv(index=False).encode('utf-8'),
        file_name='distribution_of_diseases.csv',
        mime='text/csv'
    )

    # Doctors and Patients Checked
    query = "SELECT checked_by_doctor, COUNT(*) as count FROM patient_records WHERE status = 'checked' GROUP BY checked_by_doctor"
    doctor_data = fetch_data(query)
    doctor_df = pd.DataFrame(doctor_data)

    st.subheader("Doctors and Patients Checked")
    fig = px.bar(doctor_df, x='checked_by_doctor', y='count', title='Doctors and Patients Checked')
    st.plotly_chart(fig)
    
    # Export doctor_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=doctor_df.to_csv(index=False).encode('utf-8'),
        file_name='doctors_and_patients_checked.csv',
        mime='text/csv'
    )

    # Customers and How Many Times They Have Submitted Assessments
    query = "SELECT c.full_name, COUNT(pr.id) as submissions FROM customers c JOIN patient_records pr ON c.id = pr.user_id GROUP BY c.id"
    submission_data = fetch_data(query)
    submission_df = pd.DataFrame(submission_data)

    st.subheader("Customers and How Many Times They Have Submitted Assessments")
    fig = px.bar(submission_df, x='full_name', y='submissions', title='Customers and Their Assessment Submissions')
    st.plotly_chart(fig)
    
    # Export submission_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=submission_df.to_csv(index=False).encode('utf-8'),
        file_name='customer_assessment_submissions.csv',
        mime='text/csv'
    )

    # Geographical Distribution of Patients
    query = "SELECT location, COUNT(*) as count FROM customers GROUP BY location"
    location_data = fetch_data(query)
    location_df = pd.DataFrame(location_data)

    st.subheader("Geographical Distribution of Patients")
    fig = px.choropleth(location_df, locations="location", locationmode='country names', color="count", 
                        hover_name="location", title="Geographical Distribution of Patients", 
                        color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig)
    
    # Export location_df to CSV
    st.download_button(
        label="Download data as CSV",
        data=location_df.to_csv(index=False).encode('utf-8'),
        file_name='geographical_distribution_of_patients.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    show_dashboard()
