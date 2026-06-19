from app import app, db
from app import (
    CompanyProfile,
    FinancialYear,
    WorkExperience,
    CompanyDocument,
)
from datetime import date

with app.app_context():
    db.drop_all()
    db.create_all()

    # ---------- Company Profile ----------
    profile = CompanyProfile(
        electrical_contractor_license="EC-12345",
        contractor_class="A",
        established_year=2008,
        entity_type="Partnership",   # Proprietary / Company / Partnership / JV / Society / Trust / HUF / LLP
        pan_number="ABCDE1234F"
    )
    db.session.add(profile)
    db.session.commit()  # commit now so profile.id exists for FKs below

    # ---------- Financial History (last 3 FY) ----------
    db.session.add_all([
        FinancialYear(company_id=profile.id, financial_year_end=2024, annual_turnover_crore=45.0, net_worth_crore=20.0, working_capital_crore=10.0),
        FinancialYear(company_id=profile.id, financial_year_end=2023, annual_turnover_crore=38.0, net_worth_crore=17.0, working_capital_crore=8.0),
        FinancialYear(company_id=profile.id, financial_year_end=2022, annual_turnover_crore=30.0, net_worth_crore=15.0, working_capital_crore=6.0),
    ])

    # ---------- Work Experience (for Technical Criteria) ----------
    db.session.add_all([
        WorkExperience(
            company_id=profile.id,
            project_name="Substation X Repair",
            work_value_crore=12.0,
            completion_date=date(2023, 5, 1),
            is_substantially_completed=True,
            work_type="Repair",
            equipment_combo="HT/LT Transformer & Switchgear",
            voltage_class_kv=11,
            certificate_issuer_type="govt"
        ),
        WorkExperience(
            company_id=profile.id,
            project_name="Station Facade Lighting Upgrade",
            work_value_crore=10.0,
            completion_date=date(2023, 1, 15),
            is_substantially_completed=True,
            work_type="Electrification",
            equipment_combo="Street Lighting",
            voltage_class_kv=0,
            certificate_issuer_type="govt"
        ),
        WorkExperience(
            company_id=profile.id,
            project_name="Panel Overhauling Project Y",
            work_value_crore=8.0,
            completion_date=date(2022, 9, 15),
            is_substantially_completed=True,
            work_type="Overhauling",
            equipment_combo="HT/LT Transformer & Panels",
            voltage_class_kv=11,
            certificate_issuer_type="public_listed_company",
            issuer_avg_turnover_3yr_crore=600.0,
            issuer_listed_nse=True,
            issuer_listed_bse=False,
            issuer_incorporation_date=date(2010, 1, 1),
            has_work_order_copy=True,
            has_boq=True,
            has_ca_certified_payment_details=True,
            has_tds_certificates=True,
            has_final_bill_copy=True
        ),
    ])

    # ---------- Company Documents (Compliance / Technical-Compliance credentials) ----------
    db.session.add_all([
        CompanyDocument(company_id=profile.id, document_type="ESIC_REGISTRATION", has_document=True, document_number="ESIC-998877", valid_until=date(2027, 3, 31)),
        CompanyDocument(company_id=profile.id, document_type="ELECTRICAL_CONTRACTOR_LICENSE", has_document=True, document_number="EC-12345", valid_until=date(2027, 12, 31)),
        CompanyDocument(company_id=profile.id, document_type="PARTNERSHIP_DEED", has_document=True),
        CompanyDocument(company_id=profile.id, document_type="PARTNERSHIP_JV_HUF_LLP_CERTIFICATE", has_document=True),
        CompanyDocument(company_id=profile.id, document_type="ANNEXURE_V_A", has_document=False),
        CompanyDocument(company_id=profile.id, document_type="SHRAMIKKALYAN_REGISTRATION", has_document=True),
        CompanyDocument(company_id=profile.id, document_type="SOLE_PROPRIETOR_UNDERTAKING", has_document=False),
        CompanyDocument(company_id=profile.id, document_type="POWER_OF_ATTORNEY", has_document=True),
    ])

    db.session.commit()
    print("Database reset and seeded successfully.")