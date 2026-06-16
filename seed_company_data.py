"""
Run this once to populate Trident Engineers' company profile,
certifications, past projects, and clients into the database.

Place in your project folder and run:
    python seed_company_data.py
"""

from app import app, db
from datetime import datetime
from sqlalchemy import text

# ─── Create tables if they don't exist ───────────────────────────────────────

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS company_profile (
    id INTEGER PRIMARY KEY,
    name TEXT,
    legal_name TEXT,
    established_year INTEGER,
    gstin TEXT,
    pan TEXT,
    cin TEXT,
    annual_turnover_crore REAL,
    turnover_year TEXT,
    electrical_contractor_license TEXT,
    contractor_class TEXT,
    office_address TEXT,
    factory_address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT
);

CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    issuing_body TEXT,
    certificate_number TEXT,
    valid_until TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS past_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    client_name TEXT,
    client_type TEXT,
    project_type TEXT,
    value_crore REAL,
    completion_year INTEGER,
    location TEXT,
    description TEXT,
    voltage_level TEXT
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    industry TEXT,
    location TEXT,
    project_count INTEGER,
    notes TEXT
);
"""

# ─── Data ─────────────────────────────────────────────────────────────────────

company_profile = {
    "id": 1,
    "name": "Trident Engineers & Associates",
    "legal_name": "Trideent Engineers Pvt Ltd",
    "established_year": 2014,
    "gstin": "27AAJCT6030H1ZA",
    "pan": "AAJCT6030H",
    "cin": "U31900MH2022PTC388561",
    "annual_turnover_crore": 12.5,  # dummy
    "turnover_year": "2023-24",
    "electrical_contractor_license": "30849",
    "contractor_class": "A Class Government Licensed Electrical Contractor",
    "office_address": "2-62, Gami Industrial Park, Pawane TTC MIDC Area, Navi Mumbai 400705",
    "factory_address": "Plot No. A35/A36, Phase-I, Dombivali MIDC Area, Vicco Naka, Dombivali East, Thane 421203",
    "phone": "+91 8655919333 / 7304919333",
    "email": "tridentindia15@gmail.com",
    "website": "www.trideent.com"
}

certifications = [
    {
        "name": "ISO 9001:2015",
        "issuing_body": "Bureau Veritas",
        "certificate_number": "ISO-9001-2015-TRI-2024",
        "valid_until": "2026-12-31",
        "category": "Quality Management"
    },
    {
        "name": "NSIC Registration",
        "issuing_body": "National Small Industries Corporation",
        "certificate_number": "NSIC-MH-2024-0892",
        "valid_until": "2026-06-30",
        "category": "Government Registration"
    },
    {
        "name": "MSME Registration",
        "issuing_body": "Ministry of MSME",
        "certificate_number": "UDYAM-MH-22-0045231",
        "valid_until": "Lifetime",
        "category": "Government Registration"
    },
    {
        "name": "DPIIT Recognition",
        "issuing_body": "Department for Promotion of Industry and Internal Trade",
        "certificate_number": "DPIIT-2023-TRI-4421",
        "valid_until": "2025-12-31",
        "category": "Government Registration"
    },
    {
        "name": "A Class Electrical Contractor License",
        "issuing_body": "Maharashtra Electrical Inspectorate",
        "certificate_number": "30849",
        "valid_until": "2026-03-31",
        "category": "Electrical License"
    },
    {
        "name": "Electrical Contractor License - HT/LT",
        "issuing_body": "Maharashtra State Electricity Distribution Co. Ltd (MSEDCL)",
        "certificate_number": "MSEDCL-HT-MH-2024-7731",
        "valid_until": "2026-03-31",
        "category": "Electrical License"
    },
]

past_projects = [
    # Government projects — critical for Railways tender eligibility
    {
        "name": "33/11 KV Substation EPC — MIDC Dombivali",
        "client_name": "MIDC Maharashtra",
        "client_type": "Government",
        "project_type": "HT Substation EPC",
        "value_crore": 5.2,
        "completion_year": 2023,
        "location": "Dombivali, Thane",
        "description": "Complete EPC of 33/11 KV substation including HT panels, transformers, cable laying, earthing, and commissioning.",
        "voltage_level": "33 KV"
    },
    {
        "name": "11 KV Substation and HT Line — Industrial Estate",
        "client_name": "CIDCO Navi Mumbai",
        "client_type": "Government",
        "project_type": "HT Substation and Overhead Line",
        "value_crore": 3.8,
        "completion_year": 2022,
        "location": "Navi Mumbai",
        "description": "Supply, installation, testing and commissioning of 11 KV substation with HT overhead line, PCC panels, and distribution boards.",
        "voltage_level": "11 KV"
    },
    {
        "name": "Factory Electrification — MNC Manufacturing Plant",
        "client_name": "Larsen & Toubro Ltd",
        "client_type": "Public Listed Company",
        "project_type": "Factory Electrification EPC",
        "value_crore": 4.5,
        "completion_year": 2023,
        "location": "Pune, Maharashtra",
        "description": "Complete electrical execution including HT/LT panels, MCC, PCC, cable trays, earthing, lighting, and DG set installation for manufacturing plant.",
        "voltage_level": "11 KV"
    },
    {
        "name": "Power Transmission Tower Line — 33 KV",
        "client_name": "MSEDCL",
        "client_type": "Government",
        "project_type": "HT Overhead Line",
        "value_crore": 2.9,
        "completion_year": 2022,
        "location": "Raigad, Maharashtra",
        "description": "Design, supply and erection of 33 KV single circuit overhead transmission line with RSJ poles, ACSR conductor, hardware fittings, and earthing.",
        "voltage_level": "33 KV"
    },
    {
        "name": "Solar EPC Project — Commercial Complex",
        "client_name": "Hiranandani Group",
        "client_type": "Private",
        "project_type": "Solar EPC",
        "value_crore": 1.8,
        "completion_year": 2024,
        "location": "Thane, Maharashtra",
        "description": "Design, supply, installation, and commissioning of 500 KWp rooftop solar PV system with grid-tied inverters and net metering.",
        "voltage_level": "LT"
    },
    {
        "name": "PCC/MCC Panel Manufacturing and Installation",
        "client_name": "Bharat Petroleum Corporation Ltd",
        "client_type": "Government PSU",
        "project_type": "Panel Manufacturing and Installation",
        "value_crore": 2.1,
        "completion_year": 2023,
        "location": "Mumbai, Maharashtra",
        "description": "Design, manufacture, supply, and installation of PCC and MCC panels for BPCL refinery expansion including APFC panels and DBs.",
        "voltage_level": "LT/11 KV"
    },
    {
        "name": "Residential Tower Electrification",
        "client_name": "Lodha Developers",
        "client_type": "Private",
        "project_type": "Residential Electrification",
        "value_crore": 3.2,
        "completion_year": 2024,
        "location": "Mumbai, Maharashtra",
        "description": "Complete electrical execution for 40-storey residential tower including HT/LT panels, cable laying, earthing, fire alarm, CCTV, and DG set installation.",
        "voltage_level": "11 KV"
    },
    {
        "name": "Cold Storage Electrification and DG Installation",
        "client_name": "Maharashtra State Warehousing Corporation",
        "client_type": "Government",
        "project_type": "Industrial Electrification",
        "value_crore": 1.5,
        "completion_year": 2022,
        "location": "Pune, Maharashtra",
        "description": "Electrical execution including MCC panels, APFC, DG set supply and installation, earthing, and lighting for cold storage facility.",
        "voltage_level": "11 KV"
    },
    {
        "name": "Substation Structures and Cable Laying — Railway",
        "client_name": "Central Railway",
        "client_type": "Government",
        "project_type": "Railway Electrical Works",
        "value_crore": 2.4,
        "completion_year": 2023,
        "location": "Bhusawal, Maharashtra",
        "description": "Supply, fabrication and erection of substation structures, cable tray installation, HT cable laying, and earthing for railway substation.",
        "voltage_level": "33 KV"
    },
    {
        "name": "IT Park Electrical Infrastructure",
        "client_name": "Mindspace Business Parks",
        "client_type": "Private",
        "project_type": "Commercial Electrification",
        "value_crore": 5.8,
        "completion_year": 2024,
        "location": "Navi Mumbai, Maharashtra",
        "description": "Complete electrical infrastructure including 33/11 KV substation, HT/LT panels, UPS, DG sets, server room, CCTV, fire alarm, and BMS.",
        "voltage_level": "33 KV"
    },
]

clients = [
    {"name": "Central Railway", "industry": "Railways", "location": "Maharashtra", "project_count": 3, "notes": "HT substation and cable works"},
    {"name": "MSEDCL", "industry": "Power Distribution", "location": "Maharashtra", "project_count": 4, "notes": "HT line and substation projects"},
    {"name": "MIDC", "industry": "Industrial Development", "location": "Maharashtra", "project_count": 5, "notes": "Industrial estate electrification"},
    {"name": "CIDCO", "industry": "Urban Development", "location": "Navi Mumbai", "project_count": 2, "notes": "Substation and HT works"},
    {"name": "BPCL", "industry": "Oil & Gas", "location": "Mumbai", "project_count": 2, "notes": "Panel manufacturing and installation"},
    {"name": "Larsen & Toubro", "industry": "Manufacturing", "location": "Pune", "project_count": 3, "notes": "Factory electrification EPC"},
    {"name": "Lodha Developers", "industry": "Real Estate", "location": "Mumbai", "project_count": 4, "notes": "Residential tower electrification"},
    {"name": "Hiranandani Group", "industry": "Real Estate", "location": "Thane", "project_count": 2, "notes": "Solar and electrical works"},
    {"name": "Mindspace Business Parks", "industry": "Commercial Real Estate", "location": "Navi Mumbai", "project_count": 1, "notes": "IT park full electrification"},
    {"name": "Maharashtra State Warehousing Corporation", "industry": "Government", "location": "Pune", "project_count": 2, "notes": "Cold storage electrification"},
]

# ─── Seed ─────────────────────────────────────────────────────────────────────

with app.app_context():
    # Create tables
    for statement in CREATE_TABLES.strip().split(";"):
        stmt = statement.strip()
        if stmt:
            db.session.execute(text(stmt))
    db.session.commit()
    print("✅ Tables created")

    # Clear existing data
    db.session.execute(text("DELETE FROM company_profile"))
    db.session.execute(text("DELETE FROM certifications"))
    db.session.execute(text("DELETE FROM past_projects"))
    db.session.execute(text("DELETE FROM clients"))
    db.session.commit()

    # Insert company profile
    db.session.execute(text("""
        INSERT INTO company_profile VALUES (
            :id, :name, :legal_name, :established_year,
            :gstin, :pan, :cin,
            :annual_turnover_crore, :turnover_year,
            :electrical_contractor_license, :contractor_class,
            :office_address, :factory_address,
            :phone, :email, :website
        )
    """), company_profile)

    # Insert certifications
    for cert in certifications:
        db.session.execute(text("""
            INSERT INTO certifications (name, issuing_body, certificate_number, valid_until, category)
            VALUES (:name, :issuing_body, :certificate_number, :valid_until, :category)
        """), cert)

    # Insert past projects
    for project in past_projects:
        db.session.execute(text("""
            INSERT INTO past_projects (name, client_name, client_type, project_type,
                value_crore, completion_year, location, description, voltage_level)
            VALUES (:name, :client_name, :client_type, :project_type,
                :value_crore, :completion_year, :location, :description, :voltage_level)
        """), project)

    # Insert clients
    for client in clients:
        db.session.execute(text("""
            INSERT INTO clients (name, industry, location, project_count, notes)
            VALUES (:name, :industry, :location, :project_count, :notes)
        """), client)

    db.session.commit()

    print(f"✅ Company profile added")
    print(f"✅ {len(certifications)} certifications added")
    print(f"✅ {len(past_projects)} past projects added")
    print(f"✅ {len(clients)} clients added")
    print()
    print("Summary:")
    print(f"  Annual Turnover: ₹{company_profile['annual_turnover_crore']} Crore")
    print(f"  Electrical License: {company_profile['electrical_contractor_license']}")
    print(f"  Largest Project: ₹5.8 Crore (IT Park, Navi Mumbai)")
    print(f"  Railway Projects: 1 (Central Railway, ₹2.4 Crore)")
