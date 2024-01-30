import pandas as pd
import random
import io
import copy

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

    def final_diagnosis(self, outcome):
        self.status = outcome

    def set_referral_options(self, options):
        self.referral_options = options

    def print_status(self):
        #print(f"Patient {self.patient_id}: Status - {self.status}, Visits - {self.visit_count}, Path - {self.visits}")
        return

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

def run_simulation(file_path, mode='test'):
    clinic_data = pd.read_excel(file_path)
    clinic_data['Number of Patients'] = pd.to_numeric(clinic_data['Number of Patients'], errors='coerce')
    clinic_data['Number of Patients'] = clinic_data['Number of Patients'].fillna(0)
    num_patients = int(clinic_data['Number of Patients'].sum())

    patients = generate_patients(clinic_data, num_patients)

    for patient in patients:
        while patient.status not in ['Correct Diagnosis', 'Incorrect Diagnosis', 'No Diagnosis']:
            if patient.status == 'Waiting':
                patient.visit_count += 1
                disease_row = clinic_data[clinic_data['Disease List'] == patient.disease]
                pcp_success_rate = disease_row['PCP'].values[0] / 100
                referral_options = disease_row.columns[2:-1].tolist()
                patient.set_referral_options(referral_options)

                if random.random() <= pcp_success_rate:
                    patient.final_diagnosis('Correct Diagnosis')
                    #print(f"Patient {patient.patient_id} correctly diagnosed by PCP")
                else:
                    if random.random() > 0.9:
                        patient.final_diagnosis('Incorrect Diagnosis')
                        #print(f"Patient {patient.patient_id} incorrectly diagnosed by PCP")
                    else:
                        patient.status = 'Referred'
                        #print(f"Patient {patient.patient_id} referred by PCP")
                patient.print_status()

            elif patient.status == 'Referred':
                patient.visit_count += 1
                disease_row = clinic_data[clinic_data['Disease List'] == patient.disease]
                clinic_probabilities = disease_row.iloc[0, 2:-1] / 100
                clinic_probabilities = clinic_probabilities.sort_values(ascending=False)
                unvisited_clinics = clinic_probabilities.index.difference(patient.visits)

                if unvisited_clinics.empty:
                    patient.final_diagnosis('No Diagnosis')
                    #print(f"Patient {patient.patient_id} has no diagnosis (no more clinics)")
                    continue

                if mode == 'test':
                    referral_clinic = unvisited_clinics[0]
                else:
                    referral_clinic = random.choice(unvisited_clinics.tolist())

                patient.visit_clinic(referral_clinic)
                #print(f"Patient {patient.patient_id} visiting {referral_clinic}")

                clinic_success_rate = clinic_probabilities[referral_clinic]

                if random.random() <= clinic_success_rate:
                    patient.final_diagnosis('Correct Diagnosis')
                    #print(f"Patient {patient.patient_id} correctly diagnosed at {referral_clinic}")
                else:
                    if random.random() > 0.7:
                        patient.final_diagnosis('Incorrect Diagnosis')
                        #print(f"Patient {patient.patient_id} incorrectly diagnosed at {referral_clinic}")
                    else:
                        patient.status = 'Waiting'
                        #print(f"Patient {patient.patient_id} sent back to PCP from {referral_clinic}")
                patient.print_status()

    # Results Calculation
    results = {
        'Total Patients': len(patients),
        'Correctly Diagnosed': sum(p.status == 'Correct Diagnosis' for p in patients),
        'Incorrectly Diagnosed': sum(p.status == 'Incorrect Diagnosis' for p in patients),
        'No Diagnosis': sum(p.status == 'No Diagnosis' for p in patients),
        'Average Visits': sum(p.visit_count for p in patients) / len(patients)
    }

    return results

file_path = 'Neurology_Sim_Parameters.xlsx'
test_results = run_simulation(file_path, mode='test')
print("Test Set Results:", test_results)
control_results = run_simulation(file_path, mode='control')
print("Control Set Results:", control_results)
