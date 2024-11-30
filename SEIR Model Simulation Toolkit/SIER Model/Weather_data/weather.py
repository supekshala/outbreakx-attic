from weather_generator import WeatherDataGenerator, generate_weather_data
from datetime import datetime
import os

def run_weather_simulation():
    """Run weather simulation with user input"""
    try:
        print("\n" + "="*50)
        print("COLOMBO WEATHER SIMULATION SYSTEM")
        print("="*50 + "\n")
        
        # Get simulation parameters from user
        start_date_str = input("Enter start date (YYYY-MM-DD) or press Enter for current date: ").strip()
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            start_date = datetime.now()
            
        duration = input("Enter simulation duration in days (default: 100): ").strip()
        duration_days = int(duration) if duration else 100
        
        print("\n" + "-"*50)
        print("Simulation Parameters:")
        print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
        print(f"Duration: {duration_days} days")
        print("-"*50 + "\n")
        
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(__file__), 'output', f'weather_sim_{timestamp}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize and run simulation
        print("Initializing weather simulation...")
        generator = WeatherDataGenerator(
            start_date=start_date,
            duration_days=duration_days
        )
        
        print("Running simulation...")
        weather_df = generator.save_weather_data(output_dir=output_dir)
        
        print("\n" + "="*50)
        print("SIMULATION COMPLETED")
        print("="*50)
        print(f"Data saved to: {output_dir}")
        print(f"Time range: {weather_df['timestamp'].min()} to {weather_df['timestamp'].max()}")
        print("="*50 + "\n")
        
        return weather_df
        
    except ValueError as ve:
        print(f"\nError: Invalid input - {str(ve)}")
        return None
    except Exception as e:
        print(f"\nError in weather simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Ask user which mode to run
    print("\nWeather Simulation Modes:")
    print("1. Interactive (with custom parameters)")
    print("2. Default (100 days from current date)")
    
    mode = input("\nSelect mode (1 or 2): ").strip()
    
    if mode == "1":
        weather_df = run_weather_simulation()
    else:
        weather_df = generate_weather_data()