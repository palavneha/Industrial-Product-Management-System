from flask import Flask, json, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
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

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
load_dotenv()


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import os

app = Flask(__name__)
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


@app.route("/")
def home():

    recent_products = Product.query.order_by(Product.id.desc()).limit(4).all()

    return render_template("home.html", products=recent_products)


from sqlalchemy import or_


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

        return render_template(
            "tender_result.html", result=result, tender_text=full_text[:500]
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)
