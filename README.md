`# Patient Pathway Simulation

## Overview

This Streamlit application simulates patient pathways in a healthcare setting, focusing on the journey of patients through different healthcare services until they receive a diagnosis. It's designed to analyze the efficiency and effectiveness of patient referrals and diagnoses in both test and control scenarios.

## Features

- **Patient Simulation**: Generates patient profiles based on diseases and simulates their pathway through healthcare services.
- **Dynamic Parameters**: Includes "cowboy factors" for PCP and clinics, allowing for simulation of diagnostic accuracy under various conditions.
- **Data Visualization**: Utilizes Plotly to visualize patient pathways and outcomes, offering insights into the patient journey.
- **Comparative Analysis**: Compares test and control groups to evaluate different referral strategies.
- **User Inputs**: Allows users to input parameters like cowboy factors and patient data through a simple interface.

## Setup and Installation

1. **Install Streamlit**: If you haven't installed Streamlit, you can do it via pip:
   ```bash
   pip install streamlit` 

2.  **Install Plotly**: For data visualization, ensure Plotly is installed:
    
    bashCopy code
    
    `pip install plotly` 
    
3.  **Install Pandas**: Pandas is required for data handling:
    
    bashCopy code
    
    `pip install pandas` 
    
4.  **Run the Application**: Navigate to the directory containing the application script (`patient_pathway.py`) and run:
    
    bashCopy code
    
    `streamlit run patient_pathway.py` 
    

## Usage

-   **Upload Data**: Start by uploading an Excel file containing the disease data and patient distribution.
-   **Set Cowboy Factors**: Adjust the PCP and Clinic Cowboy Factors to simulate different levels of diagnostic uncertainty.
-   **Run Simulation**: Initiate the simulation to see how patients are diagnosed in both test and control scenarios.
-   **View Results**: Analyze the results through the displayed graphs and statistics.

## Contributions

This project is open for contributions, suggestions, and feedback. Feel free to fork the repository or submit issues and pull requests. """