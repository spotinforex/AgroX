import sqlite3
import json
from datetime import datetime
import random

class SoutheastNigeriaSoilDB:
    def __init__(self, db_path=r"C:\Users\SPOT\Documents\AgroX\database\southeast_nigeria_soil.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
        self.populate_initial_data()
    
    def create_tables(self):
        """Create database tables for soil data"""
        cursor = self.conn.cursor()
        
        # States table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Local Government Areas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_governments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                state_id INTEGER,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (state_id) REFERENCES states (id)
            )
        ''')
        
        # Soil Properties table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soil_properties (
                id INTEGER PRIMARY KEY,
                lga_id INTEGER,
                ph_h2o REAL,
                ph_kcl REAL,
                organic_carbon REAL,
                organic_matter REAL,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                sand_content REAL,
                clay_content REAL,
                silt_content REAL,
                bulk_density REAL,
                cation_exchange_capacity REAL,
                soil_depth_cm INTEGER,
                drainage_class TEXT,
                erosion_risk TEXT,
                soil_type TEXT,
                fertility_rating TEXT,
                moisture_retention TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lga_id) REFERENCES local_governments (id)
            )
        ''')
        
        # Crop Suitability table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_suitability (
                id INTEGER PRIMARY KEY,
                lga_id INTEGER,
                crop_name TEXT,
                suitability_score INTEGER,
                constraints TEXT,
                recommendations TEXT,
                FOREIGN KEY (lga_id) REFERENCES local_governments (id)
            )
        ''')
        
        self.conn.commit()
    
    def populate_initial_data(self):
        """Populate database with southeastern Nigeria states and LGAs"""
        cursor = self.conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM states")
        if cursor.fetchone()[0] > 0:
            return
        
        # Southeastern Nigeria states and their LGAs
        southeast_data = {
            "Abia": {
                "code": "AB",
                "lgas": [
                    "Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano",
                    "Isiala-Ngwa North", "Isiala-Ngwa South", "Isuikwato", "Obi Nwa",
                    "Ohafia", "Osisioma", "Ngwa", "Ugwunagbo", "Ukwa East",
                    "Ukwa West", "Umuahia North", "Umuahia South", "Umu-Neochi"
                ]
            },
            "Anambra": {
                "code": "AN",
                "lgas": [
                    "Aguata", "Anambra East", "Anambra West", "Anaocha", "Awka North",
                    "Awka South", "Ayamelum", "Dunukofia", "Ekwusigo", "Idemili North",
                    "Idemili South", "Ihiala", "Njikoka", "Nnewi North", "Nnewi South",
                    "Ogbaru", "Onitsha North", "Onitsha South", "Orumba North",
                    "Orumba South", "Oyi"
                ]
            },
            "Ebonyi": {
                "code": "EB",
                "lgas": [
                    "Abakaliki", "Afikpo North", "Afikpo South", "Ebonyi", "Ezza North",
                    "Ezza South", "Ikwo", "Ishielu", "Ivo", "Izzi", "Ohaozara",
                    "Ohaukwu", "Onicha"
                ]
            },
            "Enugu": {
                "code": "EN",
                "lgas": [
                    "Aninri", "Awgu", "Enugu East", "Enugu North", "Enugu South",
                    "Ezeagu", "Igbo Etiti", "Igbo Eze North", "Igbo Eze South",
                    "Isi Uzo", "Nkanu East", "Nkanu West", "Nsukka", "Oji River",
                    "Udenu", "Udi", "Uzo Uwani"
                ]
            },
            "Imo": {
                "code": "IM",
                "lgas": [
                    "Aboh Mbaise", "Ahiazu Mbaise", "Ehime Mbano", "Ezinihitte",
                    "Ideato North", "Ideato South", "Ihitte/Uboma", "Ikeduru",
                    "Isiala Mbano", "Isu", "Mbaitoli", "Ngor Okpala", "Njaba",
                    "Nkwerre", "Nwangele", "Obowo", "Oguta", "Ohaji/Egbema",
                    "Okigwe", "Orlu", "Orsu", "Oru East", "Oru West",
                    "Owerri Municipal", "Owerri North", "Owerri West", "Unuimo"
                ]
            }
        }
        
        # Insert states and LGAs
        for state_name, state_info in southeast_data.items():
            cursor.execute(
                "INSERT INTO states (name, code) VALUES (?, ?)",
                (state_name, state_info["code"])
            )
            state_id = cursor.lastrowid
            
            for lga_name in state_info["lgas"]:
                # Generate approximate coordinates for each LGA
                lat, lon = self.generate_coordinates_for_lga(state_name, lga_name)
                cursor.execute(
                    "INSERT INTO local_governments (name, state_id, latitude, longitude) VALUES (?, ?, ?, ?)",
                    (lga_name, state_id, lat, lon)
                )
        
        self.conn.commit()
        self.generate_soil_data()
    
    def generate_coordinates_for_lga(self, state_name, lga_name):
        """Generate approximate coordinates for LGAs in southeastern Nigeria"""
        # Approximate coordinate ranges for southeastern Nigeria states
        state_coords = {
            "Abia": {"lat_range": (4.5, 6.0), "lon_range": (7.0, 8.0)},
            "Anambra": {"lat_range": (5.5, 6.8), "lon_range": (6.5, 7.5)},
            "Ebonyi": {"lat_range": (5.5, 6.8), "lon_range": (7.5, 8.5)},
            "Enugu": {"lat_range": (5.8, 7.0), "lon_range": (7.0, 8.0)},
            "Imo": {"lat_range": (5.0, 6.0), "lon_range": (6.5, 7.5)}
        }
        
        coords = state_coords.get(state_name, {"lat_range": (5.5, 6.5), "lon_range": (7.0, 8.0)})
        lat = round(random.uniform(*coords["lat_range"]), 4)
        lon = round(random.uniform(*coords["lon_range"]), 4)
        return lat, lon
    
    def generate_soil_data(self):
        """Generate realistic soil data for southeastern Nigeria"""
        cursor = self.conn.cursor()
        
        # Get all LGAs
        cursor.execute("SELECT id, name, state_id FROM local_governments")
        lgas = cursor.fetchall()
        
        # Common crops in southeastern Nigeria
        crops = [
            "Cassava", "Yam", "Cocoyam", "Maize", "Rice", "Plantain", 
            "Cocoa", "Oil Palm", "Sweet Potato", "Vegetables", "Pepper"
        ]
        
        for lga in lgas:
            # Generate soil properties based on typical southeastern Nigeria soils
            soil_data = self.generate_realistic_soil_properties(lga['name'])
            
            cursor.execute('''
                INSERT INTO soil_properties 
                (lga_id, ph_h2o, ph_kcl, organic_carbon, organic_matter, nitrogen, 
                 phosphorus, potassium, sand_content, clay_content, silt_content, 
                 bulk_density, cation_exchange_capacity, soil_depth_cm, drainage_class, 
                 erosion_risk, soil_type, fertility_rating, moisture_retention)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lga['id'], soil_data['ph_h2o'], soil_data['ph_kcl'], 
                soil_data['organic_carbon'], soil_data['organic_matter'], 
                soil_data['nitrogen'], soil_data['phosphorus'], soil_data['potassium'],
                soil_data['sand_content'], soil_data['clay_content'], soil_data['silt_content'],
                soil_data['bulk_density'], soil_data['cec'], soil_data['soil_depth'],
                soil_data['drainage'], soil_data['erosion_risk'], soil_data['soil_type'],
                soil_data['fertility'], soil_data['moisture_retention']
            ))
            
            # Generate crop suitability for each LGA
            for crop in crops:
                suitability = self.calculate_crop_suitability(crop, soil_data)
                cursor.execute('''
                    INSERT INTO crop_suitability 
                    (lga_id, crop_name, suitability_score, constraints, recommendations)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    lga['id'], crop, suitability['score'], 
                    suitability['constraints'], suitability['recommendations']
                ))
        
        self.conn.commit()
    
    def generate_realistic_soil_properties(self, lga_name):
        """Generate realistic soil properties for southeastern Nigeria"""
        # Southeastern Nigeria typically has:
        # - Acidic soils (pH 4.5-6.5)
        # - Sandy-loam to clay soils
        # - High organic matter in forest zones
        # - Variable fertility
        
        return {
            'ph_h2o': round(random.uniform(4.2, 6.8), 2),
            'ph_kcl': round(random.uniform(3.8, 6.2), 2),
            'organic_carbon': round(random.uniform(0.8, 3.5), 2),
            'organic_matter': round(random.uniform(1.4, 6.0), 2),
            'nitrogen': round(random.uniform(0.08, 0.35), 3),
            'phosphorus': round(random.uniform(5, 25), 1),
            'potassium': round(random.uniform(0.15, 0.8), 2),
            'sand_content': round(random.uniform(40, 80), 1),
            'clay_content': round(random.uniform(15, 45), 1),
            'silt_content': round(random.uniform(5, 25), 1),
            'bulk_density': round(random.uniform(1.2, 1.6), 2),
            'cec': round(random.uniform(8, 25), 1),
            'soil_depth': random.choice([30, 45, 60, 90, 120]),
            'drainage': random.choice(['Well drained', 'Moderately drained', 'Poorly drained']),
            'erosion_risk': random.choice(['Low', 'Moderate', 'High']),
            'soil_type': random.choice(['Sandy loam', 'Clay loam', 'Loamy sand', 'Clay', 'Silt loam']),
            'fertility': random.choice(['Low', 'Medium', 'High']),
            'moisture_retention': random.choice(['Low', 'Medium', 'High'])
        }
    
    def calculate_crop_suitability(self, crop, soil_data):
        """Calculate crop suitability based on soil properties"""
        # Simplified suitability scoring
        score = 50  # Base score
        constraints = []
        recommendations = []
        
        # pH suitability
        if crop in ['Rice', 'Cocoa'] and soil_data['ph_h2o'] < 5.5:
            score += 20
        elif soil_data['ph_h2o'] < 4.5:
            score -= 15
            constraints.append("Very acidic soil")
            recommendations.append("Apply lime to increase pH")
        
        # Organic matter
        if soil_data['organic_matter'] > 3.0:
            score += 10
        elif soil_data['organic_matter'] < 1.5:
            score -= 10
            constraints.append("Low organic matter")
            recommendations.append("Add organic fertilizer or compost")
        
        # Drainage
        if crop in ['Rice'] and soil_data['drainage'] == 'Poorly drained':
            score += 15
        elif crop in ['Cassava', 'Yam'] and soil_data['drainage'] == 'Well drained':
            score += 10
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'constraints': '; '.join(constraints) if constraints else 'None',
            'recommendations': '; '.join(recommendations) if recommendations else 'Standard fertilizer application'
        }
    
    def get_soil_data_by_lga(self, lga_name, state_name=None):
        """Get soil data for a specific LGA"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT s.name as state_name, lg.name as lga_name, lg.latitude, lg.longitude,
                   sp.ph_h2o, sp.ph_kcl, sp.organic_carbon, sp.organic_matter,
                   sp.nitrogen, sp.phosphorus, sp.potassium, sp.sand_content,
                   sp.clay_content, sp.silt_content, sp.bulk_density,
                   sp.cation_exchange_capacity, sp.soil_depth_cm, sp.drainage_class,
                   sp.erosion_risk, sp.soil_type, sp.fertility_rating, sp.moisture_retention
            FROM soil_properties sp
            JOIN local_governments lg ON sp.lga_id = lg.id
            JOIN states s ON lg.state_id = s.id
            WHERE lg.name = ?
        '''
        
        params = [lga_name]
        if state_name:
            query += ' AND s.name = ?'
            params.append(state_name)
        
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def get_crop_suitability(self, lga_name, crop_name=None):
        """Get crop suitability for an LGA"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT lg.name as lga_name, cs.crop_name, cs.suitability_score,
                   cs.constraints, cs.recommendations
            FROM crop_suitability cs
            JOIN local_governments lg ON cs.lga_id = lg.id
            WHERE lg.name = ?
        '''
        
        params = [lga_name]
        if crop_name:
            query += ' AND cs.crop_name = ?'
            params.append(crop_name)
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_all_lgas_by_state(self, state_name):
        """Get all LGAs for a specific state"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT lg.name, lg.latitude, lg.longitude
            FROM local_governments lg
            JOIN states s ON lg.state_id = s.id
            WHERE s.name = ?
            ORDER BY lg.name
        ''', (state_name,))
        return cursor.fetchall()
    
    def search_suitable_areas(self, crop_name, min_suitability=70):
        """Find areas suitable for a specific crop"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.name as state_name, lg.name as lga_name, cs.suitability_score,
                   cs.constraints, cs.recommendations
            FROM crop_suitability cs
            JOIN local_governments lg ON cs.lga_id = lg.id
            JOIN states s ON lg.state_id = s.id
            WHERE cs.crop_name = ? AND cs.suitability_score >= ?
            ORDER BY cs.suitability_score DESC
        ''', (crop_name, min_suitability))
        return cursor.fetchall()
    
    def export_to_json(self, filename="southeast_nigeria_soil_data.json"):
        """Export all data to JSON file"""
        cursor = self.conn.cursor()
        
        # Get all data
        cursor.execute('''
            SELECT s.name as state_name, s.code as state_code,
                   lg.name as lga_name, lg.latitude, lg.longitude,
                   sp.ph_h2o, sp.organic_carbon, sp.organic_matter,
                   sp.nitrogen, sp.phosphorus, sp.potassium,
                   sp.sand_content, sp.clay_content, sp.silt_content,
                   sp.bulk_density, sp.cation_exchange_capacity,
                   sp.soil_type, sp.fertility_rating, sp.drainage_class
            FROM soil_properties sp
            JOIN local_governments lg ON sp.lga_id = lg.id
            JOIN states s ON lg.state_id = s.id
            ORDER BY s.name, lg.name
        ''')
        
        data = []
        for row in cursor.fetchall():
            data.append(dict(row))
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data exported to {filename}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__=="__main__":
        print("=== SOIL DATA FOR ONITSHA NORTH ===")
        db = SoutheastNigeriaSoilDB()
        soil_data = db.get_soil_data_by_lga("Onitsha North")
        if soil_data:
            print(f"State: {soil_data['state_name']}")
            print(f"LGA: {soil_data['lga_name']}")
            print(f"Coordinates: {soil_data['latitude']}, {soil_data['longitude']}")
            print(f"pH: {soil_data['ph_h2o']}")
            print(f"Organic Matter: {soil_data['organic_matter']}%")
            print(f"Soil Type: {soil_data['soil_type']}")
            print(f"Fertility: {soil_data['fertility_rating']}")
            print(f"Drainage: {soil_data['drainage_class']}")
            
        print("\n=== CROP SUITABILITY FOR ONITSHA NORTH ===")
        crop_data = db.get_crop_suitability("Onitsha North")
        for crop in crop_data[:5]:  # Show first 5 crops
            print(f"{crop['crop_name']}: {crop['suitability_score']}/100")
            
        print("\n=== BEST AREAS FOR RICE CULTIVATION ===")
        rice_areas = db.search_suitable_areas("Rice", min_suitability=70)
        for area in rice_areas[:10]:  # Show top 10
            print(f"{area['state_name']} - {area['lga_name']}: {area['suitability_score']}/100")
            
        print("\n=== ALL LGAs IN ANAMBRA STATE ===")
        anambra_lgas = db.get_all_lgas_by_state("Anambra")
        for lga in anambra_lgas:
            print(f"{lga['name']} ({lga['latitude']}, {lga['longitude']})")
            
            # Export data
        db.export_to_json()
            
            # Close connection
        db.close()
            
        print("\nDatabase created successfully!")
        print("File: southeast_nigeria_soil.db")
        print("JSON export: southeast_nigeria_soil_data.json")