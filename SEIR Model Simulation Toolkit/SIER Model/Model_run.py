from SIER_Model import DengueOutbreakSimulation, run_dengue_simulation
import matplotlib.pyplot as plt

# Initialize simulation with your specified parameters
simulation = DengueOutbreakSimulation(
    beta=0.3,    # Infection rate
    sigma=0.2,   # Incubation rate (1/latent period)
    gamma=0.1,   # Recovery rate (1/infectious period)
    N=10000,     # Total population size
    E0=100,      # Initial exposed population
    I0=0,        # Initial infected population
    R0=0,        # Initial recovered population
    duration_days=100  # Simulation duration
)

# Run the simulation
df, seir_data = simulation.run_simulation()

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(seir_data['S'], label='Susceptible')
plt.plot(seir_data['E'], label='Exposed')
plt.plot(seir_data['I'], label='Infected')
plt.plot(seir_data['R'], label='Recovered')

plt.title('SEIR Model Simulation Results')
plt.xlabel('Time (days)')
plt.ylabel('Population')
plt.legend()
plt.grid(True)
plt.show()

# Save the results
simulation.save_data(df, seir_data, output_dir='output/')