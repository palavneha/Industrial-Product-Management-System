from flask import request, render_template, redirect, url_for, flash, session
from dataclasses import asdict
from flask import Flask, json, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text
from flask import send_file
import fitz
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import json
import os
from groq import Groq
import re
import time
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()
from dataclasses import dataclass
from functools import wraps

@dataclass
class CriterionResult:

    category: str

    name: str

    required: str

    actual: str

    eligible: bool

@dataclass
class CriterionResult:
    category: str
    name: str
    required: str
    actual: str
    eligible: bool
    undetermined: bool = False  # True when criteria exist but couldn't be parsed

SIMILAR_WORK_OPTIONS = [
    {"min_count": 3, "min_percent_of_tender_value": 30},
    {"min_count": 2, "min_percent_of_tender_value": 40},
    {"min_count": 1, "min_percent_of_tender_value": 60},
]
LOOKBACK_PERIOD_YEARS = 7

CERTIFICATE_RULES = {
    "private_individual_allowed": False,
    "public_listed_requirements": {
        "min_avg_turnover_last_3yr_crore": 500,
        "must_be_listed_on": ["NSE", "BSE"],
        "min_years_since_incorporation": 5,
        "required_supporting_docs": [
            "work_order_copy", "boq", "ca_certified_payment_details",
            "tds_certificates", "final_bill_copy"
        ],
    },
}

TECHNICAL_MANDATORY_CONDITIONS = [
    "Work experience certificate from a private individual shall not be considered.",
    "Certificates issued by Public Listed companies are accepted only if the issuing "
    "company has average annual turnover of Rs. 500 crore or more in the last 3 financial "
    "years, is listed on NSE or BSE, and was incorporated at least 5 years prior to the "
    "tender closing date.",
    "If the certificate is from a Public Listed company, the tenderer must also submit the "
    "work order copy, bill of quantities, CA-certified payment details, TDS certificates, "
    "and copy of the final/last bill paid.",
]

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY")

# Store PASSWORD HASHES in the environment, never plaintext passwords.
# Generate a hash once with:
#   python -c "from werkzeug.security import generate_password_hash as g; print(g('your-password'))"
# and put the resulting string in SITE_PASSWORD_HASH / ADMIN_PASSWORD_HASH.
SITE_PASSWORD_HASH = os.environ.get("SITE_PASSWORD_HASH")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

# Endpoints reachable without being logged in to the site at all.
PUBLIC_ENDPOINTS = {"site_login", "static", "favicon"}


@app.before_request
def require_site_login():
    """Site-wide gate: every page needs the shared site password,
    except the login page itself and static assets."""
    if request.endpoint in PUBLIC_ENDPOINTS or request.endpoint is None:
        return
    if not session.get("site_authenticated"):
        return redirect(url_for("site_login", next=request.path))


def login_required(f):
    """Stricter gate on top of the site login: only employees who also
    know the admin password may modify the company database
    (company profile, financial years, work experience, documents)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class FinancialYear(db.Model):
    __tablename__ = "financial_year"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profile.id"), nullable=False)
    financial_year_end = db.Column(db.Integer, nullable=False)  # e.g. 2024 = FY 2023-24
    annual_turnover_crore = db.Column(db.Float, nullable=False)
    net_worth_crore = db.Column(db.Float)
    working_capital_crore = db.Column(db.Float)

    company = db.relationship("CompanyProfile", backref="financial_years")

class CompanyProfile(db.Model):

    __tablename__ = "company_profile"

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    electrical_contractor_license = db.Column(

        db.String(100)

    )

    contractor_class = db.Column(

        db.String(50)

    )

    established_year = db.Column(

        db.Integer

    )

    entity_type = db.Column(
        
        db.String(50)
        
    )   # Proprietary / Company / Partnership / JV / Society / Trust / HUF / LLP
    
    pan_number = db.Column(
        
        db.String(20)
        
    )

class WorkExperience(db.Model):
    __tablename__ = "work_experience"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profile.id"), nullable=False)
    project_name = db.Column(db.String(200))
    work_value_crore = db.Column(db.Float, nullable=False)
    completion_date = db.Column(db.Date, nullable=False)
    is_substantially_completed = db.Column(db.Boolean, default=False)
    work_type = db.Column(db.String(50))
    equipment_combo = db.Column(db.String(100))
    voltage_class_kv = db.Column(db.Float)
    certificate_issuer_type = db.Column(db.String(30))
    issuer_avg_turnover_3yr_crore = db.Column(db.Float)
    issuer_listed_nse = db.Column(db.Boolean, default=False)
    issuer_listed_bse = db.Column(db.Boolean, default=False)
    issuer_incorporation_date = db.Column(db.Date)
    has_work_order_copy = db.Column(db.Boolean, default=False)
    has_boq = db.Column(db.Boolean, default=False)
    has_ca_certified_payment_details = db.Column(db.Boolean, default=False)
    has_tds_certificates = db.Column(db.Boolean, default=False)
    has_final_bill_copy = db.Column(db.Boolean, default=False)

    company = db.relationship("CompanyProfile", backref="work_experiences")

class CompanyDocument(db.Model):
    __tablename__ = "company_document"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profile.id"), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    has_document = db.Column(db.Boolean, default=False)
    document_number = db.Column(db.String(100))
    issuing_authority = db.Column(db.String(150))
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    file_path = db.Column(db.String(255))

    company = db.relationship("CompanyProfile", backref="documents")

class TenderComplianceRequirement(db.Model):
    __tablename__ = "tender_compliance_requirement"
    id = db.Column(db.Integer, primary_key=True)
    tender_history_id = db.Column(db.Integer, db.ForeignKey("tender_history.id"), nullable=False)
    section = db.Column(db.String(100))          # Commercial-Compliance / Technical-Compliances / Undertakings / etc.
    description = db.Column(db.Text)
    documents_uploading = db.Column(db.String(30))   # "Mandatory" / "Optional" / "Not Allowed"
    requirement_type = db.Column(db.String(50))   # normalized tag, matched against CompanyDocument.document_type; null for boilerplate items

    tender = db.relationship("TenderHistory", backref="compliance_requirements")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    applications = db.Column(db.Text)
    image_path = db.Column(db.String(255))

class TenderHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    tender_name = db.Column(
        db.String(300)
    )

    tender_value_crore = db.Column(
        db.Float
    )

    summary = db.Column(
        db.Text
    )

    eligibility_verdict = db.Column(
        db.String(50)
    )

    verdict_reason = db.Column(
        db.Text
    )

    recommended_action = db.Column(
        db.Text
    )

    eligibility_criteria = db.Column(
        db.Text
    )

    matched_products = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    tender_number = db.Column(
        
        db.String(100)
        
    )
    
    tender_closing_date = db.Column(
        
        db.DateTime
        
    )
    
    local_content_percent = db.Column(
        
        db.Float
        
    )   # manually declared per bid, not derived from company data

    certificate_rules_json = db.Column(db.Text)  # per-tender extracted CERTIFICATE_RULES equivalent
    full_result_json = db.Column(db.Text)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.Text)
    detailed_content = db.Column(db.Text)  # AI-generated detailed content (JSON)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    icon = db.Column(db.String(10))
    link = db.Column(db.String(500))


class ManufacturingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.Text)
    detailed_content = db.Column(db.Text)  # AI-generated detailed content (JSON)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    link = db.Column(db.String(500))

ENTITY_CERT_RULES = {
    "PARTNERSHIP_JV_HUF_LLP_CERTIFICATE": {"Partnership", "JV", "HUF", "LLP"},
    "SOLE_PROPRIETOR_UNDERTAKING": {"Proprietary"},
    "ANNEXURE_V_A": {"Partnership", "JV", "Society", "Trust", "HUF", "LLP"},
}

@app.route("/")
def home():

    recent_products = Product.query.order_by(Product.id.desc()).limit(4).all()

    return render_template("home.html", products=recent_products)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.png")

from sqlalchemy import or_

@app.route("/test")
def test():
    return app.send_static_file("favicon.png")
@app.route("/products")
def products():

    search = request.args.get("search", "")

    print("==========")
    print("SEARCH =", search)

    if search:
        all_products = Product.query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        ).all()
    else:
        all_products = Product.query.all()

    print("RESULTS =", len(all_products))
    print("==========")
    print("SEARCH =", search)
    print("RESULTS =", len(all_products))
    return render_template("products.html", products=all_products, search=search)


@app.route("/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        image = request.files["image"]
        filename = None

        if image and image.filename != "":
            filename = secure_filename(image.filename)

            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        product = Product(
            name=request.form["name"],
            category=request.form["category"],
            description=request.form["description"],
            features=request.form["features"],
            applications=request.form["applications"],
            image_path=filename,
        )

        db.session.add(product)
        db.session.commit()

        return redirect("/products")

    return render_template("add_product.html")


@app.route("/product/<int:id>")
def product_details(id):

    product = Product.query.get_or_404(id)

    return render_template("product_details.html", product=product)


@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    product = Product.query.get_or_404(id)

    if request.method == "POST":

        product.name = request.form["name"]
        product.category = request.form["category"]
        product.description = request.form["description"]
        product.features = request.form["features"]
        product.applications = request.form["applications"]

        image = request.files.get("image")

        if image and image.filename != "":
            filename = secure_filename(image.filename)

            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            product.image_path = filename

        db.session.commit()

        return redirect("/products")

    return render_template("edit_product.html", product=product)

def _json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not JSON serializable: {obj}")

def extract_pdf_text(pdf):
    text = ""
    doc = fitz.open(stream=pdf.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()

    # PDF text layers often embed ligatures as single glyphs (ﬁ, ﬂ, etc.)
    # instead of separate letters — normalize so downstream regex matching works
    ligature_map = {
        "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
    }
    for lig, replacement in ligature_map.items():
        text = text.replace(lig, replacement)

    return text

def extract_sections(full_text):

    headings = [

        "1. NIT HEADER",

        "2. SCHEDULE",

        "Eligibility Conditions",

        "Special Financial Criteria",

        "Special Technical Criteria",

        "Commercial-Compliance",

        "General Instructions",

        "Special Conditions",

        "Technical-Compliances",

        "Undertakings",

        "Custom"

    ]

    lower = full_text.lower()

    positions = []

    for heading in headings:

        idx = lower.find(

            heading.lower()

        )

        if idx != -1:

            positions.append(

                (idx, heading)

            )

    positions.sort()

    sections = {}

    for i, (start, heading) in enumerate(positions):
        if i < len(positions)-1:
            end = positions[i+1][0]
        else:
            end = len(full_text)
        sections[heading] = \
            full_text[start:end]
    return sections

def build_dashboard_data(sections):

    nit_data = build_nit_dictionary(sections)

    advertised = nit_data.get(

        "Advertised Value",

        "-"

    )


    advertised = re.sub(
        r"[^\d.]",
        "",
        str(advertised)
    )

    if advertised:
        advertised = f"{float(advertised):,.2f}"
    else:
        advertised = "-"


    earnest = nit_data.get(

        "Earnest Money (Rs.)",

        "-"

    )


    if earnest != "-":

        earnest = f"{float(earnest):,.2f}"


    completion = nit_data.get(

        "Period of Completion",

        "-"

    )


    return {

        "advertised_value":

        advertised,


        "earnest_money":

        earnest,


        "completion_period":

        completion

    }

def build_nit_dictionary(sections):

    nit = sections.get(
        "1. NIT HEADER",
        ""
    )

    fields = [

        "Name of Work",

        "Tender Closing Date Time",

        "Bidding Start Date",

        "Bidding type",

        "Tender Type",

        "Bidding System",

        "Pre-Bid Conference Required",

        "Advertised Value",

        "Earnest Money (Rs.)",

        "Validity of Offer ( Days)",

        "Period of Completion",

        "Are JV allowed to bid",

        "Are Consortium allowed to bid",

        "Contract Type"

    ]

    nit_data = {}

    for field in fields:
        pattern = rf"{re.escape(field)}\s*:?\s*(.+)"
        match = re.search(pattern,nit,re.IGNORECASE)
        if match:
            nit_data[field] = \
                match.group(1).strip()
     # ---------- SPECIAL FIXES ----------

    consortium = re.search(

        r'Are Consortium allowed\s+to bid\s+(Yes|No)',

        nit,

        re.IGNORECASE

    )

    if consortium:
        nit_data["Are Consortium allowed to bid"] = \
            consortium.group(1)


    closing = re.search(

        r'Tender Closing Date\s*Time\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})',

        nit,

        re.IGNORECASE

    )

    if closing:
        nit_data["Tender Closing Date Time"] = \
            closing.group(1)


    completion = re.search(

        r'Period of Completion\s+(\d+\s+\w+)',

        nit,

        re.IGNORECASE

    )

    if completion: 
        nit_data["Period of Completion"] = \
            completion.group(1)
    return nit_data

def answer_question(

question,

dashboard,

nit_data

):

    Q_MAP = {

        "When does bidding start?":

        lambda:

        nit_data.get(

            "Bidding Start Date",

            "Not found"

        ),


        "When is the tender closing date?":

        lambda:

        nit_data.get(

            "Tender Closing Date Time",

            "Not found"

        ),


        "Is JV allowed?":

        lambda:

        nit_data.get(

            "Are JV allowed to bid",

            "Not found"

        ),


        "Is consortium allowed?":

        lambda:

        nit_data.get(

            "Are Consortium allowed to bid",

            "Not found"

        ),


        "What is the contract type?":

        lambda:

        nit_data.get(

            "Contract Type",

            "Not found"

        )

    }


    if question in Q_MAP:

        return Q_MAP[question]()


    return "Question unavailable."

def parse_completion_years(period_str):
    """Parse a free-text completion period like '18 Months' or '24 months'
    into a numeric number of years, for use in V/N turnover formulas."""
    if not period_str or period_str == "-":
        return None
    match = re.search(r"(\d+)\s*(month|year)", period_str, re.IGNORECASE)
    if not match:
        return None
    value, unit = match.groups()
    value = float(value)
    return value / 12 if unit.lower().startswith("month") else value

def parse_completion_years(period_str):
    """Parse a free-text completion period like '18 Months' into a numeric
    number of years, for use in V/N turnover formulas."""
    if not period_str or period_str == "-":
        return None
    match = re.search(r"(\d+)\s*(month|year)", period_str, re.IGNORECASE)
    if not match:
        return None
    value, unit = match.groups()
    value = float(value)
    return value / 12 if unit.lower().startswith("month") else value

def evaluate_financial_eligibility(requirements, profile, tender_value_crore=None, completion_period_years=None):
    results = []
    recent = (FinancialYear.query.filter_by(company_id=profile.id)
              .order_by(FinancialYear.financial_year_end.desc())
              .limit(3).all())
    avg_turnover_rupees = (
        sum(fy.annual_turnover_crore for fy in recent) / len(recent) * 1e7
        if recent else 0
    )
    for req in requirements:
        if req["type"] == "turnover":
            results.append(CriterionResult(
                category="Financial", name="Average Annual Turnover (last 3 FY)",
                required=f"Rs. {req['required']:,.0f}",
                actual=f"Rs. {avg_turnover_rupees:,.0f}",
                eligible=avg_turnover_rupees >= req["required"]
            ))
        elif req["type"] == "turnover_formula":
            if tender_value_crore and completion_period_years:
                v_rupees = tender_value_crore * 1e7
                n = completion_period_years
                required_rupees = min(v_rupees / n, v_rupees)
                results.append(CriterionResult(
                    category="Financial", name="Average Annual Turnover (V/N formula)",
                    required=f"Rs. {required_rupees:,.0f} (V/N or V, whichever is less; V=Rs.{v_rupees:,.0f}, N={n:.1f} yrs)",
                    actual=f"Rs. {avg_turnover_rupees:,.0f}",
                    eligible=avg_turnover_rupees >= required_rupees
                ))
            else:
                results.append(CriterionResult(
                    category="Financial", name="Average Annual Turnover",
                    required=req["formula"],
                    actual="Could not compute — missing tender value or completion period",
                    eligible=False, undetermined=True
                ))
    return results

def evaluate_technical_eligibility(sections, tender_value_crore, full_text=""):
    raw_chunk = extract_similar_work_raw_chunk(sections, full_text)
    parsed = parse_similar_work_items(raw_chunk)
    print("DEBUG parsed:", parsed)

    cert_rules = extract_certificate_rules(raw_chunk)

    allowed_items = parsed.get("allowed_items", [])
    min_voltage_kv = parsed.get("min_voltage_kv") or 0
    definition_text = parsed.get("clean_definition_text") or raw_chunk

    if not allowed_items:
        result = CriterionResult(
            category="Technical", name="Similar Work Experience",
            required="Definition not found in document",
            actual=parsed.get("not_found_reason") or "Could not determine — no work-type definition found",
            eligible=False, undetermined=True
        )
        return result, definition_text, [], [], cert_rules, cert_excluded   # <-- must include cert_rules here too

    cutoff = date.today() - timedelta(days=365 * LOOKBACK_PERIOD_YEARS)

    works = WorkExperience.query.filter(
        WorkExperience.completion_date >= cutoff,
        WorkExperience.is_substantially_completed == True
    ).all()
    print("DEBUG works found:", [(w.id, w.project_name, w.equipment_combo, w.voltage_class_kv, w.completion_date, w.is_substantially_completed) for w in works])
    print("DEBUG cert_rules:", cert_rules)
    match_results, match_ok = _equipment_combo_matches_batch(works, allowed_items)
    print("DEBUG match_ok:", match_ok, "match_results:", match_results)
    if not match_ok:
        result = CriterionResult(
            category="Technical",
            name="Similar Work Experience",
            required="See SIMILAR_WORK_OPTIONS thresholds",
            actual="Could not determine — work-type matching service unavailable",
            eligible=False,
            undetermined=True
        )
        return result, definition_text, [], [],cert_rules,[]   # <-- must include cert_rules here too

    qualifying = []
    near_misses = []
    cert_excluded = []

    for w in works:
        if not match_results.get(w.id, False):
            continue
        if min_voltage_kv and (w.voltage_class_kv or 0) < min_voltage_kv:
            continue

        cert_ok, cert_reason = _certificate_ok(w, cert_rules)
        percent = (w.work_value_crore / tender_value_crore) * 100 if tender_value_crore else 0

        if cert_ok is None:
            cert_excluded.append({
                "project_name": w.project_name,
                "percent": percent,
                "completion_date": w.completion_date,
                "work_value_crore": w.work_value_crore,
                "status": "undetermined",
                "reason": cert_reason,
            })
            continue
        if not cert_ok:
            cert_excluded.append({
                "project_name": w.project_name,
                "percent": percent,
                "completion_date": w.completion_date,
                "work_value_crore": w.work_value_crore,
                "status": "rejected",
                "reason": cert_reason,
            })
            continue

        entry = {
            "project_name": w.project_name,
            "percent": percent,
            "completion_date": w.completion_date,
            "work_value_crore": w.work_value_crore,
        }
        qualifying.append({"work": w, "percent": percent, "entry": entry})
        near_misses.append(entry)

    for opt in sorted(SIMILAR_WORK_OPTIONS, key=lambda o: o["min_count"]):
        matches = [q for q in qualifying if q["percent"] >= opt["min_percent_of_tender_value"]]
        if len(matches) >= opt["min_count"]:
            matched_entries = [m["entry"] for m in matches]
            result = CriterionResult(
                category="Technical", name="Similar Work Experience",
                required=f"{opt['min_count']} work(s) >= {opt['min_percent_of_tender_value']}% of tender value",
                actual=f"{len(matches)} qualifying work(s) found",
                eligible=True
            )
            return result, definition_text, matched_entries, [], cert_rules, cert_excluded

    near_misses.sort(key=lambda e: e["percent"], reverse=True)

    # Would any cert_excluded work, if its certificate were resolved, have been enough on its own?
    blocked_qualifiers = [
        e for e in cert_excluded
        if any(e["percent"] >= opt["min_percent_of_tender_value"] and opt["min_count"] == 1
               for opt in SIMILAR_WORK_OPTIONS)
    ]

    required_desc = "; ".join(
        f"{opt['min_count']} work(s) >= {opt['min_percent_of_tender_value']}% of tender value"
        for opt in sorted(SIMILAR_WORK_OPTIONS, key=lambda o: o["min_count"])
    )

    if blocked_qualifiers:
        actual_msg = (
            f"{len(blocked_qualifiers)} work(s) meet the work-type and value threshold "
            f"but are blocked by certificate/documentation issues — see below"
        )
        result = CriterionResult(
            category="Technical", name="Similar Work Experience",
            required=required_desc, actual=actual_msg,
            eligible=False, undetermined=True   # <-- treated as "needs review," not a flat rejection
        )
        return result, definition_text, [], near_misses, cert_rules, cert_excluded

    best = max(qualifying, key=lambda q: q["percent"], default=None)
    result = CriterionResult(
        category="Technical", name="Similar Work Experience",
        required=required_desc,
        actual=f"Best match {best['percent']:.0f}% of tender value" if best else "No qualifying work found",
        eligible=False
    )
    return result, definition_text, [], near_misses, cert_rules, cert_excluded

def _certificate_ok(w, cert_rules):
    if cert_rules is None:
        return None, "Could not determine this tender's certificate rules — verify manually"

    if w.certificate_issuer_type == "private_individual":
        if not cert_rules.get("private_individual_allowed", False):
            return False, "Certificate from private individual — not considered"
        return True, None

    if w.certificate_issuer_type == "public_listed_company":
        req = cert_rules.get("public_listed_requirements")
        if req is None:
            return None, "Tender's certificate rules don't address public-listed-company issuers — verify manually whether this certificate is acceptable"

        min_turnover = req.get("min_avg_turnover_last_3yr_crore")
        if min_turnover is not None and (w.issuer_avg_turnover_3yr_crore or 0) < min_turnover:
            return False, f"Issuer turnover below Rs. {min_turnover} crore threshold"

        listed_on = req.get("must_be_listed_on") or []
        if listed_on:
            on_any = (w.issuer_listed_nse and "NSE" in listed_on) or (w.issuer_listed_bse and "BSE" in listed_on)
            if not on_any:
                return False, f"Issuer not listed on {' or '.join(listed_on)}"

        min_years = req.get("min_years_since_incorporation")
        if min_years is not None:
            if not w.issuer_incorporation_date or (date.today() - w.issuer_incorporation_date).days / 365 < min_years:
                return False, f"Issuer incorporated less than {min_years} years before tender closing"

        for doc in req.get("required_supporting_docs", []):
            if not getattr(w, f"has_{doc}", False):
                return False, f"Missing supporting document: {doc.replace('_', ' ')}"

    return True, None

def evaluate_compliance_eligibility(requirements, profile):
    results = []
    docs = {d.document_type: d for d in CompanyDocument.query.filter_by(company_id=profile.id)}

    for req in requirements:
        if req.requirement_type is None or req.documents_uploading != "Mandatory":
            continue  # boilerplate undertaking or optional item — not a pass/fail gate

        applicable_entities = ENTITY_CERT_RULES.get(req.requirement_type)
        if applicable_entities and profile.entity_type not in applicable_entities:
            continue  # doesn't apply to this entity type

        doc = docs.get(req.requirement_type)
        has_valid_doc = bool(doc and doc.has_document and (
            doc.valid_until is None or doc.valid_until >= date.today()
        ))
        results.append(CriterionResult(
            category="Compliance", name=req.requirement_type,
            required="Document on file", actual="Present" if has_valid_doc else "Missing",
            eligible=has_valid_doc
        ))
    return results

def _extract_eligibility_chunk(full_text):
    """
    Locate the eligibility section using regex — handles varied heading styles
    across different tender formats. Returns a bounded slice (max 3000 chars)
    from the first eligibility heading to the first compliance/undertaking
    boundary, so the LLM never sees the whole document.
    """
    # Cast a wide net for the start: handles "ELIGIBILITY CONDITIONS",
    # "Eligibility Criteria", "Special Financial Criteria", etc.
    start_match = re.search(
        r"(?:eligibility\s+(?:conditions?|criteria)|special\s+financial\s+criteria)",
        full_text, re.IGNORECASE
    )
    if not start_match:
        return ""

    start = start_match.start()

    # End boundary: first occurrence of COMPLIANCE, UNDERTAKING, or
    # GENERAL INSTRUCTIONS after the start, or 3000 chars — whichever is sooner.
    end_match = re.search(
        r"(?:compliance|undertaking|general\s+instruction)",
        full_text[start + 50:],   # +50 to skip a heading that itself has "compliance"
        re.IGNORECASE
    )
    if end_match:
        end = start + 50 + end_match.start()
    else:
        end = start + 3000

    chunk = full_text[start:end]
    return re.sub(r"\s+", " ", chunk).strip()


def extract_eligibility(sections, full_text=""):
    """
    Extract financial turnover requirement.
    Strategy:
      1. Cheaply bound the eligibility section with regex (no LLM).
      2. Send ONLY that slice (~3000 chars max) to the LLM to parse the
         threshold — handles fixed amounts, V/N formulas, lakh/crore variants.
      3. Fall back to legacy regex if the LLM call fails.
    """
    # Build the bounded chunk from the full text if available,
    # otherwise fall back to the already-extracted section dict.
    chunk = _extract_eligibility_chunk(full_text) if full_text else ""
    if not chunk:
        # Fall back to the pre-split section (works for standard-format tenders)
        chunk = sections.get("Special Financial Criteria", "")
        chunk = re.sub(r"\s+", " ", chunk).strip()

    if not chunk:
        return []

    prompt = f"""You are extracting the minimum average annual contractual turnover requirement from a section of an Indian government tender document.

The requirement may be expressed as:
- A fixed rupee figure (e.g. "Rs. 50 crore", "Rs. 2,05,73,430")
- A formula (e.g. "V/N or V whichever is less, where V = advertised value and N = completion period in years")

Tender section text:
\"\"\"{chunk}\"\"\"

If the requirement is a fixed figure, return it as a number in RUPEES (not crore/lakh — convert to full rupees).
If the requirement is a formula like V/N, return null for required_rupees and explain the formula in formula_text.
If no financial turnover requirement is stated, return null for both.

Return ONLY valid JSON, no markdown:
{{"required_rupees": <number or null>, "formula_text": "<formula description or null>"}}"""

    response_text = call_groq(prompt)
    print("DEBUG extract_eligibility raw response:", response_text)
    # --- LLM path ---
    if response_text:
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
            required = parsed.get("required_rupees")
            formula = parsed.get("formula_text")

            if required is not None:
                return [{
                    "type": "turnover",
                    "name": "Average Annual Turnover",
                    "required": float(required),
                    "formula": None,
                }]
            elif formula:
                print(f"Formula-based turnover requirement: {formula}")
                return [{
                    "type": "turnover_formula",
                    "name": "Average Annual Turnover",
                    "required": None,
                    "formula": formula,
                }]
        except Exception as e:
            print(f"extract_eligibility LLM parse failed: {e} — falling back to regex")

    # --- Legacy regex fallback ---
    turnover_matches = re.findall(
        r"annual contractual turnover\s*=\s*Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|lakh)?",
        chunk, re.IGNORECASE
    )
    if turnover_matches:
        value_str, unit = turnover_matches[-1]
        required_turnover = float(value_str.replace(",", ""))
        if unit and unit.lower() == "crore":
            required_turnover *= 1e7
        elif unit and unit.lower() == "lakh":
            required_turnover *= 1e5
        return [{"type": "turnover", "name": "Average Annual Turnover",
                 "required": required_turnover, "formula": None}]

    return []

groq_client = None

def get_groq_client():
    global groq_client
    if groq_client is None:
        groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return groq_client

def call_groq(prompt, model_name="openai/gpt-oss-120b"):
    try:
        response = get_groq_client().chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq call failed: {e}")
        return None

def extract_similar_work_raw_chunk(sections, full_text=""):
    """
    Returns the full bounded Special Technical Criteria section (max 2500
    chars, clipped at COMPLIANCE) for the LLM to find the work-type definition.

    We send the whole section rather than starting from the first 'similar work'
    mention because in many tenders the threshold conditions (3 works at 30%
    etc.) appear BEFORE the actual work-type definition (e.g. item 1.1), so
    anchoring on the first mention gives the LLM the wrong chunk.
    """
    # Step 1: get the technical section text
    technical_raw = sections.get("Special Technical Criteria", "")
    if not technical_raw and full_text:
        tech_match = re.search(
            r"special\s+technical\s+criteria",
            full_text, re.IGNORECASE
        )
        if tech_match:
            start = tech_match.start()
            end_match = re.search(
                r"(?:compliance|undertaking|general\s+instruction)",
                full_text[start + 50:], re.IGNORECASE
            )
            end = start + 50 + end_match.start() if end_match else start + 3000
            technical_raw = full_text[start:end]

    if not technical_raw:
        return ""

    technical = re.sub(r"\s+", " ", technical_raw)

    # Step 2: clip at COMPLIANCE so we never overshoot into unrelated sections
    compliance_match = re.search(
        r"(?:5\.\s*compliance|compliance\s+condition|compliance)",
        technical, re.IGNORECASE
    )
    if compliance_match:
        technical = technical[:compliance_match.start()]

    # Step 3: check there is at least some mention of similar work,
    # otherwise this section has nothing relevant
    if not re.search(r"similar\s+work", technical, re.IGNORECASE):
        return ""

    # Return the whole section (up to 2500 chars) — the LLM will identify
    # the work-type sub-item (e.g. item 1.1) within it
    return technical[:2500].strip()

def extract_certificate_rules(raw_chunk):
    """
    Per-tender extraction of the public-listed-company certificate conditions —
    turnover threshold, exchange listing, incorporation age, and required
    supporting documents — since these vary by tender and must not be
    hardcoded as a single global rule.
    """
    if not raw_chunk:
        return None

    prompt = f"""Extract the certificate-acceptance rules for work experience certificates from this Indian government tender's Special Technical Criteria section.

Specifically find:
1. Whether certificates from a private individual are accepted (usually "shall not be considered" = not accepted).
2. If certificates from a Public Listed company are accepted, under what conditions:
   - Minimum average annual turnover (in crore) over how many financial years
   - Which stock exchange(s) it must be listed on
   - Minimum years since incorporation, relative to tender closing date
   - Any additional supporting documents required if submitting a Public Listed company certificate (e.g. work order copy, BOQ, CA-certified payment details, TDS certificates, final bill copy — or others not in this list)

Raw text:
\"\"\"{raw_chunk}\"\"\"

Return ONLY valid JSON, no markdown:
{{
  "private_individual_allowed": true_or_false,
  "public_listed_requirements": {{
    "min_avg_turnover_last_3yr_crore": <number or null>,
    "must_be_listed_on": ["NSE", "BSE"] or whichever apply or null,
    "min_years_since_incorporation": <number or null>,
    "required_supporting_docs": ["<doc names as worded, normalized to snake_case>"]
  }} or null if no public-listed-company allowance is mentioned at all,
  "extraction_notes": "<anything unusual or any condition you weren't confident about>"
}}

If the tender doesn't mention public listed company certificates at all, set public_listed_requirements to null.
If a number isn't stated, use null rather than guessing or defaulting to a typical value."""

    response_text = call_groq(prompt)
    if response_text is None:
        return None

    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        print(f"Could not parse certificate rules: {cleaned!r}")
        return None

def parse_similar_work_items(raw_chunk):
    if not raw_chunk:
        return {"allowed_items": [], "min_voltage_kv": None, "clean_definition_text": "", "not_found_reason": "No Special Technical Criteria text found in the document."}

    prompt = f"""You are extracting the WORK-TYPE DEFINITION from a Special Technical Criteria section of an Indian government tender.

The section may be structured in different ways:
- A paragraph starting with "Definition of Similar Work:" followed by work types
- A sub-item row (e.g. item 1.1, 1.2) that lists specific equipment or work categories
- A combination of both
- A reference to an external document instead of an inline definition (e.g. "As specified in para 2.3 of EQC of tender document", "Refer Annexure-III") — in this case there is NO usable definition in this text.

IGNORE the threshold/quantity conditions (e.g. "Three similar works each costing not less than 30%..." or "One similar work costing not less than 60%...") — those are quantity thresholds, NOT the work-type definition.
IGNORE certificate rules, issuer conditions, NSE/BSE listing requirements, and bidder instructions.

FIND the part that describes WHAT TYPE OF WORK qualifies — e.g. equipment names, work categories like "HT/LT Transformer & Switchgear", "erection of substations", "Repair/Overhauling of DG Sets" etc. This is often in a sub-item (1.1, 1.2, etc.) separate from the main eligibility paragraph.

Raw text:
\"\"\"{raw_chunk}\"\"\"

Return ONLY valid JSON, no markdown, no preamble, no explanation:
{{"allowed_items": ["item exactly as worded", "..."], "min_voltage_kv": null, "clean_definition_text": "the work-type definition clause, cleaned up, for display to a user", "not_found_reason": null}}

Split allowed_items into separate work-type categories using semicolons, "or", and numbered/lettered markers (i., ii., iii.) as separators.
Do NOT split on a slash or comma that is part of a single technical term — e.g. "HT/LT Transformer" is ONE term (High Tension/Low Tension transformer), and "33/11 kV" is ONE voltage designation. Keep these intact within their item.
Each returned item should be a complete, meaningful equipment/work-type phrase, not a sentence fragment.If a minimum voltage in kV is explicitly mentioned (e.g. "for 11 KV or higher capacity substations"), put that number in min_voltage_kv.
If multiple voltage classes are given separated by a slash (e.g. "33/11 kV Substations"), this means substations of EITHER voltage class qualify — return the LOWEST of the listed values as min_voltage_kv (since meeting the lower class is sufficient), not the highest.
If no voltage is mentioned, use null.
If you cannot find a usable work-type definition, return empty allowed_items AND set not_found_reason to a short, specific explanation of what you saw instead — e.g. "Section only references an external EQC/Annexure document (para 2.3) with no inline definition", "Section contains only threshold percentages, no work-type description", "Section text appears truncated/cut off before any definition". Be specific about what's actually in the text, don't guess at causes you can't see.
If a usable definition IS found, set not_found_reason to null."""

    response_text = call_groq(prompt)

    if response_text is None:
        return {"allowed_items": [], "min_voltage_kv": None, "clean_definition_text": "", "not_found_reason": "AI extraction call failed."}

    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except Exception:
        print(f"Could not parse Groq response as JSON: {cleaned!r}")
        return {"allowed_items": [], "min_voltage_kv": None, "clean_definition_text": "", "not_found_reason": "AI response could not be parsed."}

    if "allowed_items" not in parsed:
        return {"allowed_items": [], "min_voltage_kv": None, "clean_definition_text": "", "not_found_reason": "AI response was malformed."}

    cleaned_items = []
    for item in parsed["allowed_items"]:
        item = re.sub(r"\s*\betc\.?\s*$", "", item, flags=re.IGNORECASE).strip()
        if item:
            cleaned_items.append(item)
    parsed["allowed_items"] = cleaned_items
    parsed.setdefault("clean_definition_text", "")
    parsed.setdefault("not_found_reason", None)
    return parsed

def split_similar_work_items_regex(definition_text):
    """Pure regex split on '/' — no LLM call, for comparison."""
    if not definition_text:
        return []
    items = [item.strip() for item in definition_text.split("/")]
    items = [i for i in items if i and i.lower() not in ("etc", "etc.")]
    return items

def _normalize_for_match(text):
    """Lowercase, collapse whitespace, strip slashes' surrounding spaces, drop trailing 'etc'."""
    text = text.lower().strip()
    text = re.sub(r"\s*/\s*", "/", text)        # "HT / LT" -> "ht/lt"
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*\betc\.?\s*$", "", text)
    return text.strip()

def _equipment_combo_matches(work_combo, allowed_items):
    """Fuzzy match: normalized substring match in either direction."""
    if not work_combo:
        return False
    norm_combo = _normalize_for_match(work_combo)
    for item in allowed_items:
        norm_item = _normalize_for_match(item)
        if norm_item in norm_combo or norm_combo in norm_item:
            return True
    return False

def _equipment_combo_matches_batch(works, allowed_items):
    """
    Ask the LLM to judge, for each work's equipment_combo, whether it falls
    under any of the tender's allowed work-type categories — semantically,
    not just by literal substring.

    Returns (matches, ok):
      matches: dict {work.id: bool}
      ok: False if the Groq call/parse failed (caller should treat this as
          "could not determine," not as a confident non-match)
    """
    if not allowed_items or not works:
        return {w.id: False for w in works}, True

    work_list_str = "\n".join(
        f'{w.id}: "{w.equipment_combo}"' for w in works
    )
    allowed_str = "\n".join(f"- {item}" for item in allowed_items)

    prompt = fprompt = f"""You are checking whether each company's past work falls under any of the tender's allowed work-type categories.

Judge strictly on whether the company's work involves the SAME EQUIPMENT or WORK SCOPE as an allowed category — not merely the same general field (e.g. both being "electrical work").

Allowed real-world equivalences: a work item can match an allowed category if it is a component, sub-system, or synonym of that category's named equipment — e.g. "HT/LT Transformer & Switchgear" work reasonably falls under a category naming transformer/substation equipment, since switchgear is standard substation apparatus.

Do NOT match on:
- Shared industry or general field alone (e.g. street lighting is NOT DG set work, even though both are "electrical")
- Vague topical similarity without shared equipment/scope
- The word "electrical," "electrification," or "industrial" appearing in both

If you are not confident the work shares actual equipment or scope with an allowed category, return false. When in doubt, return false — a missed match is far less costly than a false one here.

Allowed work-type categories for this tender:
{allowed_str}

Company's past works (id: equipment description):
{work_list_str}

For each work id, decide true/false.

Return ONLY valid JSON, no markdown, no preamble:
{{"matches": {{"<work_id>": true_or_false, ...}}}}"""

    response_text = call_groq(prompt)
    if response_text is None:
        return {w.id: False for w in works}, False

    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        raw_matches = parsed.get("matches", {})
        matches = {int(k): bool(v) for k, v in raw_matches.items()}
        for w in works:
            matches.setdefault(w.id, False)
        return matches, True
    except Exception:
        print(f"Could not parse Groq batch-match response: {cleaned!r}")
        return {w.id: False for w in works}, False

@app.route("/tender", methods=["GET", "POST"])
def tender():
    if request.method == "GET":
        return render_template("tender_result.html", result=None, history=None, criteria=[])

    pdf = request.files.get("pdf_file")
    if not pdf or pdf.filename == "":
        flash("Please upload a tender PDF.")
        return redirect(url_for("tender"))

    filename = secure_filename(pdf.filename)

    full_text = extract_pdf_text(pdf)
    sections = extract_sections(full_text)
    nit_data = build_nit_dictionary(sections)

    advertised_value_str = nit_data.get("Advertised Value", "0")
    try:
        tender_value_crore = float(re.sub(r"[^\d.]", "", advertised_value_str)) / 1e7
    except ValueError:
        tender_value_crore = 0.0
    print("DEBUG tender_value_crore:", tender_value_crore, "advertised_value_str:", advertised_value_str)
    # financial check — pass full_text so extractor can find the section
    # even when extract_sections() did not split it out (non-standard formats)
    financial_requirements = extract_eligibility(sections, full_text)
    profile = CompanyProfile.query.first()
    completion_period_years = parse_completion_years(nit_data.get("Period of Completion", "-"))
    financial_results = evaluate_financial_eligibility(
        financial_requirements, profile, tender_value_crore, completion_period_years
    )

    dashboard = build_dashboard_data(sections)

    # pass full_text for the same reason
    technical_result, definition_text, matched_works, near_miss_works, cert_rules, cert_excluded = evaluate_technical_eligibility(sections, tender_value_crore, full_text)
    print("DEBUG cert_rules:", cert_rules)

    technical_display = {
        "lookback_period_years": LOOKBACK_PERIOD_YEARS,
        "similar_work_options": SIMILAR_WORK_OPTIONS,
        "similar_work_definition": definition_text or "Not specified",
        "mandatory_conditions": TECHNICAL_MANDATORY_CONDITIONS,
        "eligible": technical_result.eligible,
        "undetermined": technical_result.undetermined,
        "required": technical_result.required,
        "actual": technical_result.actual,
        "matched_works": matched_works,
        "near_miss_works": near_miss_works,
        "certificate_conditions_checked": not technical_result.undetermined,
        "certificate_conditions_checked": cert_rules is not None,
        "certificate_rules_undetermined": cert_rules is None,
        "certificate_excluded": cert_excluded,
    }
    # combine results
    results = financial_results + [technical_result]

    # compliance check not wired yet — extractor for TenderComplianceRequirement
    # still needs to be written; skipping for now so this doesn't silently no-op as "pass"

    # Undetermined criteria (e.g. similar work defined in external EQC doc)
    # are excluded from pass/fail — they show as a warning, not a hard fail.
    determined = [r for r in results if not r.undetermined]
    overall_eligible = all(r.eligible for r in determined)
    failed = [r for r in determined if not r.eligible]
    reason = "; ".join(f"{r.name}: required {r.required}, actual {r.actual}" for r in failed) or "All criteria met"

    result = {
        "nit_header": nit_data,
        "dashboard": dashboard,
        "eligibility": [asdict(r) for r in financial_results],
        "technical_eligibility": technical_display,
    }

    history = TenderHistory(
        filename=filename,
        tender_name=nit_data.get("Name of Work", "-"),
        tender_value_crore=tender_value_crore,
        eligibility_verdict="ELIGIBLE" if overall_eligible else "NOT ELIGIBLE",
        verdict_reason=reason,
        eligibility_criteria=json.dumps([asdict(r) for r in results]),
        certificate_rules_json=json.dumps(cert_rules) if cert_rules else None,
        full_result_json=json.dumps(result, default=_json_default),
        created_at=datetime.utcnow()
    )
    db.session.add(history)
    db.session.commit()

    

    return render_template("tender_result.html", result=result, history=history, criteria=results)

@app.route("/tender/history")
def tender_history_list():
    history = TenderHistory.query.order_by(TenderHistory.created_at.desc()).all()
    return render_template("tender_history_list.html", history=history)

@app.route("/tender/history/<int:id>")
def tender_history_detail(id):
    record = TenderHistory.query.get_or_404(id)
    result = json.loads(record.full_result_json) if record.full_result_json else None
    if result:
        for w in result.get("technical_eligibility", {}).get("matched_works", []):
            if w.get("completion_date"):
                w["completion_date"] = datetime.fromisoformat(w["completion_date"]).date()
        for w in result.get("technical_eligibility", {}).get("near_miss_works", []):
            if w.get("completion_date"):
                w["completion_date"] = datetime.fromisoformat(w["completion_date"]).date()
        for w in result.get("technical_eligibility", {}).get("certificate_excluded_works", []):
            if w.get("completion_date"):
                w["completion_date"] = datetime.fromisoformat(w["completion_date"]).date()
    return render_template("tender_result.html", result=result, history=record, criteria=None)

# ---------- AUTH ----------
@app.after_request
def add_no_cache_headers(response):
    """Prevent browsers from serving cached pages via back/forward
    after logout — forces a fresh request that re-checks the session."""
    if request.endpoint not in PUBLIC_ENDPOINTS:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response
@app.route("/login", methods=["GET", "POST"])
def site_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        next_url = request.form.get("next") or url_for("home")
        if SITE_PASSWORD_HASH and check_password_hash(SITE_PASSWORD_HASH, password):
            session["site_authenticated"] = True
            return redirect(next_url)
        flash("Incorrect password.")
        return redirect(url_for("site_login", next=next_url))
    next_url = request.args.get("next", "")
    return render_template("login.html", next=next_url)


@app.route("/logout")
def site_logout():
    session.clear()
    return redirect(url_for("site_login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect password.")
        return redirect(url_for("admin_login"))
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


# ---------- ADMIN DASHBOARD ----------

@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin/dashboard.html")


# ---------- COMPANY PROFILE ----------

@app.route("/admin/company-profile", methods=["GET", "POST"])
@login_required
def admin_company_profile():
    profile = CompanyProfile.query.first()
    if request.method == "POST":
        if profile is None:
            profile = CompanyProfile()
            db.session.add(profile)
        profile.electrical_contractor_license = request.form.get("electrical_contractor_license")
        profile.contractor_class = request.form.get("contractor_class")
        profile.established_year = request.form.get("established_year") or None
        profile.entity_type = request.form.get("entity_type")
        profile.pan_number = request.form.get("pan_number")
        db.session.commit()
        flash("Company profile saved.")
        return redirect(url_for("admin_company_profile"))
    return render_template("admin/company_profile.html", profile=profile)


# ---------- FINANCIAL YEARS ----------

@app.route("/admin/financial-years")
@login_required
def admin_financial_years():
    profile = CompanyProfile.query.first()
    years = FinancialYear.query.order_by(FinancialYear.financial_year_end.desc()).all() if profile else []
    return render_template("admin/financial_years.html", years=years, profile=profile)


@app.route("/admin/financial-years/add", methods=["GET", "POST"])
@login_required
def admin_financial_year_add():
    profile = CompanyProfile.query.first()
    if not profile:
        flash("Create a company profile first.")
        return redirect(url_for("admin_company_profile"))
    if request.method == "POST":
        fy = FinancialYear(
            company_id=profile.id,
            financial_year_end=int(request.form["financial_year_end"]),
            annual_turnover_crore=float(request.form["annual_turnover_crore"]),
            net_worth_crore=float(request.form["net_worth_crore"]) if request.form.get("net_worth_crore") else None,
            working_capital_crore=float(request.form["working_capital_crore"]) if request.form.get("working_capital_crore") else None,
        )
        db.session.add(fy)
        db.session.commit()
        flash("Financial year added.")
        return redirect(url_for("admin_financial_years"))
    return render_template("admin/financial_year_form.html", year=None)


@app.route("/admin/financial-years/<int:id>/edit", methods=["GET", "POST"])
@login_required
def admin_financial_year_edit(id):
    fy = FinancialYear.query.get_or_404(id)
    if request.method == "POST":
        fy.financial_year_end = int(request.form["financial_year_end"])
        fy.annual_turnover_crore = float(request.form["annual_turnover_crore"])
        fy.net_worth_crore = float(request.form["net_worth_crore"]) if request.form.get("net_worth_crore") else None
        fy.working_capital_crore = float(request.form["working_capital_crore"]) if request.form.get("working_capital_crore") else None
        db.session.commit()
        flash("Financial year updated.")
        return redirect(url_for("admin_financial_years"))
    return render_template("admin/financial_year_form.html", year=fy)


@app.route("/admin/financial-years/<int:id>/delete", methods=["POST"])
@login_required
def admin_financial_year_delete(id):
    fy = FinancialYear.query.get_or_404(id)
    db.session.delete(fy)
    db.session.commit()
    flash("Financial year deleted.")
    return redirect(url_for("admin_financial_years"))


# ---------- WORK EXPERIENCE ----------

@app.route("/admin/work-experience")
@login_required
def admin_work_experience():
    works = WorkExperience.query.order_by(WorkExperience.completion_date.desc()).all()
    return render_template("admin/work_experience_list.html", works=works)


def _populate_work_experience(w, form):
    w.project_name = form.get("project_name")
    w.work_value_crore = float(form["work_value_crore"])
    w.completion_date = datetime.strptime(form["completion_date"], "%Y-%m-%d").date()
    w.is_substantially_completed = form.get("is_substantially_completed") == "on"
    w.work_type = form.get("work_type")
    w.equipment_combo = form.get("equipment_combo")
    w.voltage_class_kv = float(form["voltage_class_kv"]) if form.get("voltage_class_kv") else None
    w.certificate_issuer_type = form.get("certificate_issuer_type")
    w.issuer_avg_turnover_3yr_crore = float(form["issuer_avg_turnover_3yr_crore"]) if form.get("issuer_avg_turnover_3yr_crore") else None
    w.issuer_listed_nse = form.get("issuer_listed_nse") == "on"
    w.issuer_listed_bse = form.get("issuer_listed_bse") == "on"
    w.issuer_incorporation_date = (
        datetime.strptime(form["issuer_incorporation_date"], "%Y-%m-%d").date()
        if form.get("issuer_incorporation_date") else None
    )
    w.has_work_order_copy = form.get("has_work_order_copy") == "on"
    w.has_boq = form.get("has_boq") == "on"
    w.has_ca_certified_payment_details = form.get("has_ca_certified_payment_details") == "on"
    w.has_tds_certificates = form.get("has_tds_certificates") == "on"
    w.has_final_bill_copy = form.get("has_final_bill_copy") == "on"


@app.route("/admin/work-experience/add", methods=["GET", "POST"])
@login_required
def admin_work_experience_add():
    profile = CompanyProfile.query.first()
    if not profile:
        flash("Create a company profile first.")
        return redirect(url_for("admin_company_profile"))
    if request.method == "POST":
        w = WorkExperience(company_id=profile.id)
        _populate_work_experience(w, request.form)
        db.session.add(w)
        db.session.commit()
        flash("Work experience added.")
        return redirect(url_for("admin_work_experience"))
    return render_template("admin/work_experience_form.html", work=None)


@app.route("/admin/work-experience/<int:id>/edit", methods=["GET", "POST"])
@login_required
def admin_work_experience_edit(id):
    w = WorkExperience.query.get_or_404(id)
    if request.method == "POST":
        _populate_work_experience(w, request.form)
        db.session.commit()
        flash("Work experience updated.")
        return redirect(url_for("admin_work_experience"))
    return render_template("admin/work_experience_form.html", work=w)


@app.route("/admin/work-experience/<int:id>/delete", methods=["POST"])
@login_required
def admin_work_experience_delete(id):
    w = WorkExperience.query.get_or_404(id)
    db.session.delete(w)
    db.session.commit()
    flash("Work experience deleted.")
    return redirect(url_for("admin_work_experience"))


# ---------- COMPANY DOCUMENTS ----------

@app.route("/admin/documents")
@login_required
def admin_documents():
    docs = CompanyDocument.query.order_by(CompanyDocument.document_type).all()
    return render_template("admin/documents_list.html", docs=docs)


def _populate_document(d, form):
    d.document_type = form.get("document_type")
    d.has_document = form.get("has_document") == "on"
    d.document_number = form.get("document_number")
    d.issuing_authority = form.get("issuing_authority")
    d.valid_from = datetime.strptime(form["valid_from"], "%Y-%m-%d").date() if form.get("valid_from") else None
    d.valid_until = datetime.strptime(form["valid_until"], "%Y-%m-%d").date() if form.get("valid_until") else None


@app.route("/admin/documents/add", methods=["GET", "POST"])
@login_required
def admin_document_add():
    profile = CompanyProfile.query.first()
    if not profile:
        flash("Create a company profile first.")
        return redirect(url_for("admin_company_profile"))
    if request.method == "POST":
        d = CompanyDocument(company_id=profile.id)
        _populate_document(d, request.form)
        db.session.add(d)
        db.session.commit()
        flash("Document added.")
        return redirect(url_for("admin_documents"))
    return render_template("admin/document_form.html", doc=None)


@app.route("/admin/documents/<int:id>/edit", methods=["GET", "POST"])
@login_required
def admin_document_edit(id):
    d = CompanyDocument.query.get_or_404(id)
    if request.method == "POST":
        _populate_document(d, request.form)
        db.session.commit()
        flash("Document updated.")
        return redirect(url_for("admin_documents"))
    return render_template("admin/document_form.html", doc=d)


@app.route("/admin/documents/<int:id>/delete", methods=["POST"])
@login_required
def admin_document_delete(id):
    d = CompanyDocument.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash("Document deleted.")
    return redirect(url_for("admin_documents"))

@app.route("/services")
def services():
    all_services = Service.query.all()
    # Parse detailed_content JSON for each service
    for s in all_services:
        if s.detailed_content:
            try:
                s._parsed_content = json.loads(s.detailed_content)
            except:
                s._parsed_content = None
        else:
            s._parsed_content = None
    return render_template("services.html", services=all_services)


@app.route("/manufacturing")
def manufacturing():
    all_products = ManufacturingProduct.query.all()
    for p in all_products:
        if p.detailed_content:
            try:
                p._parsed_content = json.loads(p.detailed_content)
            except:
                p._parsed_content = None
        else:
            p._parsed_content = None
    return render_template("manufacturing.html", products=all_products)


@app.route("/service/<int:id>")
def service_detail(id):
    service = Service.query.get_or_404(id)
    parsed_content = None
    if service.detailed_content:
        try:
            parsed_content = json.loads(service.detailed_content)
        except:
            parsed_content = None
    return render_template("service_detail.html", service=service, content=parsed_content)


@app.route("/manufacturing-product/<int:id>")
def manufacturing_detail(id):
    product = ManufacturingProduct.query.get_or_404(id)
    parsed_content = None
    if product.detailed_content:
        try:
            parsed_content = json.loads(product.detailed_content)
        except:
            parsed_content = None
    return render_template("manufacturing_detail.html", product=product, content=parsed_content)


@app.route("/generate-service-content/<int:id>", methods=["POST"])
def generate_service_content(id):
    service = Service.query.get_or_404(id)

    prompt = f"""
You are a professional content writer for Trident Engineers & Associates, an electrical and instrumentation EPC company.

Generate detailed, professional content for this service:
Service Name: {service.name}
Short Description: {service.short_description}
Category: {service.category}

Create comprehensive content in this exact JSON format:
{{
    "tagline": "A compelling one-line tagline for this service",
    "overview": "A detailed 3-4 paragraph overview of this service, explaining what it involves, why it's important, and how Trident delivers it professionally. Be specific to electrical/industrial engineering.",
    "key_features": [
        "Feature 1 with brief explanation",
        "Feature 2 with brief explanation",
        "Feature 3 with brief explanation",
        "Feature 4 with brief explanation",
        "Feature 5 with brief explanation",
        "Feature 6 with brief explanation"
    ],
    "applications": [
        "Application/Industry 1",
        "Application/Industry 2",
        "Application/Industry 3",
        "Application/Industry 4",
        "Application/Industry 5"
    ],
    "process_steps": [
        {{"step": "Step 1 title", "description": "Brief description"}},
        {{"step": "Step 2 title", "description": "Brief description"}},
        {{"step": "Step 3 title", "description": "Brief description"}},
        {{"step": "Step 4 title", "description": "Brief description"}}
    ],
    "why_choose_us": [
        "Reason 1",
        "Reason 2",
        "Reason 3",
        "Reason 4"
    ],
    "technical_specs": "A paragraph about technical standards, certifications, and compliance relevant to this service"
}}

Make the content professional, technically accurate, and specific to the Indian industrial/electrical sector. Reference Indian standards (IS, BIS, CEA) where appropriate.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    text_resp = (
        response.choices[0]
        .message.content.strip()
        .replace("```json", "")
        .replace("```", "")
    )

    try:
        content = json.loads(text_resp)
        service.detailed_content = json.dumps(content)
        db.session.commit()
    except:
        pass

    return redirect(f"/service/{id}")


@app.route("/generate-manufacturing-content/<int:id>", methods=["POST"])
def generate_manufacturing_content(id):
    product = ManufacturingProduct.query.get_or_404(id)

    prompt = f"""
You are a professional content writer for Trident Engineers & Associates, an electrical panel and industrial manufacturing company.

Generate detailed, professional content for this manufactured product:
Product Name: {product.name}
Short Description: {product.short_description}
Category: {product.category}

Create comprehensive content in this exact JSON format:
{{
    "tagline": "A compelling one-line tagline for this product",
    "overview": "A detailed 3-4 paragraph overview of this product, explaining what it is, its construction, materials used, and how Trident manufactures it. Be specific to electrical/industrial manufacturing.",
    "key_features": [
        "Feature 1 with brief explanation",
        "Feature 2 with brief explanation",
        "Feature 3 with brief explanation",
        "Feature 4 with brief explanation",
        "Feature 5 with brief explanation",
        "Feature 6 with brief explanation"
    ],
    "specifications": [
        {{"spec": "Specification name", "value": "Specification value/range"}},
        {{"spec": "Specification name", "value": "Specification value/range"}},
        {{"spec": "Specification name", "value": "Specification value/range"}},
        {{"spec": "Specification name", "value": "Specification value/range"}},
        {{"spec": "Specification name", "value": "Specification value/range"}}
    ],
    "applications": [
        "Application/Industry 1",
        "Application/Industry 2",
        "Application/Industry 3",
        "Application/Industry 4",
        "Application/Industry 5"
    ],
    "manufacturing_process": [
        {{"step": "Step 1 title", "description": "Brief description"}},
        {{"step": "Step 2 title", "description": "Brief description"}},
        {{"step": "Step 3 title", "description": "Brief description"}},
        {{"step": "Step 4 title", "description": "Brief description"}}
    ],
    "quality_standards": "A paragraph about quality standards, testing procedures, certifications, and compliance relevant to this product. Reference Indian standards (IS, BIS, IEC) where appropriate.",
    "why_choose_us": [
        "Reason 1",
        "Reason 2",
        "Reason 3",
        "Reason 4"
    ]
}}

Make the content professional, technically accurate, and specific to the Indian industrial/electrical manufacturing sector.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    text_resp = (
        response.choices[0]
        .message.content.strip()
        .replace("```json", "")
        .replace("```", "")
    )

    try:
        content = json.loads(text_resp)
        product.detailed_content = json.dumps(content)
        db.session.commit()
    except:
        pass

    return redirect(f"/manufacturing-product/{id}")


@app.route("/generate-all-content", methods=["POST"])
def generate_all_content():
    """Generate content for all services and manufacturing products that don't have content yet."""
    item_type = request.form.get("type", "all")

    generated = 0

    if item_type in ["all", "services"]:
        services = Service.query.filter(
            (Service.detailed_content == None) | (Service.detailed_content == "")
        ).all()
        for service in services:
            try:
                prompt = f"""You are a professional content writer for Trident Engineers & Associates, an electrical and instrumentation EPC company.
Generate detailed content for: {service.name}
Description: {service.short_description}
Category: {service.category}

Respond ONLY in this exact JSON format:
{{"tagline": "compelling tagline", "overview": "3-4 detailed paragraphs about this service", "key_features": ["feature1", "feature2", "feature3", "feature4", "feature5", "feature6"], "applications": ["app1", "app2", "app3", "app4", "app5"], "process_steps": [{{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}], "why_choose_us": ["reason1", "reason2", "reason3", "reason4"], "technical_specs": "paragraph about standards and compliance"}}"""

                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": prompt}],
                )
                text_resp = (
                    response.choices[0]
                    .message.content.strip()
                    .replace("```json", "")
                    .replace("```", "")
                )
                content = json.loads(text_resp)
                service.detailed_content = json.dumps(content)
                db.session.commit()
                generated += 1
            except Exception as e:
                print(f"Error generating content for service {service.name}: {e}")

    if item_type in ["all", "manufacturing"]:
        products = ManufacturingProduct.query.filter(
            (ManufacturingProduct.detailed_content == None)
            | (ManufacturingProduct.detailed_content == "")
        ).all()
        for product in products:
            try:
                prompt = f"""You are a professional content writer for Trident Engineers & Associates, an electrical panel and industrial manufacturing company.
Generate detailed content for: {product.name}
Description: {product.short_description}
Category: {product.category}

Respond ONLY in this exact JSON format:
{{"tagline": "compelling tagline", "overview": "3-4 detailed paragraphs", "key_features": ["feature1", "feature2", "feature3", "feature4", "feature5", "feature6"], "specifications": [{{"spec": "name", "value": "value"}}, {{"spec": "name", "value": "value"}}, {{"spec": "name", "value": "value"}}, {{"spec": "name", "value": "value"}}, {{"spec": "name", "value": "value"}}], "applications": ["app1", "app2", "app3", "app4", "app5"], "manufacturing_process": [{{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}, {{"step": "title", "description": "desc"}}], "quality_standards": "paragraph about standards", "why_choose_us": ["reason1", "reason2", "reason3", "reason4"]}}"""

                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                )
                text_resp = (
                    response.choices[0]
                    .message.content.strip()
                    .replace("```json", "")
                    .replace("```", "")
                )
                content = json.loads(text_resp)
                product.detailed_content = json.dumps(content)
                db.session.commit()
                generated += 1
            except Exception as e:
                print(
                    f"Error generating content for product {product.name}: {e}"
                )

    return redirect(request.referrer or "/services")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        from seed_company_data import seed_database
        if CompanyProfile.query.first() is None:
            seed_database(db, CompanyProfile, FinancialYear, WorkExperience)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)