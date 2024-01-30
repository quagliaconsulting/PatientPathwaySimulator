import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

class Patient:
    def __init__(self, patient_id, age, disease):
        self.patient_id = patient_id
        self.age = age
        self.disease = disease
        self.status = "Waiting"
        self.visits = []
        self.visit_count = 0

    def visit_clinic(self, clinic):
        self.visits.append(clinic)

    def visit_pcp(self):
        self.visits.append("PCP")

    def final_diagnosis(self, outcome):
        self.status = outcome

    def set_referral_options(self, options):
        self.referral_options = options

    def print_status(self):
        print(f"Patient {self.patient_id}: Status - {self.status}, Visits - {self.visit_count}, Path - {self.visits}")

def generate_patients(disease_data, num_patients):
    patients = []
    disease_list = disease_data['Disease List'].tolist()
    patient_distribution = disease_data['Number of Patients'].tolist()
    total_patients = sum(patient_distribution)

    for i, disease in enumerate(disease_list):
        disease_patients = int((patient_distribution[i] / total_patients) * num_patients)
        for _ in range(disease_patients):
            patient_id = len(patients) + 1
            age = random.randint(18, 100)
            patients.append(Patient(patient_id, age, disease))

    return patients

def run_simulation(disease_data, num_patients, mode='test'):
    patients = generate_patients(disease_data, num_patients)

    for patient in patients:
        while patient.status not in ['Correct Diagnosis', 'Incorrect Diagnosis', 'No Diagnosis']:
            if patient.status == 'Waiting':
                patient.visit_count += 1
                disease_row = disease_data[disease_data['Disease List'] == patient.disease]
                pcp_success_rate = disease_row['PCP'].values[0] / 100
                referral_options = disease_row.columns[2:-1].tolist()
                patient.set_referral_options(referral_options)

                patient.visit_pcp()

                if random.random() <= pcp_success_rate:
                    patient.final_diagnosis('Correct Diagnosis')
                else:
                    if random.random() > 0.9:
                        patient.final_diagnosis('Incorrect Diagnosis')
                    else:
                        patient.status = 'Referred'
                patient.print_status()

            elif patient.status == 'Referred':
                patient.visit_count += 1
                disease_row = disease_data[disease_data['Disease List'] == patient.disease]
                clinic_probabilities = disease_row.iloc[0, 2:-1] / 100
                clinic_probabilities = clinic_probabilities.sort_values(ascending=False)
                unvisited_clinics = clinic_probabilities.index.difference(patient.visits)

                if unvisited_clinics.empty:
                    patient.final_diagnosis('No Diagnosis')
                    continue

                if mode == 'test':
                    referral_clinic = unvisited_clinics[0]
                else:
                    referral_clinic = random.choice(unvisited_clinics.tolist())

                patient.visit_clinic(referral_clinic)

                clinic_success_rate = clinic_probabilities[referral_clinic]

                if random.random() <= clinic_success_rate:
                    patient.final_diagnosis('Correct Diagnosis')
                else:
                    if random.random() > 0.9:
                        patient.final_diagnosis('Incorrect Diagnosis')
                    else:
                        patient.status = 'Waiting'

    results = {
        'Total Patients': len(patients),
        'Correctly Diagnosed': sum(p.status == 'Correct Diagnosis' for p in patients),
        'Incorrectly Diagnosed': sum(p.status == 'Incorrect Diagnosis' for p in patients),
        'No Diagnosis': sum(p.status == 'No Diagnosis' for p in patients),
        'Average Visits': sum(p.visit_count for p in patients) / len(patients)
    }

    return results, patients

def plot_combined_results(test_results, control_results):
    data = {
        "Mode": ["Test"] * 3 + ["Control"] * 3,
        "Outcomes": ["Correct Diagnosis", "Incorrect Diagnosis", "No Diagnosis"] * 2,
        "Count": [test_results[k] for k in ["Correctly Diagnosed", "Incorrectly Diagnosed", "No Diagnosis"]] + 
                 [control_results[k] for k in ["Correctly Diagnosed", "Incorrectly Diagnosed", "No Diagnosis"]]
    }
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Outcomes', y='Count', color='Mode', barmode='group', title="Simulation Results: Test vs Control")

    return fig

def calculate_percentage_change(test_val, control_val):

    return ((test_val - control_val) / control_val) * 100 if control_val else float('inf')

def visualize_patient_pathway(patient):
    # Nodes for each unique location and final status
    unique_locations = list(set(patient.visits + [patient.status]))
    labels = unique_locations

    # Edges for transitions between locations
    edges = list(zip(patient.visits, patient.visits[1:] + [patient.status]))

    # Creating nodes and edges for the network graph
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    for i, label in enumerate(labels):
        node_x.append(i)
        node_y.append(0)

    for edge in edges:
        x0, y0 = node_x[labels.index(edge[0])], node_y[labels.index(edge[0])]
        x1, y1 = node_x[labels.index(edge[1])], node_y[labels.index(edge[1])]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines'
    )

    node_trace = go.Scatter(
        x=node_x, y=node_y, text=labels, mode='markers+text', hoverinfo='text', marker=dict(size=10)
    )

    # Creating the figure
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=dict(text="Patient Pathway Network Graph"),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode='closest'
    ))

    return fig


def main():
    st.title('Patient Pathway Simulation')

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        disease_data = pd.read_excel(uploaded_file)
        num_patients = int(disease_data['Number of Patients'].sum())

        test_results, test_patients = run_simulation(disease_data, num_patients, mode='test')
        control_results, control_patients = run_simulation(disease_data, num_patients, mode='control')

        # Now use test_results and control_results as before
        st.plotly_chart(plot_combined_results(test_results, control_results))

        # Reporting Observations with Percentage Changes
        st.write("## Observations")
        st.write("### Diagnostic Accuracy Changes")
        test_correct_pct = (test_results['Correctly Diagnosed'] / num_patients) * 100
        control_correct_pct = (control_results['Correctly Diagnosed'] / num_patients) * 100
        accuracy_change_pct = calculate_percentage_change(test_correct_pct, control_correct_pct)
        st.write(f"Test Mode - Correct Diagnoses: {test_correct_pct:.2f}%")
        st.write(f"Control Mode - Correct Diagnoses: {control_correct_pct:.2f}%")
        st.write(f"Percentage Change: {accuracy_change_pct:.2f}%")

        st.write("### Average Visits")
        avg_visits_change_pct = calculate_percentage_change(test_results['Average Visits'], control_results['Average Visits'])
        st.write(f"Test Mode - Average Visits: {test_results['Average Visits']:.2f}")
        st.write(f"Control Mode - Average Visits: {control_results['Average Visits']:.2f}")
        st.write(f"Percentage Change: {avg_visits_change_pct:.2f}%")

        # Section for individual patient pathway visualization
        st.write("## Individual Patient Pathway Visualization")
        if uploaded_file is not None and num_patients:
            group = st.radio("Choose Group for Pathway Visualization", ("Test Group", "Control Group"))
            if group == "Test Group":
                patient_list = test_patients
            else:
                patient_list = control_patients

            patient_id_to_visualize = st.selectbox("Select Patient ID", range(1, num_patients + 1))
            selected_patient = next(p for p in patient_list if p.patient_id == patient_id_to_visualize)
            st.plotly_chart(visualize_patient_pathway(selected_patient))

if __name__ == "__main__":
    main()