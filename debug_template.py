from pptx import Presentation
from lxml import etree

prs = Presentation("templates/Brand Strategy.pptx")
slide = prs.slides[5]

# Find all blips
blips = slide._element.findall(
    ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
)
print(f"Found {len(blips)} blip(s)")
for blip in blips:
    r_embed = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
    print(f"  blip rId: {r_embed}")
    if r_embed in slide.part.rels:
        rel = slide.part.rels[r_embed]
        print(f"  -> target: {rel.target_ref}")