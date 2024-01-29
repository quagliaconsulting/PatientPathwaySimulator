import random
import plotly.express as px
import plotly.graph_objects as go

# Function to generate patients
def generate_patients(num_patients):
    return ['Patient_' + str(i) for i in range(num_patients)]

# Function to generate diseases and doctors
def generate_entities(num, prefix):
    return [f'{prefix}_{i}' for i in range(1, num + 1)]

# Function to assign diseases to patients
def assign_diseases(patients, diseases):
    return {patient: random.choice(diseases) for patient in patients}

# Function to assign doctors to patients randomly (control group)
def assign_doctors_randomly(patients, doctors):
    return {patient: random.choice(doctors) for patient in patients}

# Function to create a dynamic doctor-disease probability matrix
def create_probability_matrix(num_doctors, num_diseases):
    matrix = {}
    max_success_rate = 0.95  # Maximum success rate

    for i in range(num_doctors):
        for j in range(num_diseases):
            doctor = f'Doctor_{i+1}'
            disease = f'Disease_{j+1}'

            # Calculate success rate based on the difference between doctor and disease indices
            index_difference = abs(i - j)
            success_rate = max_success_rate * (1 - (index_difference / num_diseases))

            matrix[(doctor, disease)] = success_rate
    return matrix

# Function to assign doctors to patients based on specialization with a given probability
def assign_doctors_specialized(patients, patient_diseases, doctors, perfect_assignment_prob):
    doctor_specialization = {f'Disease_{i+1}': f'Doctor_{i+1}' for i in range(len(doctors))}
    assigned_doctors = {}

    for patient in patients:
        if random.random() < perfect_assignment_prob:
            # Assign the specialized doctor
            assigned_doctors[patient] = doctor_specialization[patient_diseases[patient]]
        else:
            # Assign a random doctor
            assigned_doctors[patient] = random.choice(doctors)

    return assigned_doctors

# Function to simulate diagnosis with specialized doctors
def diagnose_with_specialization(patient_doctors, patient_diseases, doctor_success_rate):
    outcomes = {}
    for patient, doctor in patient_doctors.items():
        disease = patient_diseases[patient]
        success_rate = doctor_success_rate[(doctor, disease)]
        outcomes[patient] = 'Lives' if random.random() < success_rate else 'Dies'
    return outcomes

# Visualization function for disease assignment
def visualize_disease_assignment(patient_diseases, title):
    diseases = list(patient_diseases.values())
    fig = px.histogram(diseases, title=title)
    fig.show()

# Visualization function for doctor assignment
def visualize_doctor_assignment(patient_doctors, title):
    doctor_assignments = list(patient_doctors.values())
    fig = px.histogram(doctor_assignments, title=title)
    fig.show()    

# Visualization function for comparing outcomes
def visualize_comparison(control_outcomes, test_outcomes, title):
    control_survival = sum(outcome == 'Lives' for outcome in control_outcomes.values())
    test_survival = sum(outcome == 'Lives' for outcome in test_outcomes.values())
    control_death = len(control_outcomes) - control_survival
    test_death = len(test_outcomes) - test_survival

    categories = ['Lives', 'Dies']
    control_data = [control_survival, control_death]
    test_data = [test_survival, test_death]

    fig = go.Figure(data=[
        go.Bar(name='Control', x=categories, y=control_data),
        go.Bar(name='Test', x=categories, y=test_data)
    ])

    # Change the bar mode
    fig.update_layout(barmode='group', title=title)
    fig.show()

def run_simulation(num_patients, num_doctors, num_diseases, specialized, perfect_assignment_prob=1.0):
    patients = generate_patients(num_patients)
    diseases = generate_entities(num_diseases, 'Disease')
    doctors = generate_entities(num_doctors, 'Doctor')
    patient_diseases = assign_diseases(patients, diseases)

    doctor_success_rate = create_probability_matrix(num_doctors, num_diseases)

    if specialized:
        patient_doctors = assign_doctors_specialized(patients, patient_diseases, doctors, perfect_assignment_prob)
    else:
        patient_doctors = assign_doctors_randomly(patients, doctors)

    outcomes = diagnose_with_specialization(patient_doctors, patient_diseases, doctor_success_rate)
    return patient_doctors, outcomes

def main():
    num_patients = int(input("Enter the number of patients: "))
    num_diseases = int(input("Enter the number of diseases: "))
    num_doctors = int(input("Enter the number of doctors: "))
    perfect_assignment_prob = float(input("Enter the probability of perfect doctor assignment (0 to 1): "))

    # Run simulation for control group (random assignment)
    control_doctors, control_outcomes = run_simulation(num_patients, num_doctors, num_diseases, specialized=False)
    visualize_doctor_assignment(control_doctors, "Control Group Doctor Assignments")

    # Run simulation for test group (specialized assignment with user-defined probability)
    test_doctors, test_outcomes = run_simulation(num_patients, num_doctors, num_diseases, specialized=True, perfect_assignment_prob=perfect_assignment_prob)
    visualize_doctor_assignment(test_doctors, "Test Group Doctor Assignments")

    visualize_comparison(control_outcomes, test_outcomes, "Comparison of Patient Outcomes")

if __name__ == "__main__":
    main()