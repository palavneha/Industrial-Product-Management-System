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
from groq import Groq
from datetime import datetime
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Proposal by Trident Services Pvt Ltd"
    slide.placeholders[1].text = "Authorized Cummins Dealer"

    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Tender Requirements"
    slide2.placeholders[1].text = summary

    for name in product_names:
        product = Product.query.filter_by(name=name).first()
        if product:
            s = prs.slides.add_slide(prs.slide_layouts[1])
            s.shapes.title.text = product.name
            s.placeholders[1].text = (
                f"{product.description}\n\nFeatures:\n{product.features}\n\nApplications:\n{product.applications}"
            )

    slide_last = prs.slides.add_slide(prs.slide_layouts[1])
    slide_last.shapes.title.text = "Why Trident Services?"
    slide_last.placeholders[1].text = (
        "✓ Authorized Cummins Dealer since 2004\n✓ 24/7 Service Availability\n✓ 4 Hour Response Guarantee\n✓ Serving Railways, Manufacturing, Data Centers & Healthcare"
    )

    filename = "Trident_Proposal.pptx"
    prs.save(filename)
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)
