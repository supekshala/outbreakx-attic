# Import required libraries
from SIER_Model import DengueOutbreakSimulation, run_dengue_simulation
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Initialize simulation with epidemiological parameters
# These parameters model the spread of dengue fever in a population
simulation = DengueOutbreakSimulation(
    beta=0.3,    # Infection rate: probability of disease transmission per contact between S and I
    sigma=0.2,   # Incubation rate: rate at which exposed individuals become infectious (1/latent period)
    gamma=0.1,   # Recovery rate: rate at which infected individuals recover (1/infectious period)
    N=10000,     # Total population size: number of individuals in the simulation
    E0=100,      # Initial exposed population: number of people exposed at start
    I0=0,        # Initial infected population: number of infected people at start
    R0=0,        # Initial recovered population: number of recovered people at start
    duration_days=100  # Length of simulation in days
)

# Execute the simulation
# Returns two objects:
# - df: detailed DataFrame with daily counts
# - seir_data: dictionary containing S, E, I, R populations over time
df, seir_data = simulation.run_simulation()

# Create visualization of the simulation results
plt.figure(figsize=(10, 6))  # Set the plot size to 10x6 inches
# Plot each compartment (S, E, I, R) as a separate line
plt.plot(seir_data['S'], label='Susceptible')  # People who can get infected
plt.plot(seir_data['E'], label='Exposed')      # People who are exposed but not infectious
plt.plot(seir_data['I'], label='Infected')     # People who are infectious
plt.plot(seir_data['R'], label='Recovered')    # People who have recovered and are immune

# Add plot labels and styling
plt.title('SEIR Model Simulation Results')
plt.xlabel('Time (days)')
plt.ylabel('Population')
plt.legend()
plt.grid(True)
plt.show()

# Create timestamped output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join('output', f'simulation_{timestamp}')
os.makedirs(output_dir, exist_ok=True)

# Save the simulation results to files in the timestamped output directory
simulation.save_data(df, seir_data, output_dir=output_dir)