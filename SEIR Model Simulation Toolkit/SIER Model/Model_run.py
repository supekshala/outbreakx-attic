# Import required libraries
from SIER_Model import DiseaseOutbreakSimulation, run_disease_simulation
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Function to run simulation manually with custom parameters
def run_manual_simulation():
    # Ask for disease name instead of hardcoding it
    disease_name = input("Enter the disease name for simulation: ")
    
    print("\n" + "="*50)
    print(f"DISEASE OUTBREAK SIMULATION: {disease_name.upper()}")
    print("="*50 + "\n")

    # Initialize simulation with epidemiological parameters
    simulation = DiseaseOutbreakSimulation(
        disease_name=disease_name,  # Pass the input disease name
        beta=0.3,    
        sigma=0.2,   
        gamma=0.1,   
        N=10000,     
        E0=100,      
        I0=0,        
        R0=0,        
        duration_days=100  
    )

    print("Simulation Parameters:")
    print("-"*50)
    print(f"Disease Name: {disease_name}")
    print(f"Population Size: {10000:,}")
    print(f"Initial Exposed: {100}")
    print(f"Simulation Duration: {100} days")
    print("-"*50 + "\n")

    # Execute the simulation
    print("Running simulation...")
    df, seir_data = simulation.run_simulation()
    print("Simulation completed!\n")

    # Create visualization of the simulation results
    plt.figure(figsize=(10, 6))
    plt.plot(seir_data['t'], seir_data['S'], label='Susceptible')
    plt.plot(seir_data['t'], seir_data['E'], label='Exposed')
    plt.plot(seir_data['t'], seir_data['I'], label='Infected')
    plt.plot(seir_data['t'], seir_data['R'], label='Recovered')

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

    # Save the simulation results
    simulation.save_data(df, seir_data, output_dir=output_dir)

if __name__ == "__main__":
    # Ask user which mode to run
    mode = input("Enter run mode (1 for interactive, 2 for manual parameters): ")
    
    if mode == "1":
        # Run interactive simulation
        df, seir_data = run_disease_simulation()
    else:
        # Run manual simulation with predefined parameters
        run_manual_simulation()