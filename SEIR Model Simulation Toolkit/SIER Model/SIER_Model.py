import numpy as np
import pandas as pd
from scipy.integrate import odeint
from datetime import datetime, timedelta
import random
import uuid
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns

class DengueOutbreakSimulation:
    def __init__(self, duration_days=100, N=1000000, I0=100, R0=0, E0=0,
                 beta=0.4, sigma=1/5.5, gamma=1/7,
                 center_lat=6.9271, center_lon=79.8612, radius_km=20):
        if N <= 0 or I0 < 0 or R0 < 0 or E0 < 0:
            raise ValueError("Population and initial values must be non-negative")
        if I0 + R0 + E0 > N:
            raise ValueError("Sum of I0, R0, and E0 cannot exceed total population N")
        
        self.duration_days = duration_days
        self.N = N
        self.I0 = I0
        self.R0 = R0
        self.E0 = E0
        self.S0 = N - I0 - R0 - E0
        self.beta = beta
        self.sigma = sigma
        self.gamma = gamma
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km

    def seir_model(self, y, t, N, beta, sigma, gamma):
        S, E, I, R = y
        dSdt = -beta * S * I / N
        dEdt = beta * S * I / N - sigma * E
        dIdt = sigma * E - gamma * I
        dRdt = gamma * I
        return dSdt, dEdt, dIdt, dRdt

    def run_simulation(self):
        t = np.linspace(0, self.duration_days, self.duration_days + 1)
        y0 = self.S0, self.E0, self.I0, self.R0
        ret = odeint(self.seir_model, y0, t, args=(self.N, self.beta, self.sigma, self.gamma))
        S, E, I, R = ret.T

        seir_data = pd.DataFrame({
            't': t,
            'S': S,
            'E': E,
            'I': I,
            'R': R
        })

        df = self.generate_patient_data(I)
        return df, seir_data

    def generate_patient_data(self, I):
        start_date = datetime.now()
        data = []
        patient_counter = 1  # Initialize counter for patient IDs

        for day, infected in enumerate(I):
            new_cases = max(0, int(infected) - (int(I[day-1]) if day > 0 else self.I0))
            if new_cases > 0:
                for _ in range(new_cases):
                    # Generate location for each patient
                    lat, lon = self.generate_random_location()
                    
                    # Generate patient ID (using Option 1: Simple numeric ID with prefix)
                    patient_id = f"P{patient_counter:05d}"  # P00001, P00002, etc.
                    
                    data.append({
                        'patient_id': patient_id,
                        'timestamp': start_date + timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                        'age': random.randint(1, 90),
                        'severity': random.choices(['Mild', 'Moderate', 'Severe'], weights=[0.7, 0.25, 0.05])[0],
                        'latitude': lat,
                        'longitude': lon
                    })
                    patient_counter += 1

        return pd.DataFrame(data)

    def generate_random_location(self):
        """
        Generate random coordinates within specified radius around Colombo, Sri Lanka
        Returns latitude and longitude within city limits
        """
        # Colombo city limits (approximately)
        COLOMBO_BOUNDS = {
            'min_lat': 6.8500,  # Southern boundary
            'max_lat': 6.9800,  # Northern boundary
            'min_lon': 79.8200,  # Western boundary
            'max_lon': 79.9000   # Eastern boundary
        }
        
        while True:
            r = self.radius_km * np.sqrt(random.random())
            theta = random.random() * 2 * np.pi
            
            dx = r * np.cos(theta)
            dy = r * np.sin(theta)
            
            lat = self.center_lat + (dy / 111.32)
            lon = self.center_lon + (dx / (111.32 * np.cos(np.radians(self.center_lat))))
            
            # Check if the generated point is within Colombo city limits
            if (COLOMBO_BOUNDS['min_lat'] <= lat <= COLOMBO_BOUNDS['max_lat'] and 
                COLOMBO_BOUNDS['min_lon'] <= lon <= COLOMBO_BOUNDS['max_lon']):
                return lat, lon

    def create_summary_visualizations(self, seir_data, output_dir):
        plt.figure(figsize=(10, 6))
        plt.plot(seir_data['t'], seir_data['S']/self.N, 'b', label='Susceptible')
        plt.plot(seir_data['t'], seir_data['E']/self.N, 'y', label='Exposed')
        plt.plot(seir_data['t'], seir_data['I']/self.N, 'r', label='Infectious')
        plt.plot(seir_data['t'], seir_data['R']/self.N, 'g', label='Recovered')
        plt.xlabel('Days')
        plt.ylabel('Proportion of Population')
        plt.title('SEIR Model Progression')
        plt.legend()
        plt.grid(True)
        seir_plot_path = f"{output_dir}seir_curve.png"
        plt.savefig(seir_plot_path)
        plt.close()
        return seir_plot_path

    def generate_pdf_reports(self, df, seir_data, output_dir='data/'):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # First, create the SEIR plot and save it
            seir_plot_path = self.create_summary_visualizations(seir_data, output_dir)
            print(f"SEIR plot saved to: {seir_plot_path}")

            # Initialize ReportLab styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=30
            )

            # Generate Summary PDF
            print("Generating summary PDF...")
            summary_pdf_path = os.path.join(output_dir, 'dengue_outbreak_summary.pdf')
            doc = SimpleDocTemplate(
                summary_pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            elements = []
            elements.append(Paragraph("Dengue Outbreak Simulation Summary", title_style))
            elements.append(Paragraph(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 20))

            param_data = [
                ["Parameter", "Value"],
                ["Total Population", f"{self.N:,}"],
                ["Simulation Duration", f"{self.duration_days} days"],
                ["Total Cases", f"{len(df):,}"],
                ["Initial Infected", f"{self.I0:,}"],
                ["Transmission Rate (β)", f"{self.beta:.3f}"],
                ["Incubation Rate (σ)", f"{self.sigma:.3f}"],
                ["Recovery Rate (γ)", f"{self.gamma:.3f}"],
            ]
            param_table = Table(param_data, colWidths=[200, 200])
            param_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(param_table)
            elements.append(Spacer(1, 20))

            seir_plot_path = self.create_summary_visualizations(seir_data, output_dir)
            elements.append(Image(seir_plot_path, width=6*inch, height=4*inch))
            elements.append(Spacer(1, 20))

            elements.append(Paragraph("Key Statistics:", styles['Heading2']))
            severity_counts = df['severity'].value_counts()
            
            stats_data = [
                ["Statistic", "Value"],
                ["Average Age", f"{df['age'].mean():.1f}"],
                ["Age Range", f"{df['age'].min()} - {df['age'].max()}"],
                ["Mild Cases", f"{severity_counts.get('Mild', 0)}"],
                ["Moderate Cases", f"{severity_counts.get('Moderate', 0)}"],
                ["Severe Cases", f"{severity_counts.get('Severe', 0)}"],
            ]
            
            stats_table = Table(stats_data, colWidths=[200, 200])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(stats_table)

            # Build the document
            doc.build(elements)
            print(f"Summary PDF saved to: {summary_pdf_path}")

            # Generate Detailed PDF
            print("Generating detailed PDF...")
            detailed_pdf_path = os.path.join(output_dir, 'dengue_outbreak_detailed.pdf')
            doc = SimpleDocTemplate(
                detailed_pdf_path,
                pagesize=landscape(A4),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            elements = []
            elements.append(Paragraph("Dengue Outbreak Detailed Patient Records", title_style))
            elements.append(Paragraph(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 20))

            # Add pagination info
            page_size = 50  # Number of records per page
            total_pages = (len(df) + page_size - 1) // page_size

            # Process data in chunks
            for page in range(total_pages):
                if page > 0:
                    elements.append(PageBreak())
                
                start_idx = page * page_size
                end_idx = min((page + 1) * page_size, len(df))
                df_chunk = df.iloc[start_idx:end_idx].copy()
                
                # Format the data
                df_chunk['timestamp'] = df_chunk['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                df_chunk['latitude'] = df_chunk['latitude'].round(4)
                df_chunk['longitude'] = df_chunk['longitude'].round(4)
                
                # Create table header
                headers = ['Patient ID', 'Date & Time', 'Age', 'Severity', 'Location (Lat, Lon)']
                
                # Prepare data for table
                table_data = [headers]
                for _, row in df_chunk.iterrows():
                    table_data.append([
                        row['patient_id'],
                        row['timestamp'],
                        str(row['age']),
                        row['severity'],
                        f"{row['latitude']}, {row['longitude']}"
                    ])

                # Create and style table
                table = Table(table_data, colWidths=[80, 100, 50, 70, 150])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                ]))
                
                # Add page number
                elements.append(Paragraph(
                    f"Page {page + 1} of {total_pages}",
                    ParagraphStyle('PageNum', parent=styles['Normal'], alignment=TA_CENTER)
                ))
                elements.append(Spacer(1, 10))
                elements.append(table)

            doc.build(elements)
            print(f"Detailed PDF saved to: {detailed_pdf_path}")

        except Exception as e:
            print(f"Error generating PDFs: {str(e)}")
            import traceback
            traceback.print_exc()

    def save_data(self, df, seir_data, output_dir='output/'):
        """Save all simulation data to files"""
        # Ensure output directory exists
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Saving data to: {output_dir}")

        try:
            # Save CSV data
            df.to_csv(os.path.join(output_dir, 'dengue_outbreak_data.csv'), index=False)
            print("CSV data saved successfully")

            # Generate PDFs
            self.generate_pdf_reports(df, seir_data, output_dir)

        except Exception as e:
            print(f"Error in save_data: {str(e)}")
            import traceback
            traceback.print_exc()

def run_dengue_simulation():
    """Run the simulation with timestamped output directory"""
    try:
        print("Starting dengue outbreak simulation...")
        
        # Create simulation instance
        sim = DengueOutbreakSimulation(duration_days=100)
        
        # Run simulation
        df, seir_data = sim.run_simulation()
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, 'output', f'simulation_{timestamp}')
        
        # Save all data
        print(f"\nSaving data to: {output_dir}")
        sim.save_data(df, seir_data, output_dir)
        
        print("\nSimulation complete!")
        print(f"Total cases generated: {len(df)}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Results saved in: {output_dir}")
        
        return df, seir_data
        
    except Exception as e:
        print(f"Error in simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    df, seir_data = run_dengue_simulation()