from flask import Flask, json, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text
from werkzeug.utils import secure_filename
from pptx import Presentation
from flask import send_file
import fitz
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import io
from datetime import datetime
import json
import os
from groq import Groq

load_dotenv()

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


app = Flask(__name__)
app.secret_key = "trident_secret_key_2024"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    applications = db.Column(db.Text)
    image_path = db.Column(db.String(255))


class TenderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    summary = db.Column(db.Text)
    matched_products = db.Column(db.Text)  # stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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


@app.route("/")
def home():

    recent_products = Product.query.order_by(Product.id.desc()).limit(4).all()

    return render_template("home.html", products=recent_products)


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


@app.route("/generate-ppt/<int:id>")
def generate_ppt(id):

    product = Product.query.get_or_404(id)

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = product.name

    if len(slide.placeholders) > 1:
        slide.placeholders[1].text = product.category

    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Description"
    slide2.placeholders[1].text = product.description

    slide3 = prs.slides.add_slide(prs.slide_layouts[1])
    slide3.shapes.title.text = "Features"
    slide3.placeholders[1].text = product.features

    slide4 = prs.slides.add_slide(prs.slide_layouts[1])
    slide4.shapes.title.text = "Applications"
    slide4.placeholders[1].text = product.applications

    filename = f"{product.name}.pptx"

    prs.save(filename)

    return send_file(filename, as_attachment=True)


@app.route("/tender", methods=["GET", "POST"])
def tender():
    if request.method == "POST":
        pdf = request.files["tender_pdf"]
        filename = secure_filename(pdf.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf.save(path)

        # Extract text via OCR
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            text = page.get_text()
            if text.strip():
                full_text += text
            else:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                full_text += pytesseract.image_to_string(img)

        # Get all products from DB
        all_products = Product.query.all()
        product_list = "\n".join(
            [
                f"- {p.name} ({p.category}): {p.description} | Features: {p.features} | Applications: {p.applications}"
                for p in all_products
            ]
        )

        # Get company data
        from sqlalchemy import text as sqla_text

        profile = db.session.execute(
            sqla_text("SELECT * FROM company_profile WHERE id=1")
        ).fetchone()
        certs = db.session.execute(sqla_text("SELECT * FROM certifications")).fetchall()
        projects = db.session.execute(
            sqla_text("SELECT * FROM past_projects ORDER BY value_crore DESC")
        ).fetchall()

        cert_list = "\n".join(
            [f"- {c.name} (valid until {c.valid_until})" for c in certs]
        )
        project_list = "\n".join(
            [
                f"- {p.name} | {p.client_name} ({p.client_type}) | ₹{p.value_crore}Cr | {p.completion_year} | {p.voltage_level}"
                for p in projects
            ]
        )

        prompt = f"""
        You are a tender eligibility assessment assistant for Trident Engineers & Associates.

        COMPANY PROFILE:
        - Annual Turnover: ₹{profile.annual_turnover_crore} Crore ({profile.turnover_year})
        - Electrical Contractor License: {profile.electrical_contractor_license} ({profile.contractor_class})
        - Established: {profile.established_year}

        CERTIFICATIONS:
        {cert_list}

        PAST PROJECTS (sorted by value):
        {project_list}

        OUR SERVICES AND PRODUCTS:
        {product_list}

        TENDER DOCUMENT:
        {full_text[:5000]}

        YOUR TASKS:
        1. Extract SPECIFIC eligibility criteria from the tender document including:
        - Exact minimum turnover required (calculate from tender value and years)
        - Exact past project experience required (30%/40%/60% of tender value)
        - Required licenses and certifications
        - Any other specific requirements
        2. Check EACH criterion with EXACT numbers against company data
        3. Match our services to tender line items
        4. Summarize the tender

        Respond ONLY in this exact JSON format:
        {{
        "tender_name": "short name",
        "tender_value_crore": 8.05,
        "tender_summary": "3-4 sentence summary",
        "eligibility": {{
            "verdict": "ELIGIBLE or PARTIALLY ELIGIBLE or NOT ELIGIBLE",
            "verdict_reason": "one line with specific numbers e.g. Turnover ₹12.5Cr > ₹8.05Cr required",
            "criteria": [
            {{
                "requirement": "specific requirement with exact number e.g. Min turnover ₹8.05 Crore/year",
                "company_status": "exact company value e.g. ₹12.5 Crore turnover",
                "result": "PASS or FAIL or PARTIAL",
                "notes": "brief specific note"
            }}
            ],
            "recommended_action": "specific next steps"
        }},
        "matched_products": [
            {{
            "name": "product/service name from our catalog",
            "reason": "why it fits this specific tender",
            "match_score": "High or Medium or Low",
            "evidence": "exact quote from tender document"
            }}
        ]
        }}
        """

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
        result = json.loads(text_resp)

        history = TenderHistory(
            filename=filename,
            summary=result.get("tender_summary", ""),
            matched_products=json.dumps(result.get("matched_products", [])),
        )
        db.session.add(history)
        db.session.commit()

        return render_template(
            "tender_result.html", result=result, tender_text=full_text[:500]
        )

    return render_template("tender.html")
    if request.method == "POST":
        pdf = request.files["tender_pdf"]
        filename = secure_filename(pdf.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf.save(path)

        # Extract text via OCR
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            text = page.get_text()
            if text.strip():
                full_text += text
            else:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                full_text += pytesseract.image_to_string(img)

        # Get all products from DB
        all_products = Product.query.all()
        product_list = "\n".join(
            [
                f"- {p.name} ({p.category}): {p.description} | Features: {p.features} | Applications: {p.applications}"
                for p in all_products
            ]
        )

        # Ask Gemini to match products to tender
        prompt = f"""
You are a technical sales assistant for Trident Services Pvt Ltd, an authorized Cummins dealer.

Here is a tender document:
{full_text[:5000]}

Here are our available products:
{product_list}

Your task:
1. Summarize what this tender is asking for in 3-4 sentences
2. Identify which of our products are relevant to this tender
3. For each matched product, explain in 2-3 sentences why it fits the tender requirements

Respond in this exact JSON format:
{{
  "tender_summary": "...",
  "matched_products": [
    {{
      "name": "product name",
      "reason": "why it fits",
      "confidence": "High"
    }}
  ]
}}

For confidence, use:
- "High" if the product directly matches a specific requirement in the tender
- "Medium" if the product is relevant but not explicitly required
- "Low" if the product is a stretch match
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        text = (
            response.choices[0]
            .message.content.strip()
            .replace("```json", "")
            .replace("```", "")
        )
        result = json.loads(text)
        history = TenderHistory(
            filename=filename,
            summary=result["tender_summary"],
            matched_products=json.dumps(result["matched_products"]),
        )
        db.session.add(history)
        db.session.commit()

        # Store tender text in session for next steps
        from flask import session

        app.secret_key = "trident_secret_key"
        session["tender_text"] = tender_text
        session["tender_filename"] = filename

        return render_template(
            "tender_result.html",
            result=None,
            tender_text=tender_text,
            filename=filename,
            run_check=True,
        )

    return render_template("tender.html")


@app.route("/tender/ppt", methods=["POST"])
def tender_ppt():
    summary = request.form.get("summary")
    product_names = request.form.getlist("product_names")
    sections = request.form.getlist("sections")

    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    import copy

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # Color scheme from the template
    BLACK = RGBColor(0x00, 0x00, 0x00)
    LIGHT_GREY = RGBColor(0xC5, 0xCF, 0xD1)
    WHITE = RGBColor(0xFD, 0xFC, 0xFB)

    def add_slide(title_text, body_text):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        # Background
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = WHITE

        # Title bar
        from pptx.util import Inches, Pt

        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.4), Inches(12), Inches(0.8)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = BLACK

        # Divider line
        from pptx.util import Pt as PtLine

        line = slide.shapes.add_shape(
            1, Inches(0.5), Inches(1.3), Inches(12), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = LIGHT_GREY
        line.line.fill.background()

        # Body
        body_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(1.5), Inches(12), Inches(5.5)
        )
        tf2 = body_box.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = body_text
        p2.font.size = Pt(14)
        p2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        return slide

    # Cover
    if "cover" in sections:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background
        bg.fill.solid()
        bg.fill.fore_color.rgb = BLACK
        tb = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.2))
        p = tb.text_frame.paragraphs[0]
        p.text = "Trident Services Pvt Ltd"
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = WHITE
        tb2 = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(11), Inches(0.6))
        p2 = tb2.text_frame.paragraphs[0]
        p2.text = "Authorized Cummins Dealer | Proposal"
        p2.font.size = Pt(18)
        p2.font.color.rgb = LIGHT_GREY

    # Tender Summary
    if "tender_summary" in sections:
        add_slide("Tender Requirements", summary)

    # Products
    if "products" in sections:
        for name in product_names:
            product = Product.query.filter_by(name=name).first()
            if product:
                body = f"{product.description}\n\nKey Features:\n{product.features}\n\nApplications:\n{product.applications}"
                add_slide(product.name, body)

    # About
    if "about" in sections:
        add_slide(
            "About Trident Services",
            "Trident Services Pvt Ltd is an authorized Cummins dealer since 2004, "
            "promoted by three Ex-General Managers of Cummins India Limited with 23 years of experience.\n\n"
            "Headquartered in Pune, Maharashtra, we serve clients across Pune, Mumbai, Thane, "
            "Kolhapur, Satara, and surrounding regions.\n\n"
            "We provide end-to-end solutions including supply, installation, commissioning, "
            "and 24/7 after-sales support for all Cummins products.",
        )

    # Services
    if "services" in sections:
        add_slide(
            "Our Services",
            "• 24x7 Service Availability\n"
            "• 4-Hour Service Response Guarantee\n"
            "• Annual Maintenance Contracts (AMC)\n"
            "• Engine & Alternator Overhauling\n"
            "• Fuel System Repair & Calibration\n"
            "• Express Service Van\n"
            "• Cummins Ashwashan Extended Warranty\n"
            "• Paid / Call Base Services",
        )

    # Why Us
    if "why_us" in sections:
        add_slide(
            "Why Choose Trident Services?",
            "✓ Authorized Cummins Dealer since 2004\n"
            "✓ Promoted by Ex-Cummins General Managers with 23 years experience\n"
            "✓ 24/7 availability with 4-hour response guarantee\n"
            "✓ Serving Railways, Manufacturing, Data Centers, Healthcare & Real Estate\n"
            "✓ Complete lifecycle support — supply, install, maintain\n"
            "✓ Genuine Cummins parts and certified technicians\n"
            "✓ Coverage across Maharashtra including Pune, Mumbai, Kolhapur, Satara",
        )

    # Contact
    if "contact" in sections:
        add_slide(
            "Contact Us",
            "Head Office:\nTriden House, Survey No. 116, Mumbai-Bangalore Highway, Warje, Pune 411 058\n\n"
            "Navi Mumbai Office:\nEL 54, TTC Industrial Area, Mahape, Navi Mumbai 400 710\n\n"
            "Phone: +91 20 66266222 / 23\n"
            "Email: customercare@tridents.net\n"
            "After Hours: +91 98509 08146\n"
            "Website: www.tridentservices.co.in",
        )

    filename = "Trident_Proposal.pptx"
    prs.save(filename)
    return send_file(filename, as_attachment=True)


@app.route("/tender/eligibility", methods=["POST"])
def tender_eligibility():
    tender_text = request.form.get("tender_text")

    # Get company data
    profile = db.session.execute(
        text("SELECT * FROM company_profile WHERE id=1")
    ).fetchone()

    certs = db.session.execute(text("SELECT * FROM certifications")).fetchall()

    projects = db.session.execute(
        text("SELECT * FROM past_projects ORDER BY value_crore DESC")
    ).fetchall()

    # Build company summary for LLM
    cert_list = "\n".join(
        [f"- {c.name} ({c.issuing_body}, valid until {c.valid_until})" for c in certs]
    )
    project_list = "\n".join(
        [
            f"- {p.name} | Client: {p.client_name} ({p.client_type}) | Value: ₹{p.value_crore} Crore | Year: {p.completion_year} | Type: {p.project_type} | Voltage: {p.voltage_level}"
            for p in projects
        ]
    )

    prompt = f"""
You are an eligibility assessment assistant for Trident Engineers & Associates.

COMPANY PROFILE:
- Name: {profile.name}
- Annual Turnover: ₹{profile.annual_turnover_crore} Crore ({profile.turnover_year})
- Electrical Contractor License: {profile.electrical_contractor_license} ({profile.contractor_class})
- Established: {profile.established_year}

CERTIFICATIONS:
{cert_list}

PAST PROJECTS:
{project_list}

TENDER DOCUMENT (relevant sections):
{tender_text[:4000]}

YOUR TASK:
1. Extract the eligibility criteria from the tender (financial + technical + license requirements)
2. Check each criterion against the company profile
3. Give an overall verdict: ELIGIBLE, PARTIALLY ELIGIBLE, or NOT ELIGIBLE

Respond ONLY in this exact JSON format:
{{
  "tender_name": "short name of the tender",
  "tender_value_crore": 0.0,
  "overall_verdict": "ELIGIBLE or PARTIALLY ELIGIBLE or NOT ELIGIBLE",
  "verdict_reason": "one line summary",
  "criteria": [
    {{
      "requirement": "what the tender requires",
      "company_status": "what the company has",
      "result": "PASS or FAIL or PARTIAL",
      "notes": "brief explanation"
    }}
  ],
  "recommended_action": "what Trident should do next"
}}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]
    )
    text_response = (
        response.choices[0]
        .message.content.strip()
        .replace("```json", "")
        .replace("```", "")
    )
    eligibility = json.loads(text_response)

    # Save to tender history
    history = TenderHistory(
        filename=request.form.get("filename"),
        summary=eligibility.get("verdict_reason", ""),
        matched_products=json.dumps([]),
    )
    db.session.add(history)
    db.session.commit()

    return render_template(
        "tender_result.html", result=eligibility, tender_text=tender_text[:500]
    )


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
        model="llama-3.3-70b-versatile",
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
        model="llama-3.3-70b-versatile",
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


def _replace_text_in_slide(slide, replacements):
    def process_shapes(shapes):
        for shape in shapes:
            # Recurse into groups
            if shape.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
                process_shapes(shape.shapes)
                continue
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                # Merge all runs to handle split placeholders
                full_text = "".join(run.text for run in para.runs)
                replaced = False
                for placeholder, value in replacements.items():
                    if placeholder in full_text:
                        full_text = full_text.replace(placeholder, value)
                        replaced = True
                if replaced and para.runs:
                    para.runs[0].text = full_text
                    for run in para.runs[1:]:
                        run.text = ""
                elif not replaced:
                    # Per-run replacement for non-split cases
                    for run in para.runs:
                        for placeholder, value in replacements.items():
                            if placeholder in run.text:
                                run.text = run.text.replace(placeholder, value)

    process_shapes(slide.shapes)



def _remove_slide(prs, slide):
    """Remove a slide from the presentation."""
    xml_slides = prs.slides._sldIdLst
    slide_part = slide.part
    for sldId in list(xml_slides):
        rId = sldId.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        if rId and prs.slides.part.rels[rId].target_part == slide_part:
            xml_slides.remove(sldId)
            return

def _clone_slide(prs, template_slide):
    import copy
    from pptx.oxml.ns import qn
    from lxml import etree

    slide_layout = template_slide.slide_layout
    new_slide = prs.slides.add_slide(slide_layout)

    # Replace spTree content
    sp_tree = new_slide.shapes._spTree
    for child in list(sp_tree):
        sp_tree.remove(child)
    for child in template_slide.shapes._spTree:
        sp_tree.append(copy.deepcopy(child))

    # Copy background
    tmpl_bg = template_slide._element.find(qn("p:bg"))
    if tmpl_bg is not None:
        existing_bg = new_slide._element.find(qn("p:bg"))
        if existing_bg is not None:
            new_slide._element.remove(existing_bg)
        new_slide._element.insert(2, copy.deepcopy(tmpl_bg))

    # Copy image relationships with new rIds
    rId_map = {}
    for old_rId, rel in template_slide.part.rels.items():
        if "image" in rel.reltype:
            new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
            rId_map[old_rId] = new_rId

    r_embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
    for blip in new_slide._element.findall(
        ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
    ):
        old_rId = blip.get(r_embed_attr)
        if old_rId in rId_map:
            blip.set(r_embed_attr, rId_map[old_rId])

    # === MOVE the new slide to come right after the template slide ===
    sldIdLst = prs.slides._sldIdLst
    all_sldIds = list(sldIdLst)
    
    # Find template slide's position
    template_part = template_slide.part
    template_pos = None
    for i, sldId in enumerate(all_sldIds):
        rId = sldId.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        if prs.slides.part.rels[rId].target_part == template_part:
            template_pos = i
            break

    if template_pos is not None:
        # The new slide is currently last — move it to template_pos + 1
        new_sldId = all_sldIds[-1]
        sldIdLst.remove(new_sldId)
        sldIdLst.insert(template_pos + 1, new_sldId)

    return new_slide

def _replace_slide_image(slide, image_url, target_index=1):
    """Download image_url and replace the content blip (not the logo) on the slide."""
    import requests as _req

    try:
        resp = _req.get(image_url, timeout=10)
        resp.raise_for_status()
        image_bytes = resp.content

        blips = slide._element.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
        )
        if not blips:
            print("No blip found on slide.")
            return

        if len(blips) <= target_index:
            print(f"Only {len(blips)} blip(s) found, can't use index {target_index}, using last.")
            target_index = -1

        blip = blips[target_index]
        r_embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        rId = blip.get(r_embed_attr)

        if rId and rId in slide.part.rels:
            slide.part.rels[rId].target_part._blob = image_bytes
            print(f"Replaced image rId={rId}")
        else:
            print(f"rId={rId} not found in slide relationships.")

    except Exception as e:
        import traceback
        print(f"Image replacement failed for {image_url}: {e}")
        traceback.print_exc()

@app.route("/generate-service-ppt/<int:id>")
def generate_service_ppt(id):
    """Generate a PPT for a single service using the Brand Strategy template (Slide 6)."""
    service = Service.query.get_or_404(id)

    content = None
    if service.detailed_content:
        try:
            content = json.loads(service.detailed_content)
        except:
            content = None

    service_name = service.name
    overview_text = content["overview"] if content and content.get("overview") else (service.short_description or "")
    services_text = "\n".join([f"- {f}" for f in content["key_features"]]) if content and content.get("key_features") else (service.short_description or "")
    why_text = "\n".join([f"- {r}" for r in content["why_choose_us"]]) if content and content.get("why_choose_us") else "- Professional team\n- Quality workmanship\n- Indian standards compliance\n- End-to-end project management"

    template_path = os.path.join("templates", "Brand Strategy.pptx")
    prs = Presentation(template_path)
    slide = prs.slides[5]  # Slide 6 = service template

    _replace_text_in_slide(slide, {
        "{{SERVICE_NAME}}": service_name,
        "{{SERVICE_OVERVIEW}}": overview_text,
        "{{THE_SERVICES}}": services_text,
        "{{WHY_CHOOSE_US}}": why_text,
    })

    if service.image_url:
        _replace_slide_image(slide, service.image_url, target_index=1)

    # Clear manufacturing placeholders on slide 7 so they don't appear raw
    _replace_text_in_slide(prs.slides[6], {
        "{{MANUFACTURING_NAME}}": "",
        "{{MANUFACTURING_OVERVIEW}}": "",
    })

    safe_name = service.name.replace("/", "-").replace("\\", "-").replace(":", "-").strip()
    filename = f"{safe_name}_Service.pptx"
    output_path = os.path.join("static", "uploads", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return send_file(output_path, as_attachment=True, download_name=filename)


@app.route("/generate-manufacturing-ppt/<int:id>")
def generate_manufacturing_ppt(id):
    """Generate a PPT for a single manufacturing product using the Brand Strategy template (Slide 7)."""
    import requests as req_lib

    product = ManufacturingProduct.query.get_or_404(id)

    content = None
    if product.detailed_content:
        try:
            content = json.loads(product.detailed_content)
        except:
            content = None

    mfg_name = product.name
    overview_text = content["overview"] if content and content.get("overview") else (product.short_description or "")

    template_path = os.path.join("templates", "Brand Strategy.pptx")
    prs = Presentation(template_path)
    slide = prs.slides[6]  # Slide 7 = manufacturing template

    _replace_text_in_slide(slide, {
        "{{MANUFACTURING_NAME}}": mfg_name,
        "{{MANUFACTURING_OVERVIEW}}": overview_text,
    })

    if product.image_url:
        _replace_slide_image(slide, product.image_url, target_index=1)

    # Clear service placeholders on slide 6
    _replace_text_in_slide(prs.slides[5], {
        "{{SERVICE_NAME}}": "",
        "{{SERVICE_OVERVIEW}}": "",
        "{{THE_SERVICES}}": "",
        "{{WHY_CHOOSE_US}}": "",
    })

    safe_name = product.name.replace("/", "-").replace("\\", "-").replace(":", "-").strip()
    filename = f"{safe_name}_Manufacturing.pptx"
    output_path = os.path.join("static", "uploads", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return send_file(output_path, as_attachment=True, download_name=filename)


@app.route("/generate-all-services-ppt")
def generate_all_services_ppt():
    all_services = Service.query.all()
    if not all_services:
        return redirect("/services")

    template_path = os.path.join("templates", "Brand Strategy.pptx")

    all_slides = []
    for service in all_services:
        # Fresh presentation for EACH service
        prs_single = Presentation(template_path)
        slide = prs_single.slides[5]

        content = None
        if service.detailed_content:
            try:
                content = json.loads(service.detailed_content)
            except:
                content = None

        overview_text = content["overview"] if content and content.get("overview") else (service.short_description or "")
        services_text = "\n".join([f"• {f}" for f in content["key_features"]]) if content and content.get("key_features") else (service.short_description or "")
        why_text = "\n".join([f"✓ {r}" for r in content["why_choose_us"]]) if content and content.get("why_choose_us") else "✓ Professional team\n✓ Quality workmanship"

        _replace_text_in_slide(slide, {
            "{{SERVICE_NAME}}": service.name,
            "{{SERVICE_OVERVIEW}}": overview_text,
            "{{THE_SERVICES}}": services_text,
            "{{WHY_CHOOSE_US}}": why_text,
        })
        if service.image_url:
            _replace_slide_image(slide, service.image_url, target_index=1)

        all_slides.append((prs_single, 5))  # (presentation, slide_index)

    # Merge all slide-6s into one presentation
    base_prs, base_idx = all_slides[0]
    import copy
    from pptx.oxml.ns import qn

    for prs_single, slide_idx in all_slides[1:]:
        src_slide = prs_single.slides[slide_idx]
        slide_layout = base_prs.slide_layouts[6]
        new_slide = base_prs.slides.add_slide(slide_layout)

        sp_tree = new_slide.shapes._spTree
        for child in list(sp_tree):
            sp_tree.remove(child)
        for child in src_slide.shapes._spTree:
            sp_tree.append(copy.deepcopy(child))

        tmpl_bg = src_slide._element.find(qn("p:bg"))
        if tmpl_bg is not None:
            existing_bg = new_slide._element.find(qn("p:bg"))
            if existing_bg is not None:
                new_slide._element.remove(existing_bg)
            new_slide._element.insert(2, copy.deepcopy(tmpl_bg))

        r_embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        rId_map = {}
        for old_rId, rel in src_slide.part.rels.items():
            if "image" in rel.reltype:
                new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
                rId_map[old_rId] = new_rId

        for blip in new_slide._element.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
        ):
            old_rId = blip.get(r_embed_attr)
            if old_rId in rId_map:
                blip.set(r_embed_attr, rId_map[old_rId])

    # Remove all non-service slides from base_prs (keep only slide at base_idx)
    # Collect the slide OBJECT to keep, then remove everything else
    keep_slide = base_prs.slides[base_idx]
    all_slide_objects = list(base_prs.slides)
    for s in all_slide_objects:
        if s != keep_slide:
            _remove_slide(base_prs, s)

    output_path = os.path.join("static", "uploads", "All_Services_Presentation.pptx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_prs.save(output_path)
    return send_file(output_path, as_attachment=True, download_name="All_Services_Presentation.pptx")

@app.route("/generate-all-manufacturing-ppt")
def generate_all_manufacturing_ppt():
    import copy
    from pptx.oxml.ns import qn

    all_products = ManufacturingProduct.query.all()
    if not all_products:
        return redirect("/manufacturing")

    template_path = os.path.join("templates", "Brand Strategy.pptx")

    all_slides = []
    for product in all_products:
        prs_single = Presentation(template_path)
        slide = prs_single.slides[6]
        content = None
        if product.detailed_content:
            try:
                content = json.loads(product.detailed_content)
            except:
                content = None

        overview_text = content["overview"] if content and content.get("overview") else (product.short_description or "")
        _replace_text_in_slide(slide, {
            "{{MANUFACTURING_NAME}}": product.name,
            "{{MANUFACTURING_OVERVIEW}}": overview_text,
        })
        if product.image_url:
            _replace_slide_image(slide, product.image_url, target_index=1)

        all_slides.append((prs_single, 6))

    base_prs, base_idx = all_slides[0]
    for prs_single, slide_idx in all_slides[1:]:
        src_slide = prs_single.slides[slide_idx]
        slide_layout = base_prs.slide_layouts[6]
        new_slide = base_prs.slides.add_slide(slide_layout)

        sp_tree = new_slide.shapes._spTree
        for child in list(sp_tree):
            sp_tree.remove(child)
        for child in src_slide.shapes._spTree:
            sp_tree.append(copy.deepcopy(child))

        tmpl_bg = src_slide._element.find(qn("p:bg"))
        if tmpl_bg is not None:
            existing_bg = new_slide._element.find(qn("p:bg"))
            if existing_bg is not None:
                new_slide._element.remove(existing_bg)
            new_slide._element.insert(2, copy.deepcopy(tmpl_bg))

        r_embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        rId_map = {}
        for old_rId, rel in src_slide.part.rels.items():
            if "image" in rel.reltype:
                new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
                rId_map[old_rId] = new_rId
        for blip in new_slide._element.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
        ):
            old_rId = blip.get(r_embed_attr)
            if old_rId in rId_map:
                blip.set(r_embed_attr, rId_map[old_rId])

    # Collect the slide OBJECT to keep, then remove everything else
    keep_slide = base_prs.slides[base_idx]
    all_slide_objects = list(base_prs.slides)
    for s in all_slide_objects:
        if s != keep_slide:
            _remove_slide(base_prs, s)

    output_path = os.path.join("static", "uploads", "All_Manufacturing_Presentation.pptx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_prs.save(output_path)
    return send_file(output_path, as_attachment=True, download_name="All_Manufacturing_Presentation.pptx")
@app.route("/generate-custom-ppt", methods=["POST"])
def generate_custom_ppt():
    import copy
    from pptx.oxml.ns import qn

    service_ids = request.form.getlist("service_ids")
    product_ids = request.form.getlist("product_ids")

    if not service_ids and not product_ids:
        return redirect(request.referrer or "/services")

    template_path = os.path.join("templates", "Brand Strategy.pptx")

    def merge_slide_into(base_prs, src_slide):
        """Copy src_slide into base_prs as a new last slide."""
        slide_layout = base_prs.slide_layouts[6]
        new_slide = base_prs.slides.add_slide(slide_layout)

        sp_tree = new_slide.shapes._spTree
        for child in list(sp_tree):
            sp_tree.remove(child)
        for child in src_slide.shapes._spTree:
            sp_tree.append(copy.deepcopy(child))

        tmpl_bg = src_slide._element.find(qn("p:bg"))
        if tmpl_bg is not None:
            existing_bg = new_slide._element.find(qn("p:bg"))
            if existing_bg is not None:
                new_slide._element.remove(existing_bg)
            new_slide._element.insert(2, copy.deepcopy(tmpl_bg))

        r_embed_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        rId_map = {}
        for old_rId, rel in src_slide.part.rels.items():
            if "image" in rel.reltype:
                new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
                rId_map[old_rId] = new_rId

        for blip in new_slide._element.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
        ):
            old_rId = blip.get(r_embed_attr)
            if old_rId in rId_map:
                blip.set(r_embed_attr, rId_map[old_rId])

    # Build list of (src_presentation, slide_index) for each selected item
    all_items = []  # (prs_single, slide_index)

    for sid in service_ids:
        service = Service.query.get(int(sid))
        if not service:
            continue
        content = None
        if service.detailed_content:
            try:
                content = json.loads(service.detailed_content)
            except:
                content = None

        prs_single = Presentation(template_path)
        slide = prs_single.slides[5]
        overview_text = content["overview"] if content and content.get("overview") else (service.short_description or "")
        services_text = "\n".join([f"• {f}" for f in content["key_features"]]) if content and content.get("key_features") else (service.short_description or "")
        why_text = "\n".join([f"✓ {r}" for r in content["why_choose_us"]]) if content and content.get("why_choose_us") else "✓ Professional team\n✓ Quality workmanship"

        _replace_text_in_slide(slide, {
            "{{SERVICE_NAME}}": service.name,
            "{{SERVICE_OVERVIEW}}": overview_text,
            "{{THE_SERVICES}}": services_text,
            "{{WHY_CHOOSE_US}}": why_text,
        })
        if service.image_url:
            _replace_slide_image(slide, service.image_url, target_index=1)

        all_items.append((prs_single, 5))

    for pid in product_ids:
        product = ManufacturingProduct.query.get(int(pid))
        if not product:
            continue
        content = None
        if product.detailed_content:
            try:
                content = json.loads(product.detailed_content)
            except:
                content = None

        prs_single = Presentation(template_path)
        slide = prs_single.slides[6]
        overview_text = content["overview"] if content and content.get("overview") else (product.short_description or "")

        _replace_text_in_slide(slide, {
            "{{MANUFACTURING_NAME}}": product.name,
            "{{MANUFACTURING_OVERVIEW}}": overview_text,
        })
        if product.image_url:
            _replace_slide_image(slide, product.image_url, target_index=1)

        all_items.append((prs_single, 6))

    if not all_items:
        return redirect(request.referrer or "/services")

    # Use first item as base, merge rest into it
    base_prs, base_idx = all_items[0]
    for prs_single, slide_idx in all_items[1:]:
        merge_slide_into(base_prs, prs_single.slides[slide_idx])

    # Remove all slides except the one we want from base_prs
    # Keep only base_idx, remove everything else
    # Collect the slide OBJECT to keep, then remove everything else
    keep_slide = base_prs.slides[base_idx]
    all_slide_objects = list(base_prs.slides)
    for s in all_slide_objects:
        if s != keep_slide:
            _remove_slide(base_prs, s)

    filename = "Trident_Custom_Selection.pptx"
    output_path = os.path.join("static", "uploads", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_prs.save(output_path)
    return send_file(output_path, as_attachment=True, download_name=filename)

@app.route("/build-ppt")
def build_ppt_picker():
    all_services = Service.query.all()
    all_products = ManufacturingProduct.query.all()
    return render_template("build_ppt.html", services=all_services, products=all_products)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)
