import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import plotly.express as px
#add
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import time
import logging
import re
import requests

# Set the page configuration to wide mode
st.set_page_config(layout="wide")

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "abhinda5334@gmail.com"
EMAIL_PASSWORD = "ufsf fojk klfm zemt"

# Fetch DAG runs data and convert timestamps to IST
def fetch_dag_runs():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow")
    )
    
    query = """
    SELECT
        dr.execution_date::date AS "Execution Date",
        dr.dag_id AS "Job Name",
        CONCAT('#', ROW_NUMBER() OVER (ORDER BY dr.execution_date)) AS "Build No",
        dr.start_date AS "Start Date",
        dr.end_date AS "End Date",
        CONCAT(EXTRACT(hour FROM (dr.end_date - dr.start_date)), ' Hr : ', 
               EXTRACT(minute FROM (dr.end_date - dr.start_date)), ' Min : ', 
               EXTRACT(second FROM (dr.end_date - dr.start_date)), ' Sec') AS "Total Execution Time",
        dr.state AS "Status",
        CASE 
            WHEN dr.start_date IS NOT NULL AND dr.end_date IS NOT NULL THEN
                TO_CHAR(dr.start_date, 'Dy') || '-' || TO_CHAR(dr.end_date, 'Dy') 
            ELSE 'Not Scheduled'
        END AS "Frequency", 
        d.next_dagrun AS "Scheduled Time"
    FROM
        dag_run dr
    JOIN
        dag d ON dr.dag_id = d.dag_id
    ORDER BY
        dr.execution_date DESC
    """
    
    df_dag_runs = pd.read_sql(query, conn)
    conn.close()
    
    df_dag_runs['Start Date'] = pd.to_datetime(df_dag_runs['Start Date'])
    df_dag_runs['End Date'] = pd.to_datetime(df_dag_runs['End Date'])
    
    utc = pytz.timezone('UTC')
    ist = pytz.timezone('Asia/Kolkata')
    
    def convert_to_ist(dt):
        if dt.tzinfo is None:
            dt = utc.localize(dt)
        return dt.astimezone(ist)
    
    df_dag_runs['Execution Date'] = pd.to_datetime(df_dag_runs['Execution Date'])
    df_dag_runs['Execution Date'] = df_dag_runs['Execution Date'].apply(convert_to_ist)
    
    return df_dag_runs

# Send email notification
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "mohdnawaz2112@gmail.com"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("Email sent successfully!")
        logging.info(f"Email sent successfully at {datetime.now()}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Fetch DAG runs data
df_dag_runs = fetch_dag_runs()

# Styling the app
st.markdown(
    """
    <style>
        .main {
            background-color: #f0f2f6;
            font-family: 'Arial', sans-serif;
        }
        h1 {
            color: #333333;
        }
        .css-1offfwp {
            background-color: #333333 !important;
            color: white;
        }
        .css-1aumxhk {
            margin-top: 10px;
            margin-bottom: 5px;
        }
        .streamlit-expander {
            border: 2px solid #ececec;
        }
        .stMetric {
            background-color: #f4f4f9;
            border: 2px solid #dddddd;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
        }
        .dataframe {
            border: 2px solid #dddddd;
            border-radius: 10px;
            font-size: 13px;
        }
        .dataframe tr th {
            background-color: #f5f5f5;
            padding: 10px;
            text-align: center;
        }
        .dataframe tr td {
            padding: 8px;
        }
        .status-success {
            background-color: green;
            color: white;
        }
        .status-failed {
            background-color: red;
            color: white;
        }
        .status-running {
            background-color: orange;
            color: black;
        }
    </style>
    """, unsafe_allow_html=True
)

# Dashboard Title
st.markdown("<h1 style='text-align: center;'>AIRFLOW Jobs Monitoring Dashboard</h1>", unsafe_allow_html=True)

# Add a horizontal line between sections
st.markdown("<hr style='border: 2px solid #ccc;' />", unsafe_allow_html=True)

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Visualisation", "Email Notifications", "DAG Triggerig"])

# Tab 1: Summary Metrics
with tab1:
    st.markdown("### Filter by Date Range")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(df_dag_runs['Execution Date'].min()).date())
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(df_dag_runs['Execution Date'].max()).date())

    st.markdown("### Filter by Job name")
    col1, col2 = st.columns(2)
    job_options = ['All Jobs']+list(df_dag_runs['Job Name'].unique())

    selected_job = st.multiselect(
        "Select Job Name(s)", 
        options=job_options,
        default=[],
        help="You can select multiple job names to filter"
    )

    show_all = st.checkbox("Show all records", value=False)

    # Apply filters if not bypassed
    filtered_df = df_dag_runs.copy()
    
    if not show_all:
        filtered_df = filtered_df[(filtered_df['Execution Date'].dt.date >= start_date) & 
                                  (filtered_df['Execution Date'].dt.date <= end_date)]
    
    if "All Jobs" not in selected_job:  # Apply job name filter if a specific job is selected
        filtered_df = filtered_df[filtered_df['Job Name'].isin(selected_job)]
    # Display the Summary Metrics dynamically based on the filtered data
    st.markdown("### Summary Metrics")
    total_dags = filtered_df['Job Name'].nunique()
    total_runs = len(filtered_df)
    successful_runs = len(filtered_df[filtered_df['Status'] == 'success'])
    failed_runs = len(filtered_df[filtered_df['Status'] == 'failed'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total DAGs", total_dags)
    with col2:
        st.metric("Total Runs", total_runs)
    with col3:
        st.metric("Successful Runs", successful_runs)
    with col4:
        st.metric("Failed Runs", failed_runs)

    # Recent DAG Runs Table after metrics
    st.markdown("### Recent DAG Runs")

    # Add a custom styling to the data table
    st.markdown(
        """
        <style>
            .dataframe {
                border: 2px solid #dddddd;
                border-radius: 10px;
                font-size: 13px;
            }
            .dataframe tr th {
                background-color: #f5f5f5;
                padding: 10px;
                text-align: center;
            }
            .dataframe tr td {
                padding: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Styling the status column based on the status
    def color_status(val):
        if val == 'success':
            return 'background-color: green; color: white;'
        elif val == 'failed':
            return 'background-color: red; color: white;'
        elif val == 'running':
            return 'background-color: orange; color: black;'
        return ''

    styled_df = filtered_df.style.map(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)

    # Alerts and notifications section
    st.markdown("### Alerts")
    if failed_runs > 0:
        st.warning("Some DAG runs have failed. Please check the details in the table!")
        st.error("Attention: Check failed DAGs immediately!")
    else:
        st.success("All DAG runs are successful!")



# Tab 2: Analytics
with tab2:
    st.markdown("### Real-Time Analytics")
    
    if not filtered_df.empty:
        # Plotly bar chart for status counts with updated colors and bar width reduced
        status_counts = filtered_df['Status'].value_counts()
        
        # Define color mapping for the status
        status_colors = {
            'success': 'green',  # Subtle green
            'running': 'orange',  # Yellow shade
            'failed': 'red'    # Red shade
        }

        fig_bar = px.bar(
            status_counts, 
            x=status_counts.index, 
            y=status_counts.values,
            title="DAG Runs Status Distribution", 
            labels={'x': 'Status', 'y': 'Count'},
            color=status_counts.index,  # Set color by status
            color_discrete_map=status_colors  # Apply custom colors
        )
        
        # Reduce the bar width
        fig_bar.update_traces(width=0.4)  # Half of the current width

        # Update layout for better visuals
        fig_bar.update_layout(
            xaxis_title="Status",
            yaxis_title="Count",
            bargap=0.2  # Reduce space between bars
        )
        
        st.plotly_chart(fig_bar)

        # Plotly pie chart for status distribution with updated colors
        fig_pie = px.pie(
            status_counts, 
            values=status_counts.values, 
            names=status_counts.index,
            title="Status Distribution", 
            hole=0.3,
            color=status_counts.index,  # Set color by status
            color_discrete_map=status_colors  # Apply custom colors
        )
        st.plotly_chart(fig_pie)

        # Line chart for duration of recent runs
        recent_runs = filtered_df[['Execution Date', 'Total Execution Time', 'Job Name']].copy()
        
        # Handle NaN in execution time and convert to integer for plotting
        def convert_to_seconds(time_str):
            if pd.isnull(time_str):
                return 0
            total_seconds = 0
            # Use regex to find hours, minutes, and seconds
            matches = re.findall(r'(\d+\.?\d*)\s*(Hr|Min|Sec)', time_str)
            for value, unit in matches:
                if unit.lower() == 'hr':
                    total_seconds += float(value) * 3600  # Convert hours to seconds
                elif unit.lower() == 'min':
                    total_seconds += float(value) * 60  # Convert minutes to seconds
                elif unit.lower() == 'sec':
                    total_seconds += float(value)  # Seconds
            return total_seconds/1000

# Apply the conversion function to the DataFrame column
        recent_runs['Total Execution Time'] = recent_runs['Total Execution Time'].apply(convert_to_seconds)
        recent_runs['Execution Date'] = recent_runs['Execution Date'].dt.strftime('%Y-%m-%d')
        recent_runs['Execution Date and Job'] = recent_runs['Execution Date'] + " - " + recent_runs['Job Name']
        
        fig_line = px.line(
            recent_runs, 
            x='Execution Date', 
            y='Total Execution Time',
            color='Job Name',
            title="Execution Time of Recent DAG Runs", 
            labels={'Execution Date': 'Date', 'Total Execution Time': 'Execution Time (seconds)'},
            markers=True,
            hover_data={'Execution Date':False,'Job Name':True}, # Include DAG Name in hover data 
        )
        # Set opacity using update_traces
        fig_line.update_traces(opacity=0.7)  # Set transparency for all traces

        st.plotly_chart(fig_line)
    else:
        st.warning("No data available for visualization.")

# Tab 3: Email Notifications
with tab3:
    st.markdown("### Email Notifications")

    # Summary Metrics
    total_dags = filtered_df['Job Name'].nunique()
    total_runs = len(filtered_df)
    successful_runs = len(filtered_df[filtered_df['Status'] == 'success'])
    failed_runs = len(filtered_df[filtered_df['Status'] == 'failed'])

    # Display summary cards
    st.markdown("### Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total DAGs", total_dags)
    with col2:
        st.metric("Total Runs", total_runs)
    with col3:
        st.metric("Successful Runs", successful_runs)
    with col4:
        st.metric("Failed Runs", failed_runs)

    # HTML formatting for summary cards
    summary_html = f"""
    <html>
    <body>
        <h2>DAG Run Summary</h2>
        <ul>
            <li><strong>Total DAGs:</strong> {total_dags}</li>
            <li><strong>Total Runs:</strong> {total_runs}</li>
            <li><strong>Successful Runs:</strong> {successful_runs}</li>
            <li><strong>Failed Runs:</strong> {failed_runs}</li>
        </ul>
    </body>
    </html>
    """

    # Convert the filtered dataframe to an HTML table
    if st.button("Send DAG Run Status Email"):
        subject = "Recent DAG Run Status"
        html_table = filtered_df.to_html(index=False)
        # Create the email body with some additional styling (optional)
        email_body = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                h2 {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <h2>DAG Run Status Report</h2>
            {summary_html}
            <br>
            <h2>Detailed DAG Run Table</h2>
            {html_table}
        </body>
        </html>
        """
        # Send the email with the summary and table
        send_email(subject, email_body)
    # Define the function to be called by the scheduler
    def scheduled_email_job():
        # Fetch filtered DAG data for email
        filtered_df = fetch_dag_runs()

        subject = "Scheduled DAG Run Status Report"

        # HTML format for summary
        total_dags = filtered_df['Job Name'].nunique()
        total_runs = len(filtered_df)
        successful_runs = len(filtered_df[filtered_df['Status'] == 'success'])
        failed_runs = len(filtered_df[filtered_df['Status'] == 'failed'])

        summary_html = f"""
        <html>
        <body>
            <h2>DAG Run Summary</h2>
            <ul>
                <li><strong>Total DAGs:</strong> {total_dags}</li>
                <li><strong>Total Runs:</strong> {total_runs}</li>
                <li><strong>Successful Runs:</strong> {successful_runs}</li>
                <li><strong>Failed Runs:</strong> {failed_runs}</li>
            </ul>
        </body>
        </html>
        """

        # Convert the filtered dataframe to an HTML table
        html_table = filtered_df.to_html(index=False)

        # Create the email body with summary and detailed DAG run data
        email_body = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                h2 {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <h2>DAG Run Status Report</h2>
            {summary_html}
            <br>
            <h2>Detailed DAG Run Table</h2>
            {html_table}
        </body>
        </html>
        """
        # Send the email
        send_email(subject,email_body)
    # Initialize the Background Scheduler
    scheduler = BackgroundScheduler()
    # Schedule the email job to run daily at a specific time (e.g., 9 AM IST) or every minute for testing
    scheduler.add_job(scheduled_email_job, 'cron', hour=00, minute=56)  # Use cron for daily scheduling
    # Start the scheduler
    scheduler.start()