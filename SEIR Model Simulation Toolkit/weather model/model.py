import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns

class WeatherDataGenerator:
    def __init__(self, start_date=None, duration_days=100):
        # Colombo city limits (approximately)
        self.COLOMBO_BOUNDS = {
            'min_lat': 6.8500,  # Southern boundary
            'max_lat': 6.9800,  # Northern boundary
            'min_lon': 79.8200,  # Western boundary
            'max_lon': 79.9000   # Eastern boundary
        }
        
        # Monsoon seasons in Colombo
        self.MONSOON_SEASONS = {
            'southwest': {  # May to September
                'start_month': 5,
                'end_month': 9,
                'rainfall_probability': 0.8,
                'rainfall_intensity': {
                    'min': 20,  # mm
                    'max': 150  # mm
                },
                'wind_speed': {
                    'min': 15,  # km/h
                    'max': 45   # km/h
                },
                'humidity': {
                    'min': 75,  # %
                    'max': 95
                }
            },
            'northeast': {  # December to February
                'start_month': 12,
                'end_month': 2,
                'rainfall_probability': 0.6,
                'rainfall_intensity': {
                    'min': 10,  # mm
                    'max': 100  # mm
                },
                'wind_speed': {
                    'min': 10,  # km/h
                    'max': 35   # km/h
                },
                'humidity': {
                    'min': 70,  # %
                    'max': 90
                }
            },
            'inter_monsoon': {  # March-April and October-November
                'months': [3, 4, 10, 11],
                'rainfall_probability': 0.4,
                'rainfall_intensity': {
                    'min': 5,   # mm
                    'max': 50   # mm
                },
                'wind_speed': {
                    'min': 5,   # km/h
                    'max': 25   # km/h
                },
                'humidity': {
                    'min': 65,  # %
                    'max': 85
                }
            }
        }
        
        # Base weather parameters (for non-monsoon periods)
        self.BASE_WEATHER = {
            'temperature': {
                'min': 24,  # °C
                'max': 32,
                'night_reduction': 3  # Temperature reduction at night
            },
            'humidity': {
                'min': 60,  # %
                'max': 80
            },
            'rainfall': {
                'probability': 0.2,
                'amount': {
                    'min': 0,  # mm
                    'max': 20
                }
            },
            'wind_speed': {
                'min': 0,  # km/h
                'max': 15
            }
        }
        
        self.start_date = start_date if start_date else datetime.now()
        self.duration_days = duration_days

    def get_season(self, date):
        """Determine the monsoon season for a given date"""
        month = date.month
        
        if 5 <= month <= 9:
            return 'southwest'
        elif month == 12 or 1 <= month <= 2:
            return 'northeast'
        elif month in [3, 4, 10, 11]:
            return 'inter_monsoon'
        else:
            return 'normal'

    def generate_hourly_data(self):
        data = []
        current_date = self.start_date

        for day in range(self.duration_days):
            current_datetime = current_date + timedelta(days=day)
            season = self.get_season(current_datetime)
            
            # Get season-specific parameters
            if season in ['southwest', 'northeast']:
                season_params = self.MONSOON_SEASONS[season]
                rainfall_prob = season_params['rainfall_probability']
                rainfall_range = season_params['rainfall_intensity']
                wind_range = season_params['wind_speed']
                humidity_range = season_params['humidity']
            elif season == 'inter_monsoon':
                season_params = self.MONSOON_SEASONS['inter_monsoon']
                rainfall_prob = season_params['rainfall_probability']
                rainfall_range = season_params['rainfall_intensity']
                wind_range = season_params['wind_speed']
                humidity_range = season_params['humidity']
            else:
                rainfall_prob = self.BASE_WEATHER['rainfall']['probability']
                rainfall_range = self.BASE_WEATHER['rainfall']['amount']
                wind_range = self.BASE_WEATHER['wind_speed']
                humidity_range = self.BASE_WEATHER['humidity']

            # Generate daily base values
            base_temp = random.uniform(
                self.BASE_WEATHER['temperature']['min'],
                self.BASE_WEATHER['temperature']['max']
            )
            is_rainy_day = random.random() < rainfall_prob
            
            for hour in range(24):
                # Temperature variation
                temp_variation = np.sin(np.pi * (hour - 6) / 12) * 3
                if 0 <= hour <= 6 or 18 <= hour <= 23:
                    temp_variation -= self.BASE_WEATHER['temperature']['night_reduction']
                
                temperature = base_temp + temp_variation
                
                # Monsoon effects on temperature
                if season in ['southwest', 'northeast'] and is_rainy_day:
                    temperature -= random.uniform(1, 3)  # Cooling effect during monsoon rain
                
                # Humidity (higher during monsoon)
                humidity = random.uniform(humidity_range['min'], humidity_range['max'])
                if is_rainy_day:
                    humidity += random.uniform(5, 10)
                humidity = min(humidity, 100)
                
                # Rainfall patterns
                rainfall = 0
                if is_rainy_day:
                    # Monsoon rainfall patterns
                    if season in ['southwest', 'northeast']:
                        # Heavy continuous rain with peaks
                        if 6 <= hour <= 18:  # Daytime rain more likely
                            rainfall = random.uniform(
                                rainfall_range['min'],
                                rainfall_range['max']
                            ) * (1 + np.sin(np.pi * hour / 12) * 0.5)
                    else:
                        # Normal rainfall pattern
                        if 12 <= hour <= 18:  # Afternoon rain
                            rainfall = random.uniform(
                                rainfall_range['min'],
                                rainfall_range['max']
                            )
                
                # Wind speed (stronger during monsoons)
                wind_variation = np.sin(np.pi * hour / 12) * 5
                wind_speed = random.uniform(
                    wind_range['min'],
                    wind_range['max']
                ) + wind_variation
                
                # Location
                latitude = random.uniform(
                    self.COLOMBO_BOUNDS['min_lat'],
                    self.COLOMBO_BOUNDS['max_lat']
                )
                longitude = random.uniform(
                    self.COLOMBO_BOUNDS['min_lon'],
                    self.COLOMBO_BOUNDS['max_lon']
                )
                
                data.append({
                    'timestamp': current_datetime + timedelta(hours=hour),
                    'season': season,
                    'latitude': round(latitude, 4),
                    'longitude': round(longitude, 4),
                    'temperature': round(temperature, 1),
                    'humidity': round(humidity, 1),
                    'rainfall': round(rainfall, 1),
                    'wind_speed': round(wind_speed, 1)
                })

        return pd.DataFrame(data)

    def create_weather_visualizations(self, df, output_dir):
        """Create and save weather data visualizations"""
        # Temperature and Rainfall Plot
        plt.figure(figsize=(12, 6))
        
        # Plot temperature
        plt.plot(df['timestamp'], df['temperature'], 'r-', label='Temperature (°C)', alpha=0.7)
        plt.ylabel('Temperature (°C)', color='r')
        plt.tick_params(axis='y', labelcolor='r')
        
        # Plot rainfall on secondary axis
        ax2 = plt.twinx()
        ax2.bar(df['timestamp'], df['rainfall'], alpha=0.3, color='b', label='Rainfall (mm)')
        ax2.set_ylabel('Rainfall (mm)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        
        plt.title('Temperature and Rainfall Over Time')
        plt.xticks(rotation=45)
        
        # Save plot
        plot_path = f"{output_dir}/weather_plot.png"
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
        return plot_path

    def generate_pdf_report(self, df, output_dir):
        """Generate PDF report with weather data summary"""
        try:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(output_dir, f'weather_report_{timestamp}.pdf')
            
            print(f"Creating PDF at: {pdf_path}")
            
            # Initialize PDF with compressed settings
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=landscape(A4),
                rightMargin=10,  # Reduced margins
                leftMargin=10,
                topMargin=15,
                bottomMargin=15,
                compress=True  # Enable compression
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Simplified header with smaller font
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=10,
                spaceAfter=10
            )
            elements.append(Paragraph("Weather Data Report", title_style))
            elements.append(Paragraph(f"Records: {len(df)} | Range: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}", 
                                    ParagraphStyle('Info', fontSize=8)))
            elements.append(Spacer(1, 10))
            
            # Format DataFrame more efficiently
            df_formatted = df.copy()
            
            # Round numbers to fewer decimal places
            df_formatted['temperature'] = df_formatted['temperature'].round(1)
            df_formatted['humidity'] = df_formatted['humidity'].round(1)
            df_formatted['rainfall'] = df_formatted['rainfall'].round(1)
            df_formatted['wind_speed'] = df_formatted['wind_speed'].round(1)
            df_formatted['latitude'] = df_formatted['latitude'].round(3)
            df_formatted['longitude'] = df_formatted['longitude'].round(3)
            
            # Format timestamp more efficiently
            df_formatted['timestamp'] = df_formatted['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Create table data more efficiently
            data = [list(df_formatted.columns)]  # Headers
            data.extend(df_formatted.values.tolist())
            
            # Optimize column widths based on content
            col_widths = [75, 50, 45, 45, 45, 45, 45, 45]  # Optimized widths
            
            table = Table(data, colWidths=col_widths, repeatRows=1)
            
            # Simplified table style
            table.setStyle(TableStyle([
                # Header style - simplified
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 6),  # Reduced font size
                
                # Data style - simplified
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 5),  # Reduced font size
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),  # Thinner, lighter grid
                
                # Minimal padding
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            
            elements.append(table)
            
            # Build PDF with compression
            doc.build(elements)
            
            # Report file size
            file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Convert to MB
            print(f"PDF created successfully at: {pdf_path}")
            print(f"File size: {file_size:.2f} MB")
            
            return pdf_path
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_weather_data(self, output_dir='output/'):
        """Generate and save weather data to CSV and PDF"""
        # Ensure output directory exists
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Saving data to: {output_dir}")

        try:
            # Generate weather data
            weather_df = self.generate_hourly_data()
            
            # Save CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(output_dir, f'weather_data_{timestamp}.csv')
            weather_df.to_csv(csv_path, index=False)
            print(f"CSV data saved to: {csv_path}")
            
            # Generate PDF report
            self.generate_pdf_report(weather_df, output_dir)
            
            return weather_df
            
        except Exception as e:
            print(f"Error saving weather data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def generate_weather_data():
    """Function to run weather data generation"""
    try:
        print("\n" + "="*50)
        print("MONSOON WEATHER DATA GENERATION")
        print("="*50 + "\n")
        
        generator = WeatherDataGenerator()
        print("Generating weather data with monsoon patterns...")
        weather_df = generator.save_weather_data()
        print("Weather data generation completed!\n")
        
        # Print summary statistics by season
        print("Weather Data Summary by Season:")
        print("-"*50)
        for season in weather_df['season'].unique():
            season_data = weather_df[weather_df['season'] == season]
            print(f"\nSeason: {season.upper()}")
            print(f"Temperature Range: {season_data['temperature'].min():.1f}°C to {season_data['temperature'].max():.1f}°C")
            print(f"Average Humidity: {season_data['humidity'].mean():.1f}%")
            print(f"Total Rainfall: {season_data['rainfall'].sum():.1f}mm")
            print(f"Average Wind Speed: {season_data['wind_speed'].mean():.1f}km/h")
        print("-"*50 + "\n")
        
        return weather_df
        
    except Exception as e:
        print(f"Error generating weather data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    weather_df = generate_weather_data()