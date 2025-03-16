# ITSM Ticket Analysis Dashboard

A web-based dashboard for analyzing ITSM ticket data, built with Python Flask and Plotly.

## Features

- Upload and compare weekly ITSM ticket data
- Interactive visualizations:
  - Weekly ticket count comparison
  - New tickets distribution by site
  - New tickets distribution by priority
  - Weekly ticket distribution with year filtering
- Modern and responsive UI
- Support for Excel file uploads
- Data filtering from 2022 onwards

## Technical Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Data Visualization: Plotly.js
- Data Processing: Pandas

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python app.py
```
4. Access the dashboard at `http://localhost:3000`

## Usage

1. Prepare two Excel files containing ITSM ticket data:
   - Last week's data
   - This week's data
2. Upload both files using the web interface
3. View the generated analysis and visualizations

## Data Format Requirements

The Excel files should contain the following columns:
- ID: Ticket identifier
- Created On: Date in DD.MM.YYYY format
- Site: Location information
- Priority: Ticket priority level 