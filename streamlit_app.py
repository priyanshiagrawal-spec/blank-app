import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

# ---------------- FONT LOADER ----------------
def load_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

# ---------------- TEXT POSITION ----------------
def get_centered_position(text, font, y, width):
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    return ((width - text_width) // 2, y)

# ---------------- GENERATE CARDS ----------------
def generate_cards(df, templates, positions, font_size):
    zip_buffer = io.BytesIO()
    font = load_font(font_size)

    with tempfile.TemporaryDirectory() as tmpdir:
        progress = st.progress(0)

        for i, row in df.iterrows():
            template = templates[i % len(templates)]
            pos = positions[i % len(positions)]

            name = str(row['Owner Name'])
            business = str(row['Business Name'])

            img = template.copy()
            draw = ImageDraw.Draw(img)

            name_pos = get_centered_position(name, font, pos['name_y'], img.width)
            bus_pos = get_centered_position(f"({business})", font, pos['business_y'], img.width)

            draw.text(name_pos, name, fill="black", font=font)
            draw.text(bus_pos, f"({business})", fill="black", font=font)

            file_path = os.path.join(tmpdir, f"{business.replace(' ', '_')}.png")
            img.save(file_path)

            progress.progress((i + 1) / len(df))

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for file in os.listdir(tmpdir):
                z.write(os.path.join(tmpdir, file), file)

    return zip_buffer.getvalue()

# ---------------- UI ----------------
st.set_page_config(page_title="🎂 Card Generator", layout="wide")

st.title("🎂 Birthday Card Generator")

# Upload Excel
excel_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

# Upload Templates
templates_files = st.file_uploader(
    "Upload Templates (multiple allowed)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Font size
font_size = st.slider("Font Size", 10, 120, 50)

templates = []
positions = []

# Handle templates
if templates_files:
    for i, file in enumerate(templates_files):
        img = Image.open(file)
        templates.append(img)

        st.subheader(f"Template {i+1} Settings")

        col1, col2 = st.columns(2)

        with col1:
            name_y = st.slider(f"Name Y (Template {i+1})", 0, img.height, img.height // 2)

        with col2:
            business_y = st.slider(f"Business Y (Template {i+1})", 0, img.height, img.height // 2 + 50)

        positions.append({
            "name_y": name_y,
            "business_y": business_y
        })

        # Preview
        font = load_font(font_size)
        preview = img.copy()
        draw = ImageDraw.Draw(preview)

        draw.text(
            get_centered_position("John Doe", font, name_y, img.width),
            "John Doe", fill="black", font=font
        )
        draw.text(
            get_centered_position("(My Business)", font, business_y, img.width),
            "(My Business)", fill="black", font=font
        )

        st.image(preview, width=300)

# Generate button
if excel_file and templates:
    if st.button("🚀 Generate Cards"):
        try:
            # READ EXCEL (FIXED)
            df = pd.read_excel(excel_file, engine="openpyxl")

            required = {"Owner Name", "Business Name"}
            if not required.issubset(df.columns):
                st.error("Excel must contain 'Owner Name' and 'Business Name'")
                st.stop()

            with st.spinner("Generating cards..."):
                zip_data = generate_cards(df, templates, positions, font_size)

            st.success("✅ Cards generated successfully!")

            # Download
            st.download_button(
                "📥 Download ZIP",
                zip_data,
                file_name="birthday_cards.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Instructions
st.markdown("""
---
### 📌 Instructions

1. Upload Excel with:
   - Owner Name
   - Business Name

2. Upload templates

3. Adjust positions

4. Generate & Download 🎉
""")
