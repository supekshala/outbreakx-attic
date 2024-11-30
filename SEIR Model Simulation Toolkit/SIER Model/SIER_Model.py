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
from PyPDF2 import PdfReader, PdfWriter
import io

class DiseaseOutbreakSimulation:
    def __init__(self, disease_name="Unknown Disease", duration_days=100, N=2000, I0=100, R0=0, E0=0,
                 beta=0.4, sigma=1/5.5, gamma=1/7,
                 center_lat=6.9271, center_lon=79.8612, radius_km=20, start_date=None):
        if N <= 0 or I0 < 0 or R0 < 0 or E0 < 0:
            raise ValueError("Population and initial values must be non-negative")
        if I0 + R0 + E0 > N:
            raise ValueError("Sum of I0, R0, and E0 cannot exceed total population N")
        
        self.disease_name = disease_name
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
        self.start_date = start_date or datetime.now()

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
        start_date = self.start_date
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
                        'disease_name': self.disease_name,
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

    def compress_pdf(self, input_path, output_path=None):
        """Compress PDF file"""
        try:
            if output_path is None:
                output_path = input_path
            
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Copy pages and compress
            for page in reader.pages:
                page.compress_content_streams()  # This compresses the PDF content
                writer.add_page(page)
            
            # Save compressed PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # Get and print compression ratio
            original_size = os.path.getsize(input_path) / 1024  # KB
            compressed_size = os.path.getsize(output_path) / 1024  # KB
            ratio = (1 - (compressed_size / original_size)) * 100
            
            print(f"Original size: {original_size:.1f} KB")
            print(f"Compressed size: {compressed_size:.1f} KB")
            print(f"Compression ratio: {ratio:.1f}%")
            
            return output_path
            
        except Exception as e:
            print(f"Error compressing PDF: {str(e)}")
            return None

    def generate_pdf_reports(self, df, seir_data, output_dir='data/'):
        """Generate compressed PDF reports with all fields preserved"""
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Initialize styles with minimal settings
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=8,
                alignment=TA_CENTER,
                spaceAfter=5
            )

            # Generate Summary PDF (keeping it minimal)
            summary_pdf_path = os.path.join(output_dir, 'outbreak_summary.pdf')
            doc = SimpleDocTemplate(
                summary_pdf_path,
                pagesize=A4,
                rightMargin=15,
                leftMargin=15,
                topMargin=15,
                bottomMargin=15,
                compress=True,
                pageCompression=1  # Added maximum compression
            )
            
            elements = []
            elements.append(Paragraph(f"{self.disease_name} Outbreak Summary", title_style))
            elements.append(Spacer(1, 5))
            
            # Summary table with minimal formatting
            summary_data = [
                ["Total Population", f"{self.N:,}"],
                ["Duration", f"{self.duration_days} days"],
                ["Total Cases", f"{len(df):,}"],
                ["Date Range", f"{df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[80, 120])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ]))
            elements.append(summary_table)
            doc.build(elements)

            # Generate Detailed PDF with maximum compression
            detailed_pdf_path = os.path.join(output_dir, 'outbreak_detailed.pdf')
            doc = SimpleDocTemplate(
                detailed_pdf_path,
                pagesize=landscape(A4),
                rightMargin=10,
                leftMargin=10,
                topMargin=10,
                bottomMargin=10,
                compress=True,
                pageCompression=1
            )
            
            elements = []
            elements.append(Paragraph(f"{self.disease_name} Detailed Records", title_style))
            elements.append(Spacer(1, 5))
            
            # Add record count
            elements.append(Paragraph(f"Total Records: {len(df):,}", 
                                    ParagraphStyle('Info', fontSize=7, alignment=TA_CENTER)))
            elements.append(Spacer(1, 5))
            
            # Prepare data efficiently
            df_formatted = df.copy()
            df_formatted['timestamp'] = df_formatted['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            df_formatted['latitude'] = df_formatted['latitude'].round(4)
            df_formatted['longitude'] = df_formatted['longitude'].round(4)
            
            # Headers
            headers = ['Patient ID', 'Disease', 'Date & Time', 'Age', 'Severity', 'Latitude', 'Longitude']
            
            # Process in larger chunks for fewer page breaks
            chunk_size = 150  # Increased from 45 to 150 for better compression
            chunks = [df_formatted[i:i + chunk_size] for i in range(0, len(df_formatted), chunk_size)]
            
            # Create table for each chunk
            for chunk in chunks:
                data = [headers]
                for _, row in chunk.iterrows():
                    data.append([
                        row['patient_id'],
                        row['disease_name'],
                        row['timestamp'],
                        str(row['age']),
                        row['severity'],
                        f"{row['latitude']}",
                        f"{row['longitude']}"
                    ])
                
                # Create table with optimized settings
                table = Table(data, colWidths=[60, 45, 70, 25, 45, 45, 45])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7),  # Header font
                    ('FONTSIZE', (0, 1), (-1, -1), 6),  # Data font
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.15, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                
                elements.append(table)
                elements.append(PageBreak())
            
            # Remove last page break
            if elements:
                elements.pop()
            
            # Build PDF with maximum compression
            doc.build(elements)
            
            # After generating the detailed PDF, compress it
            print("\nCompressing detailed PDF...")
            compressed_pdf_path = os.path.join(output_dir, 'outbreak_detailed_compressed.pdf')
            self.compress_pdf(detailed_pdf_path, compressed_pdf_path)
            
            # Replace original with compressed version if smaller
            if os.path.getsize(compressed_pdf_path) < os.path.getsize(detailed_pdf_path):
                os.replace(compressed_pdf_path, detailed_pdf_path)
                print("Using compressed version of detailed PDF")
            else:
                os.remove(compressed_pdf_path)
                print("Original PDF was already optimally compressed")
            
            # Report final file sizes
            summary_size = os.path.getsize(summary_pdf_path) / 1024
            detailed_size = os.path.getsize(detailed_pdf_path) / 1024
            print(f"\nFinal PDF sizes:")
            print(f"Summary PDF: {summary_size:.1f} KB")
            print(f"Detailed PDF: {detailed_size:.1f} KB")
            
            return summary_pdf_path, detailed_pdf_path

        except Exception as e:
            print(f"Error generating PDFs: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

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

def run_disease_simulation():
    """Run the simulation with timestamped output directory and PDF compression"""
    try:
        print("\n" + "="*50)
        print("DISEASE OUTBREAK SIMULATION SYSTEM")
        print("="*50 + "\n")
        
        # Prompt for disease name and start date
        disease_name = input("Enter the disease name for simulation: ")
        while True:
            start_date_str = input("Enter simulation start date (YYYY-MM-DD): ")
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD format.")
        
        print("\n" + "-"*50)
        print(f"Starting simulation for: {disease_name}")
        print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
        print("-"*50 + "\n")
        
        # Create simulation instance
        sim = DiseaseOutbreakSimulation(
            disease_name=disease_name,
            duration_days=100,
            start_date=start_date
        )
        
        # Run simulation
        df, seir_data = sim.run_simulation()
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, 'output', f'simulation_{timestamp}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save CSV data
        csv_path = os.path.join(output_dir, 'outbreak_data.csv')
        df.to_csv(csv_path, index=False)
        print("CSV data saved successfully")
        
        # Generate PDFs with compression
        print("\nGenerating and compressing PDFs...")
        summary_pdf_path = os.path.join(output_dir, 'outbreak_summary.pdf')
        detailed_pdf_path = os.path.join(output_dir, 'outbreak_detailed.pdf')
        
        # Generate initial PDFs
        sim.generate_pdf_reports(df, seir_data, output_dir)
        
        # Compress the detailed PDF
        print("\nApplying additional compression to detailed PDF...")
        compressed_pdf_path = os.path.join(output_dir, 'outbreak_detailed_compressed.pdf')
        
        # Compress using PyPDF2
        reader = PdfReader(detailed_pdf_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.compress_content_streams()  # This compresses the PDF content
            writer.add_page(page)
        
        # Save compressed version
        with open(compressed_pdf_path, "wb") as output_file:
            writer.write(output_file)
        
        # Compare sizes and use the smaller version
        original_size = os.path.getsize(detailed_pdf_path) / 1024  # KB
        compressed_size = os.path.getsize(compressed_pdf_path) / 1024  # KB
        
        if compressed_size < original_size:
            os.replace(compressed_pdf_path, detailed_pdf_path)
            print(f"Compression successful:")
            print(f"Original size: {original_size:.1f} KB")
            print(f"Compressed size: {compressed_size:.1f} KB")
            print(f"Reduction: {((original_size - compressed_size) / original_size * 100):.1f}%")
        else:
            os.remove(compressed_pdf_path)
            print("Original PDF was already optimally compressed")
        
        print("\n" + "="*50)
        print(f"SIMULATION RESULTS FOR: {disease_name.upper()}")
        print("="*50)
        print(f"Total cases generated: {len(df):,}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Results saved in: {output_dir}")
        print("="*50 + "\n")
        
        return df, seir_data
        
    except Exception as e:
        print(f"Error in simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    df, seir_data = run_disease_simulation()