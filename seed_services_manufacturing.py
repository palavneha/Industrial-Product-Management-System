"""
Seed script to populate Services and ManufacturingProduct tables
with data from trideent.com website.
"""
from app import app, db, Service, ManufacturingProduct

SERVICES_DATA = [
    {
        "name": "Electrical Execution Services",
        "short_description": "Professional electrical installation, wiring, and execution services for industrial and commercial projects with highest quality standards.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ELECTRICAL-EXECUTION-SERVICES.jpg",
        "category": "Electrical",
        "icon": "⚡",
        "link": "https://trideent.com/electrical-execution-services-2/",
    },
    {
        "name": "Electrical Design Services",
        "short_description": "Expert design and planning for electrical systems, power distribution, and infrastructure solutions tailored to your needs.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ELECTRICAL-DESIGN-SERVICES.jpg",
        "category": "Design",
        "icon": "📐",
        "link": "https://trideent.com/electrical-design-services-2/",
    },
    {
        "name": "Electrical Audits",
        "short_description": "Comprehensive audits of electrical systems to ensure compliance, safety, and optimal performance. Professional assessment and recommendations.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ELECTRICAL-AUDITS.jpg",
        "category": "Electrical",
        "icon": "🔍",
        "link": "https://trideent.com/electrical-audits-3/",
    },
    {
        "name": "DG Set Supply & Installation",
        "short_description": "Supply, installation, and commissioning of diesel generator sets with professional maintenance and support services.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/DG-SET-SUPPLY-AND-INSTALLATION-1.jpg",
        "category": "Electrical",
        "icon": "🔌",
        "link": "https://trideent.com/dg-set-supply-and-installation-3/",
    },
    {
        "name": "Instrumentation Projects",
        "short_description": "Advanced instrumentation solutions and project services for monitoring, control, and automation systems.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/06/instrumentation-projects-services.png",
        "category": "Design",
        "icon": "📊",
        "link": "https://trideent.com/instrumentation-projects-services-2/",
    },
    {
        "name": "Solar Services",
        "short_description": "Complete solar energy solutions including design, installation, and maintenance of solar power systems.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/SOLAR-SERVICES.jpg",
        "category": "Electrical",
        "icon": "☀️",
        "link": "https://trideent.com/solar-services-2/",
    },
    {
        "name": "Fire Alarm Systems",
        "short_description": "Advanced fire detection and alarm systems installation, testing, and maintenance for complete safety.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/06/fire-alarm-systems.jpg",
        "category": "Design",
        "icon": "🔥",
        "link": "https://trideent.com/fire-alarm-systems-2/",
    },
    {
        "name": "HT Overhead Line & Switch Yards",
        "short_description": "Design and installation of high-tension overhead lines and switching stations for power distribution.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/HT-OVERHEAD-LINE-SWITCH-YARDS.jpg",
        "category": "Electrical",
        "icon": "⚙️",
        "link": "https://trideent.com/ht-overhead-line-switch-yards-2/",
    },
    {
        "name": "Security System/CCTV",
        "short_description": "Complete security solutions with CCTV systems, monitoring, and advanced surveillance technology.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/SECURITY-SYSTEM-CCTV.jpg",
        "category": "Design",
        "icon": "📹",
        "link": "https://trideent.com/security-system-cctv-2/",
    },
    {
        "name": "Communication Systems, Server Data & Telecommunications",
        "short_description": "Integrated communication solutions including network design, installation, and technical support.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/COMMUNICATION-SYSTEMS.jpg",
        "category": "Design",
        "icon": "📡",
        "link": "#",
    },
    {
        "name": "Maintenance/AMC Division",
        "short_description": "Professional maintenance and annual maintenance contracts for all electrical and technical systems.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/MAINTENANCE-AMC-DIVISION.jpg",
        "category": "Maintenance",
        "icon": "🔧",
        "link": "https://trideent.com/maintenance-amc-division-2/",
    },
    {
        "name": "Load Sanction & Approval Services",
        "short_description": "Government department approvals and load sanction services for all regulatory requirements.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/LOAD-SANCTION-APPROVAL-SERVICES-ALL-GOT.-DEPT.jpg",
        "category": "Electrical",
        "icon": "📋",
        "link": "https://trideent.com/load-sanction-approval-services/",
    },
    {
        "name": "Electrical Signage & Banners",
        "short_description": "Professional electrical signage design and installation for retail, corporate, and commercial spaces.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ELECTRICAL-SINGAES-BANNERS-WORK.jpg",
        "category": "Design",
        "icon": "✨",
        "link": "https://trideent.com/electrical-signages-banners-work/",
    },
    {
        "name": "Shops & Stations Name Boards",
        "short_description": "Custom name boards and identification signage for shops, stations, and commercial establishments.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/SHOPS-STATIONS-NAME-BOARS-ALL-TYPE.jpg",
        "category": "Design",
        "icon": "🏷️",
        "link": "https://trideent.com/shops-stations-name-boards/",
    },
    {
        "name": "IoT Based Monitoring Systems",
        "short_description": "IoT-based monitoring systems connect electrical, mechanical, and industrial equipment to the internet, enabling real-time monitoring, control, data analysis, and predictive maintenance from anywhere.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/06/WhatsApp-Image-2026-06-13-at-13.57.54.jpeg",
        "category": "Electrical",
        "icon": "🏷️",
        "link": "https://trideent.com/iot-internet-of-things-based-monitoring-systems/",
    },
]

MANUFACTURING_DATA = [
    {
        "name": "Electrical Panels and DBs",
        "short_description": "Manufactured electrical panels and distribution boards designed for safe and reliable power distribution in commercial and industrial installations.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ELECTRICAL-PANELS-AND-DBS.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "Customized Design & Fabrication",
        "short_description": "Bespoke design and fabrication solutions for industrial and electrical applications, built precisely to client drawings and specifications.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/DESIGN-FABRICATION-as-per-CUSTOMISE.jpg",
        "category": "Fabrication",
        "link": "#",
    },
    {
        "name": "All Type GI, ALU. & SS Cable Tray",
        "short_description": "Galvanized iron, aluminium, and stainless steel cable trays for organized and protected cable routing across industrial and infrastructure projects.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ALL-TYPE-GI-ALU.-SS-CABLE-TRAY.jpg",
        "category": "Cable Management",
        "link": "#",
    },
    {
        "name": "MCC Panels As Requirement",
        "short_description": "Motor Control Centre panels engineered and fabricated to customer specifications for efficient motor management and control.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/MCC-PANELS-AS-REQUIRMENT.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "PCC Panels",
        "short_description": "Power Control Centre panels for centralized power distribution and control, built for heavy-duty industrial environments.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/PCC-PANLES.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "APFC Panels",
        "short_description": "Automatic Power Factor Correction panels that optimize energy efficiency and reduce electricity costs in industrial facilities.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/APFC-PANELS.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "PDB and LDB Control Panels",
        "short_description": "Power and lighting distribution boards with integrated control solutions for structured and safe electrical distribution.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/PDB-AND-LDBS-CONTROL-PANELS.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "Laser Cutting Services MS/SS/GI/Copper/ALU.",
        "short_description": "High-precision laser cutting services for mild steel, stainless steel, GI, copper, and aluminium, suitable for complex and custom profiles.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/LESAR-CUTTING-SRVICES-MS.jpg",
        "category": "Fabrication",
        "link": "#",
    },
    {
        "name": "All Type Name Boards & Station Name Boards",
        "short_description": "Durable and clearly legible name boards and station identification boards for industrial plants, infrastructure, and public spaces.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ALL-TYPE-NAME-BOARDS-STATION-NAME-BOARS.jpg",
        "category": "Signage",
        "link": "#",
    },
    {
        "name": "All Type Signage Boards Manufacturing",
        "short_description": "Custom signage boards for commercial, industrial, and public use — manufactured for durability and visual clarity.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/ALL-TYPE-SINAGES-BOARDS-MANUFACTR.jpg",
        "category": "Signage",
        "link": "#",
    },
    {
        "name": "Feeder Pillar All Type Manufacturing",
        "short_description": "Robust feeder pillars for outdoor and indoor electrical distribution, manufactured for varied load and environmental requirements.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/FEEDER-PILLAR-ALL-TYPE-MANUFACTR.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "Customize Boxes and DBs As Per Customer Requirement",
        "short_description": "Tailor-made enclosures and distribution boxes fabricated to exact customer dimensions and specifications.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/CUSTOMISE-BOXS-AND-DBS.-AS-PER-CUSOTMER-REQ.jpg",
        "category": "Panels",
        "link": "#",
    },
    {
        "name": "Banner & IP67 LED Strips",
        "short_description": "Weather-resistant IP67-rated LED strip lighting and banner illumination solutions for signage and outdoor applications.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/Banner-IP67LED-strips.jpg",
        "category": "Lighting",
        "link": "#",
    },
    {
        "name": "Cubical-CSS – All Type Fabrication",
        "short_description": "Full fabrication services for cubicles, CSS enclosures, and structural steel components across industrial and office environments.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/Cubical-CSS-All-type-Fabrication.jpg",
        "category": "Fabrication",
        "link": "#",
    },
    {
        "name": "Server Rack Manufacturing",
        "short_description": "Server racks, crone boxes, and communication enclosures manufactured to standard and custom dimensions for IT and telecom infrastructure.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/05/unnamed-2.jpg",
        "category": "IT Infrastructure",
        "link": "#",
    },
    {
        "name": "Crone Box Manufacturing",
        "short_description": "Server racks, crone boxes, and communication enclosures manufactured to standard and custom dimensions for IT and telecom infrastructure.",
        "image_url": "https://trideent.com/wp-content/uploads/2026/06/Server-Rack-–-Crone-Box-Manufacturing.png",
        "category": "IT Infrastructure",
        "link": "#",
    },
]


def seed():
    with app.app_context():
        db.create_all()

        # Clear existing data
        Service.query.delete()
        ManufacturingProduct.query.delete()
        db.session.commit()

        # Seed services
        for data in SERVICES_DATA:
            service = Service(
                name=data["name"],
                short_description=data["short_description"],
                image_url=data["image_url"],
                category=data["category"],
                icon=data["icon"],
                link=data["link"],
            )
            db.session.add(service)

        # Seed manufacturing products
        for data in MANUFACTURING_DATA:
            product = ManufacturingProduct(
                name=data["name"],
                short_description=data["short_description"],
                image_url=data["image_url"],
                category=data["category"],
                link=data["link"],
            )
            db.session.add(product)

        db.session.commit()
        print(f"✅ Seeded {len(SERVICES_DATA)} services")
        print(f"✅ Seeded {len(MANUFACTURING_DATA)} manufacturing products")


if __name__ == "__main__":
    seed()
