import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

class Patient:
    def __init__(self, patient_id, age, disease, mode='test'):
        self.patient_id = patient_id
        self.age = age
        self.disease = disease
        self.status = "Waiting"
        self.visits = []
        self.visit_count = 0
        self.mode = mode

    def visit_clinic(self, clinic):
        self.visits.append(clinic)

    def visit_pcp(self):
        self.visits.append("PCP")

    def final_diagnosis(self, outcome):
        self.status = outcome

    def set_referral_options(self, options):
        self.referral_options = options

    #TODO: DELETE REDUNDANT CODE BELOW
    def print_status(self):
        print(f"Patient {self.patient_id}: Status - {self.status}, Visits - {self.visit_count}, Path - {self.visits}, Mode - {self.mode}")

def generate_patients(disease_data, num_patients, mode):
    patients = []
    disease_list = disease_data['Disease List'].tolist()
    patient_distribution = disease_data['Number of Patients'].tolist()
    total_patients = sum(patient_distribution)

    for i, disease in enumerate(disease_list):
        disease_patients = int((patient_distribution[i] / total_patients) * num_patients)
        for _ in range(disease_patients):
            patient_id = len(patients) + 1
            age = random.randint(18, 100)
            patients.append(Patient(patient_id, age, disease, mode))

    return patients

def run_simulation(disease_data, num_patients, mode='test', pcp_cowboy_factor=0.95, clinic_cowboy_factor=0.9):
    patients = generate_patients(disease_data, num_patients, mode)

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
                    break
                else:
                    if random.random() > pcp_cowboy_factor:  # Use the PCP cowboy factor
                        patient.final_diagnosis('Incorrect Diagnosis')
                        break
                    
                    # Break loop if a final diagnosis is made
                    if patient.status in ['Correct Diagnosis', 'Incorrect Diagnosis', 'No Diagnosis']:
                        break

                    patient.status = 'Referred'
                #patient.print_status()

            elif patient.status == 'Referred':
                patient.visit_count += 1
                disease_row = disease_data[disease_data['Disease List'] == patient.disease]
                clinic_probabilities = disease_row.iloc[0, 2:-1] / 100
                clinic_probabilities = clinic_probabilities.sort_values(ascending=False)

                # Filter out clinics already visited
                unvisited_clinics = clinic_probabilities.index.difference(patient.visits)

                if unvisited_clinics.empty:
                    patient.final_diagnosis('No Diagnosis')
                    break

                if mode == 'test':
                    # Select the highest probability clinic that hasn't been visited yet
                    for clinic in clinic_probabilities.index:
                        if clinic in unvisited_clinics:
                            referral_clinic = clinic
                            break
                else:
                    referral_clinic = random.choice(unvisited_clinics.tolist())

                patient.visit_clinic(referral_clinic)
                clinic_success_rate = clinic_probabilities[referral_clinic]

                if random.random() <= clinic_success_rate:
                    patient.final_diagnosis('Correct Diagnosis')
                    break
                else:
                    if random.random() > clinic_cowboy_factor:  # Use the clinic cowboy factor
                        patient.final_diagnosis('Incorrect Diagnosis')
                        break

                    #TODO: DELETE REDUNDANT CODE BELOW OR DO IT BY GETTING RID OF ALL THE SINGLE BREAKS
                    # Break loop if a final diagnosis is made
                    if patient.status in ['Correct Diagnosis', 'Incorrect Diagnosis', 'No Diagnosis']:
                        break

                    patient.status = 'Waiting'
                    #patient.print_status()

    results = {
        'Total Patients': len(patients),
        'Correctly Diagnosed': sum(p.status == 'Correct Diagnosis' for p in patients),
        'Incorrectly Diagnosed': sum(p.status == 'Incorrect Diagnosis' for p in patients),
        'No Diagnosis': sum(p.status == 'No Diagnosis' for p in patients),
        'Average Visits': sum(p.visit_count for p in patients) / len(patients)
    }

        # Print patient journeys
    for patient in patients:
            patient.print_status()

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
    # Nodes for each visit and the final status
    pathway_nodes = patient.visits + [patient.status]

    # Creating nodes and edges for the network graph
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []

    # Assign positions
    for i, node in enumerate(pathway_nodes):
        node_x.append(i)  # Incremental x position for each visit
        node_y.append(0)  # Keeping y constant for simplicity

    # Create edges
    for i in range(len(patient.visits)):
        x0, y0 = node_x[i], node_y[i]
        x1, y1 = node_x[i + 1], node_y[i + 1]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_trace = go.Scatter(x=node_x, y=node_y, text=pathway_nodes, mode='markers+text', hoverinfo='text', marker=dict(size=10))

    # Creating the figure with an updated title
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=dict(text=f"Patient Pathway Network Graph - Patient ID: {patient.patient_id}, Disease: {patient.disease}"),
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
        # Add inputs for cowboy factors
        pcp_cowboy_factor = st.number_input('Enter PCP Cowboy Factor (0.0-1.0)', min_value=0.0, max_value=1.0, value=0.95)
        clinic_cowboy_factor = st.number_input('Enter Clinic Cowboy Factor (0.0-1.0)', min_value=0.0, max_value=1.0, value=0.9)
        disease_data = pd.read_excel(uploaded_file)
        num_patients = int(disease_data['Number of Patients'].sum())

        # Pass the cowboy factors to the simulation function
        test_results, test_patients = run_simulation(disease_data, num_patients, 'test', pcp_cowboy_factor, clinic_cowboy_factor)
        control_results, control_patients = run_simulation(disease_data, num_patients, 'control', pcp_cowboy_factor, clinic_cowboy_factor)


        # Assuming test_patients and control_patients have the same length and corresponding patients
        for i in range(len(test_patients)):
            test_patient = test_patients[i]
            control_patient = control_patients[i]

            print(f"Patient {test_patient.patient_id} [Test Mode]: Disease - {test_patient.disease}, Status - {test_patient.status}, Visits - {test_patient.visit_count}, Path - {test_patient.visits}")
            print(f"Patient {control_patient.patient_id} [Control Mode]: Disease - {control_patient.disease}, Status - {control_patient.status}, Visits - {control_patient.visit_count}, Path - {control_patient.visits}")
            print()  # Blank line for better readability
            
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