
# Medical Diagnosis Simulation

This Python script simulates the process of patient diagnosis in a medical setting. It models the journey of patients through primary care physicians (PCPs) and various specialist clinics to understand the efficiency and accuracy of medical diagnoses under different conditions.

## Features

1. **Patient Class**: Represents each patient with attributes like ID, age, disease, visit history, and diagnosis status.
2. **Patient Generation**: Generates a set of patients based on disease distribution data.
3. **PCP Diagnosis Simulation**: Simulates the initial diagnosis process by a PCP and determines if a patient is correctly diagnosed, incorrectly diagnosed, or referred to a specialist.
4. **Referral Simulation**: Models the process of referring patients to specialist clinics and tracks the outcome of each visit.
5. **Comparison of Test and Control Groups**: Compares the outcomes of patient journeys under 'test' and 'control' scenarios to evaluate different diagnostic strategies.

## How to Run the Simulation

1. **Prepare Data File**: Ensure you have an Excel file (`Neurology_Sim_Parameters.xlsx`) with the required structure for disease distribution and clinic success rates.
2. **Run Script**: Execute the script. It will read the data file and run the simulation for both test and control groups.

## Script Overview

- `Patient` class: Defines the structure and methods for patient data.
- `generate_patients`: Generates patient objects based on disease distribution.
- `simulate_pcp_diagnosis`: Simulates the diagnosis process at the PCP level.
- `simulate_referrals`: Simulates the referral process to specialist clinics.
- `run_simulation`: Orchestrates the entire simulation process using the above components.

## Simulation Process

1. **Patient Generation**: Based on the input data, patients with various diseases are generated.
2. **PCP Diagnosis**: Each patient visits a PCP. The outcome can be a correct diagnosis, incorrect diagnosis, or a referral to a specialist.
3. **Specialist Referral**: Referred patients visit specialists. The process repeats until a final diagnosis is made or the patient runs out of referral options.

## Output

The script outputs the results of the simulation for both test and control groups, including the total number of patients, the number correctly and incorrectly diagnosed, those who received no diagnosis, and the average number of visits per patient.

## Dependencies

- Python 3.x
- Pandas (`pandas` library)
- Random (`random` library)

## Usage Example

```python
file_path = 'Neurology_Sim_Parameters.xlsx'
test_results, control_results = run_simulation(file_path)
print("Test Set Results:", test_results)
print("Control Set Results:", control_results)
```

## License

[Specify the license under which this script is released, if applicable]

