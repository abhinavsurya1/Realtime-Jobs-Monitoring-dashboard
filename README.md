# Real-Time Airflow Jobs Monitoring Dashboard 🚀

A sleek and modern dashboard built using **Streamlit**, designed to monitor and manage **Apache Airflow DAGs** in real time. View job statuses, trigger DAGs on the fly, apply dynamic filters. Backed by **PostgreSQL** and **Docker**, the dashboard delivers a clean, responsive UI styled with **MassMutual's design theme**.

---

## 🛠️ Built With

- **Streamlit** – Fast way to build and deploy data dashboards in Python  
- **Apache Airflow** – Platform to programmatically author, schedule, and monitor workflows  
- **PostgreSQL** – Relational database for storing job metadata  
- **Docker** – Containerization for consistent deployment   
- **MassMutual Theme** – Clean, modern UI styling

---

## 🔧 Project Setup

### Prerequisites

Make sure you have the following installed:

- [Python 3.9+](https://www.python.org/)
- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)

---

### Getting Started

```bash
# Step 1: Clone the repository
git clone https://github.com/your-username/airflow-monitor-dashboard.git

# Step 2: Navigate into the project directory
cd airflow-monitor-dashboard

# Step 3: Create a virtual environment
python -m venv venv && source venv/bin/activate

# Step 4: Install required dependencies
pip install -r requirements.txt

# Step 5: Start the Streamlit app
streamlit run app.py
