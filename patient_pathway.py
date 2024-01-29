import pandas as pd
import random
import io
import copy

# Patient class to track each patient's journey
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
        #self.status = "Referred"
        #self.visit_count += 1

    def final_diagnosis(self, outcome):
        self.status = outcome

    def set_referral_options(self, options):
        self.referral_options = options

# Function to generate patients based on the disease distribution in the data
def generate_patients(disease_data, num_patients):
    patients = []
    disease_list = disease_data['Disease List'].tolist()
    patient_distribution = disease_data['Number of Patients'].tolist()
    total_patients = sum(patient_distribution)

    for i, disease in enumerate(disease_list):
        disease_patients = int((patient_distribution[i] / total_patients) * num_patients)
        for _ in range(disease_patients):
            patient_id = len(patients) + 1
            age = random.randint(18, 100)  # Random age for simplicity
            patients.append(Patient(patient_id, age, disease))

    return patients

# Function to simulate the PCP diagnosis process
def simulate_pcp_diagnosis(patients, clinic_data):
    for patient in patients:
        patient.visit_count += 1  # Increment for the PCP visit

        disease_row = clinic_data[clinic_data['Disease List'] == patient.disease]
        pcp_success_rate = disease_row['PCP'].values[0] / 100
        referral_options = disease_row.columns[2:-1].tolist()
        patient.set_referral_options(referral_options)

        if random.random() <= pcp_success_rate:
            patient.final_diagnosis('Correct Diagnosis')
        else:
            # Incorrect diagnosis or referral
            if random.random() > 0.9:
                patient.final_diagnosis('Incorrect Diagnosis')
            else:
                patient.status = 'Referred'

    return patients


# Function to simulate the referral process
def simulate_referrals(patients, clinic_data, mode):
    for patient in patients:
        while patient.status == 'Referred' or patient.status == 'Waiting':
            patient.visit_count += 1  # Incrementing the visit count for every visit

            # Handle referrals or return to PCP
            if patient.status == 'Waiting':
                referral_options = patient.referral_options
                unvisited_clinics = [clinic for clinic in referral_options if clinic not in patient.visits]
                if not unvisited_clinics:
                    patient.final_diagnosis('No Diagnosis')
                    break
            else:
                disease_row = clinic_data[clinic_data['Disease List'] == patient.disease]
                clinic_probabilities = disease_row.iloc[0, 2:-1] / 100
                clinic_probabilities = clinic_probabilities.sort_values(ascending=False)
                unvisited_clinics = clinic_probabilities.index.difference(patient.visits)
                
                if mode == 'test':
                    referral_clinic = unvisited_clinics[0]  # Highest probability clinic
                else:  # 'control' mode
                    referral_clinic = random.choice(unvisited_clinics.tolist())  # Random clinic

            patient.visit_clinic(referral_clinic)
            clinic_success_rate = clinic_probabilities[referral_clinic]

            if random.random() <= clinic_success_rate:
                patient.final_diagnosis('Correct Diagnosis')
            else:
                if random.random() > 0.75:  # Probability of incorrect diagnosis or send back to PCP
                    patient.final_diagnosis('Incorrect Diagnosis')
                else:
                    patient.status = 'Waiting'  # Patient returns to PCP

    return patients

def run_simulation(file_path):
    clinic_data = pd.read_excel(file_path)
    clinic_data['Number of Patients'] = pd.to_numeric(clinic_data['Number of Patients'], errors='coerce')
    clinic_data['Number of Patients'] = clinic_data['Number of Patients'].fillna(0)
    num_patients = int(clinic_data['Number of Patients'].sum())

    patients = generate_patients(clinic_data, num_patients)
    control_patients = [copy.deepcopy(p) for p in patients]

    test_patients = simulate_pcp_diagnosis(patients, clinic_data)
    control_patients = simulate_pcp_diagnosis(control_patients, clinic_data)

    test_patients = simulate_referrals(test_patients, clinic_data, mode='test')
    control_patients = simulate_referrals(control_patients, clinic_data, mode='control')

    test_results = {
        'Total Patients': len(test_patients),
        'Correctly Diagnosed': sum(p.status == 'Correct Diagnosis' for p in test_patients),
        'Incorrectly Diagnosed': sum(p.status == 'Incorrect Diagnosis' for p in test_patients),
        'No Diagnosis': sum(p.status == 'No Diagnosis' for p in test_patients),
        'Average Visits': sum(p.visit_count for p in test_patients) / len(test_patients)
    }

    control_results = {
        'Total Patients': len(control_patients),
        'Correctly Diagnosed': sum(p.status == 'Correct Diagnosis' for p in control_patients),
        'Incorrectly Diagnosed': sum(p.status == 'Incorrect Diagnosis' for p in control_patients),
        'No Diagnosis': sum(p.status == 'No Diagnosis' for p in control_patients),
        'Average Visits': sum(p.visit_count for p in control_patients) / len(control_patients)
    }

    return test_results, control_results

file_path = 'Neurology_Sim_Parameters.xlsx'
test_results, control_results = run_simulation(file_path)
print("Test Set Results:", test_results)
print("Control Set Results:", control_results)