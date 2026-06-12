"""
Run this once to populate your database with Trident's actual product catalog.
Place this file in your project folder (same level as app.py) and run:
    python seed_products.py
"""

from app import app, db, Product

products = [
    {
        "name": "RECD (Retrofit Emission Control Device)",
        "category": "Emission Control",
        "description": "A revolutionary clean air solution for diesel Genset customers. Designed using electrostatic precipitation (fetterless technology), RECD helps older Gensets (CPCB 1: 2004–2014 and CPCB 2: 2014–2023) comply with modern emission regulations without complete replacement. Reduces Particulate Matter (PM), Hydrocarbons (HC), and Carbon Monoxide (CO) by over 70%, fully aligned with National Green Tribunal guidelines.",
        "features": "No manual cleaning or filter replacement. No choking, water, chemical, or solvent usage. Low maintenance. Energy efficient — no active regeneration needed. No dependency on exhaust temperature. Remote installation possible. Onboard diagnostics and IoT telematics with cloud-based push notifications. Separated particulate matter can be reused as raw material in paint, dye, and plastics industry. All-weatherproof design.",
        "applications": "Diesel generator sets (DG Sets) in industries, commercial establishments, data centers, hospitals, railways, and government installations. Suitable for CPCB 1 and CPCB 2 compliant gensets. Ideal for organizations needing to comply with pollution control regulations.",
    },
    {
        "name": "Battery Energy Storage System (BESS)",
        "category": "Energy Storage",
        "description": "Cummins-backed Battery Energy Storage System for on-grid and off-grid applications. One of the few BESS solutions suitable for true off-grid use. Stores excess energy from renewable sources like solar and wind and releases it when needed, ensuring grid stability and uninterrupted power supply. Ideal for commercial, industrial, and utility-scale applications across Pune, Mumbai, Thane, Kolhapur, and surrounding regions.",
        "features": "True on-grid and off-grid capability. Plug-and-play integration with Cummins DER product range, pre-validated at factory. Global Cummins distribution and service network. Power Integration Centre (PIC) for testing and optimizing before commissioning. Over 100 years of Cummins power systems reliability. Supports solar integration and standalone storage units.",
        "applications": "Renewable energy storage for solar and wind plants. Power backup for commercial and industrial facilities. Grid stabilization for utilities. Off-grid power solutions for remote locations. Reducing electricity bills through peak shaving and load shifting. Railways, data centers, hospitals, and manufacturing plants.",
    },
    {
        "name": "Fuel Management System (FMS)",
        "category": "Fuel Monitoring",
        "description": "Advanced digital fuel tracking and monitoring system (Datum FMS) for diesel generators and fuel storage tanks. Provides real-time visibility into fuel consumption, theft detection, and inventory management. Helps organizations eliminate fuel pilferage and optimize generator operations.",
        "features": "Real-time fuel level monitoring. Fuel theft and anomaly detection alerts. Remote monitoring via cloud dashboard. Integration with DG sets and fuel tanks. Automated reports on consumption patterns. SMS and email alerts for critical events.",
        "applications": "Diesel generator fuel monitoring in industries, data centers, telecom towers, hospitals, and railways. Ideal for organizations with multiple generators or large fuel inventories needing centralized visibility and theft prevention.",
    },
    {
        "name": "Dual Fuel Kit for Diesel Generators",
        "category": "Fuel Efficiency",
        "description": "A retrofit kit that enables diesel generators to run on a combination of diesel and natural gas (CNG/PNG), significantly reducing diesel consumption and operating costs. Designed for existing Cummins and other brand gensets without requiring major engine modifications.",
        "features": "Reduces diesel consumption by up to 30–40%. Compatible with CNG and PNG gas supply. Minimal modifications to existing engine. Automatic switchover between diesel-only and dual-fuel mode. Safe and certified for industrial use. Easy installation by Cummins-trained technicians.",
        "applications": "Industries and commercial establishments with access to piped natural gas (PNG) or CNG supply. Data centers, hospitals, manufacturing plants, and real estate projects looking to reduce fuel costs and carbon emissions. Suitable for Railways and government facilities targeting fuel savings.",
    },
    {
        "name": "Power Management Solutions (PMS)",
        "category": "Power Management",
        "description": "Comprehensive power management solutions including Smart Energy Meters, Hybrid Power Management Systems, and Static VAR Generators. Designed to optimize energy efficiency, manage load distribution, and improve power quality for industrial and commercial customers.",
        "features": "Smart Energy Meter for real-time consumption tracking. Hybrid Power Management Solution for integrating multiple power sources. Static VAR Generator (SVG) for power factor correction and reactive power compensation. Load balancing and demand management. Integration with DG sets, solar, and grid supply.",
        "applications": "Manufacturing plants requiring power factor improvement. Industries needing load management and energy cost reduction. Data centers and hospitals requiring uninterrupted, high-quality power. Railways and utilities needing smart metering and reactive power correction.",
    },
    {
        "name": "New Cummins DG Sets",
        "category": "Diesel Generators",
        "description": "Brand new Cummins diesel generator sets supplied and installed by Trident Services, an authorized Cummins dealer since 2004. Available in a wide range of KVA ratings for standby and prime power applications. Backed by Cummins warranty and Trident's 24/7 after-sales service.",
        "features": "Full range of Cummins gensets from 15 KVA to 3000 KVA. CPCB 2 and CPCB 4 emission compliant models available. PCC (Power Command Controller) control panels. AMF (Auto Mains Failure) panel integration. Factory-tested before delivery. Cummins warranty with Trident after-sales support.",
        "applications": "Standby and prime power for industries, data centers, hospitals, hotels, real estate, manufacturing plants, telecom towers, and railways. Critical power backup for government and defense installations.",
    },
    {
        "name": "Genuine Cummins Spare Parts",
        "category": "Spare Parts",
        "description": "Original Cummins engine spare parts sourced directly from Cummins India Limited. Ensures engine performance, longevity, and warranty compliance. Covers the full range of Cummins engine families used in diesel generators and industrial applications.",
        "features": "100% genuine Cummins-sourced parts. Full range including filters, belts, injectors, fuel pumps, turbochargers, alternator parts, and control system components. Fast availability through Trident's parts inventory. Compatible with all Cummins engine families.",
        "applications": "Maintenance and repair of Cummins diesel generators and industrial engines. Preventive maintenance contracts (AMC). Emergency breakdown support. Engine overhauling and refurbishment projects.",
    },
    {
        "name": "Recon Engine & Components",
        "category": "Engine Refurbishment",
        "description": "Factory-reconditioned Cummins engines and components that deliver like-new performance at a fraction of the cost of a new engine. Each recon engine is rebuilt to Cummins OEM specifications and tested before delivery.",
        "features": "Rebuilt to OEM Cummins specifications. Full testing and quality checks before dispatch. Significant cost savings over new engine purchase. Backed by warranty. Available for major Cummins engine families used in gensets.",
        "applications": "Cost-effective engine replacement for aging DG sets. Engine swap for industries and organizations looking to extend generator life without full genset replacement. Suitable for Railways, manufacturing, and infrastructure projects.",
    },
    {
        "name": "Valvoline Cummins Lubricants",
        "category": "Lubricants & Oils",
        "description": "Genuine Valvoline Cummins branded engine oils and lubricants recommended for Cummins diesel engines. Ensures optimal engine performance, reduced wear, and compliance with engine warranty requirements.",
        "features": "Specifically formulated for Cummins diesel engines. Wide range including engine oils, coolants, and gear oils. Meets Cummins CES (Cummins Engineering Standards). Reduces engine wear and extends oil change intervals.",
        "applications": "Routine maintenance of Cummins diesel generators and engines. AMC and service contracts. Recommended for all Cummins genset users to maintain warranty and performance.",
    },
    {
        "name": "OptiNAS+ Hydraulic Oil Filter",
        "category": "Filtration",
        "description": "High-performance hydraulic oil filtration system designed for industrial and commercial fluid purification. Removes contaminants from hydraulic oil to extend equipment life and reduce maintenance costs.",
        "features": "High dirt-holding capacity. Multi-stage filtration for fine particle removal. Suitable for a wide range of hydraulic fluids. Robust construction for industrial environments. Easy installation and maintenance.",
        "applications": "Industrial hydraulic systems in manufacturing plants. Construction and heavy equipment. Railways and defense equipment maintenance. Any application requiring clean hydraulic fluid for equipment longevity.",
    },
    {
        "name": "Allison Transmission Service",
        "category": "Transmission Services",
        "description": "Authorized Allison Transmission repair, overhaul, and maintenance services. Trident Services is a certified Allison dealer providing genuine parts and trained technician support for Allison automatic transmissions.",
        "features": "Authorized Allison dealer with factory-trained technicians. Full transmission overhaul and rebuild capability. Genuine Allison parts supply. Diagnostic and performance testing. Preventive maintenance programs.",
        "applications": "Bus and commercial vehicle fleets including Railways and MSRTC. Defense and military vehicles. Construction and mining equipment. Any application using Allison automatic transmissions.",
    },
    {
        "name": "Coil Cooler",
        "category": "Cooling Systems",
        "description": "High-efficiency coil cooler for engine temperature control in Cummins DG sets and industrial engines. Ensures optimal operating temperatures to prevent overheating and extend engine life.",
        "features": "High heat transfer efficiency. Compact and robust design. Compatible with Cummins engine cooling systems. Low maintenance. Suitable for harsh industrial environments.",
        "applications": "Cummins diesel generator sets requiring supplemental or replacement cooling. Industrial engines in manufacturing and power plants. Suitable for high-load and continuous-duty applications.",
    },
    {
        "name": "Cummins Funnel Fuel Filters",
        "category": "Filtration",
        "description": "Portable funnel-type fuel filters with water separation capability for filtering diesel before it enters the generator fuel tank. Prevents water and particulate contamination that can damage fuel injectors and fuel pumps.",
        "features": "Removes water and particles from diesel fuel. Portable and easy to use. No electricity required. Transparent bowl for visual inspection. Compatible with standard diesel fuel filling equipment.",
        "applications": "Diesel fuel filling for generators at construction sites, remote locations, and temporary installations. Railways fuel depots and maintenance yards. Any application requiring clean diesel fuel supply.",
    },
    {
        "name": "Fuel Sure Kit",
        "category": "Fuel Maintenance",
        "description": "Complete fuel maintenance kit for diesel generators ensuring clean fuel supply and preventing common fuel-related engine problems. Includes accessories for fuel system maintenance and contamination prevention.",
        "features": "Complete accessories kit for fuel system maintenance. Prevents contamination and fuel degradation. Easy to use by field technicians. Compatible with Cummins and other genset brands.",
        "applications": "Preventive maintenance of diesel generator fuel systems. Ideal for AMC contracts and field service teams. Railways and industries with multiple generators requiring standardized maintenance kits.",
    },
    {
        "name": "Cummins Genset Battery",
        "category": "Batteries",
        "description": "Heavy-duty Cummins Pulse batteries specifically designed for diesel generator starting applications. Engineered for reliable cold cranking performance and long service life in standby power applications.",
        "features": "High cold cranking amperage (CCA) for reliable generator starting. Long service life in standby applications. Maintenance-free design. Tested and approved for Cummins gensets. Available in multiple capacities.",
        "applications": "Starting batteries for Cummins diesel generator sets of all sizes. Replacement batteries for existing gensets. Suitable for generators in data centers, hospitals, industries, and railways.",
    },
    {
        "name": "Cummins Vigilar",
        "category": "Remote Monitoring",
        "description": "Cummins Vigilar is a remote monitoring and telematics solution for Cummins generator sets. Provides real-time visibility into generator health, performance, and operational status from anywhere via a web or mobile interface.",
        "features": "Real-time remote monitoring of generator parameters. Fault alerts and notifications via SMS and email. Historical data logging and performance reports. Cloud-based dashboard accessible from any device. Integration with Cummins PowerCommand control systems.",
        "applications": "Remote monitoring of Cummins generator fleets for industries, data centers, telecom operators, and railways. Ideal for organizations with multiple generator sites needing centralized monitoring. Reduces need for physical inspections and enables predictive maintenance.",
    },
    {
        "name": "Retrofit Aftertreatment System (RAS)",
        "category": "Emission Control",
        "description": "Advanced retrofit aftertreatment system for diesel generator sets to reduce exhaust emissions and comply with CPCB and NGT pollution norms. Designed for integration with existing gensets without major engine modifications.",
        "features": "Reduces PM, HC, and CO emissions significantly. Compatible with CPCB 1 and CPCB 2 gensets. Minimal impact on DG operational efficiency. Robust and weatherproof design. IoT-enabled monitoring.",
        "applications": "Industries, hospitals, data centers, and railways with diesel generators needing to comply with CPCB 4 and NGT emission norms. Government and defense installations subject to environmental regulations.",
    },
]

with app.app_context():
    # Clear existing products (optional - comment out if you want to keep existing)
    # Product.query.delete()
    # db.session.commit()

    added = 0
    for p in products:
        # Check if product already exists to avoid duplicates
        existing = Product.query.filter_by(name=p["name"]).first()
        if not existing:
            product = Product(
                name=p["name"],
                category=p["category"],
                description=p["description"],
                features=p["features"],
                applications=p["applications"],
                image_path=None,
            )
            db.session.add(product)
            added += 1

    db.session.commit()
    print(f"✅ Done! Added {added} products to the database.")
    print(f"Total products in DB: {Product.query.count()}")
