Real-Time Airflow Jobs Monitoring Dashboard

📌 Overview

The Real-Time Airflow Jobs Monitoring Dashboard is a user-friendly web interface designed to track and manage DAG runs in Apache Airflow. Built with Streamlit, the dashboard fetches metadata from PostgreSQL and provides an intuitive view of scheduled, running, and completed DAGs. It offers enhanced visibility into task execution status, failures, and performance metrics in real time.

🚀 Features

Live DAG Monitoring – View active, scheduled, and completed DAG runs with real-time updates.
Clickable DAG IDs – Easily access detailed DAG run information with interactive links.
Customizable Filtering – Use a toggle button to refine DAG views based on status.
Trigger DAG Runs – Start DAG executions directly from the dashboard.
Role-Based Access Control (RBAC) – Secure access with user-specific permissions.
Modern UI – Clean, responsive design using the MassMutual color palette.
🛠️ Tech Stack

Frontend: Streamlit (Python)
Backend: PostgreSQL (Airflow metadata database)
Orchestration: Apache Airflow (Docker)
Deployment: Dockerized environment for seamless integration
📂 Project Structure

/realtime-airflow-dashboard
│── airflow_dashboard.py   # Main Streamlit dashboard file
│── config.py              # Configuration settings
│── db_connector.py        # PostgreSQL connection handler
│── utils.py               # Helper functions
│── Dockerfile             # Docker setup
│── requirements.txt       # Dependencies
└── README.md              # Project documentation
🔧 Setup & Installation

Prerequisites
Docker installed and running
Python 3.x environment
Apache Airflow configured with PostgreSQL metadata database
Steps
Clone the repository:
git clone https://github.com/yourusername/realtime-airflow-dashboard.git
cd realtime-airflow-dashboard
Install dependencies:
pip install -r requirements.txt
Set up environment variables for PostgreSQL connection:
export DB_HOST=your_db_host
export DB_PORT=your_db_port
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password
export DB_NAME=your_db_name
Run the dashboard:
streamlit run airflow_dashboard.py
(Optional) Run using Docker:
docker build -t airflow-dashboard .
docker run -p 8501:8501 --env-file .env airflow-dashboard
🎯 Future Enhancements

Historical DAG Performance Analysis
Error Logging & Notifications
Improved UI/UX with Advanced Filtering
Integration with Other Monitoring Tools
💡 Contributing

Feel free to fork, modify, and contribute to this project by submitting a pull request.
