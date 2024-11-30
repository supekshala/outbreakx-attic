# Import required libraries
from SIER_Model import DiseaseOutbreakSimulation, run_disease_simulation
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Function to run simulation manually with custom parameters
def run_manual_simulation():
    """Run simulation with manual parameters and compressed PDF output"""
    try:
        # Ask for disease name
        disease_name = input("Enter the disease name for simulation: ")
        
        print("\n" + "="*50)
        print(f"DISEASE OUTBREAK SIMULATION: {disease_name.upper()}")
        print("="*50 + "\n")

        # Initialize simulation with epidemiological parameters
        simulation = DiseaseOutbreakSimulation(
            disease_name=disease_name,
            beta=0.3,    
            sigma=0.2,   
            gamma=0.1,   
            N=10000,     
            E0=100,      
            I0=0,        
            R0=0,        
            duration_days=100  
        )

        print("Running simulation...")
        df, seir_data = simulation.run_simulation()
        print("Simulation completed!\n")

        # Create visualization with minimal settings
        plt.figure(figsize=(6, 3), dpi=72)  # Minimal size and DPI
        plt.plot(seir_data['t'], seir_data['S'], label='S', linewidth=1)
        plt.plot(seir_data['t'], seir_data['E'], label='E', linewidth=1)
        plt.plot(seir_data['t'], seir_data['I'], label='I', linewidth=1)
        plt.plot(seir_data['t'], seir_data['R'], label='R', linewidth=1)
        plt.title('SEIR Model', fontsize=8)
        plt.xlabel('Days', fontsize=8)
        plt.ylabel('Population', fontsize=8)
        plt.legend(fontsize=6)
        plt.tick_params(labelsize=6)
        plt.grid(True, alpha=0.3)

        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join('output', f'simulation_{timestamp}')
        os.makedirs(output_dir, exist_ok=True)

        # Save plot with minimal settings
        plt.savefig(
            os.path.join(output_dir, 'seir_plot.png'),
            dpi=72,  # Low DPI for smaller file size
            bbox_inches='tight',
            pad_inches=0.1
        )
        plt.close()

        # Save data with compression
        print("\nSaving compressed data files...")
        
        # Save minimal CSV
        df_minimal = df.copy()
        df_minimal['timestamp'] = df_minimal['timestamp'].dt.strftime('%y-%m-%d')
        df_minimal['latitude'] = df_minimal['latitude'].round(2)
        df_minimal['longitude'] = df_minimal['longitude'].round(2)
        csv_path = os.path.join(output_dir, 'outbreak_data.csv')
        df_minimal.to_csv(csv_path, index=False)

        # Generate compressed PDFs
        summary_pdf, detailed_pdf = simulation.generate_pdf_reports(df, seir_data, output_dir)
        
        if summary_pdf and detailed_pdf:
            print("\nFiles generated successfully:")
            summary_size = os.path.getsize(summary_pdf)/1024
            detailed_size = os.path.getsize(detailed_pdf)/1024
            print(f"Summary PDF: {summary_size:.1f}KB")
            print(f"Detailed PDF: {detailed_size:.1f}KB")
            
            # Print warning if files are large
            if detailed_size > 1024:  # If larger than 1MB
                print("\nNote: Detailed PDF is quite large. Consider reducing the simulation duration or population size for smaller files.")
        
        print(f"\nAll files saved in: {output_dir}")
        
        return df, seir_data

    except Exception as e:
        print(f"Error in manual simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    # Ask user which mode to run
    print("\nSimulation Modes:")
    print("1. Interactive (with user input)")
    print("2. Manual (with predefined parameters)")
    
    while True:
        mode = input("\nSelect mode (1 or 2): ").strip()
        if mode in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    try:
        if mode == "1":
            df, seir_data = run_disease_simulation()
        else:
            df, seir_data = run_manual_simulation()
            
        if df is not None:
            print("\nSimulation completed successfully!")
    except Exception as e:
        print(f"\nError running simulation: {str(e)}")
        traceback.print_exc()