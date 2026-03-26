# KPI Dashboard (Streamlit)

Interactive dashboard developed in **Python and Streamlit** for monitoring operational and performance indicators.

The application demonstrates how to build a lightweight analytics dashboard capable of retrieving external datasets, processing structured indicators and generating dynamic visualizations for decision support.

## Features

The dashboard provides:

* Executive **KPI summary metrics**
* **Progress curve visualization**
* **Operational indicators monitoring**
* **Performance status indicators**
* Automatic **data refresh**
* Interactive **data exploration**

The architecture allows the dashboard to connect to external data sources and automatically update visualizations when the dataset changes.

## Technologies

* Python
* Streamlit
* Pandas
* Plotly
* OpenPyXL
* Requests

## Project Structure

```text
Dash_KPI_264/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Running the Application

Clone the repository:

```bash
git clone https://github.com/AndresJLaraA/Dash_KPI_264.git
cd Dash_KPI_264
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

The application will open automatically in your browser.

## Data

This repository **does not contain operational datasets**.

The application is designed to connect to **external data sources**, which are intentionally excluded from this repository for confidentiality and security reasons.

Users interested in testing the application can adapt the data loading section to connect to their own dataset.

## Deployment

The application can be deployed using platforms such as:

* Streamlit Community Cloud
* Docker
* Local Python environments

## Disclaimer

This repository is intended for **demonstration and development purposes**.
No proprietary data or confidential information is included.

## Author

**Andrés J. Lara**

Financial engineer focused on:

* Data analytics
* Process automation
* Decision-support systems
* Applied AI in finance
