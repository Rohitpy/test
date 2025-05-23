import fitz
import io
from PIL import Image
import re
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
import os
from pathlib import Path

def clean_text_for_markdown(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'([#*`_~\[\]])', r'\\\1', text)
    return text

def get_element_location(element):
    """Get the y-coordinate of an element (text block or image)"""
    if isinstance(element, fitz.Rect):  # Image rectangle
        return element.y0
    elif isinstance(element, dict):  # Text block
        return element.get('bbox')[1]  # y0 coordinate
    return 0

def initialize_image_explainer():
    """Initialize the SmolDocling model for image explanation"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained("smoldocling")
    model = AutoModelForVision2Seq.from_pretrained(
        "smoldocling",
        torch_dtype=torch.bfloat16,
        _attn_implementation="flash_attention_2" if device == "cuda" else "eager"
    ).to(device)
    return processor, model, device

def explain_image(image_path, processor, model, device):
    """Generate text explanation for an image"""
    image = load_image(image_path)
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Describe this image in detail."}
            ]
        },
    ]
    
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt")
    inputs = inputs.to(device)
    
    generated_ids = model.generate(**inputs, max_new_tokens=8192)
    prompt_length = inputs.input_ids.shape[1]
    trimmed_generated_ids = generated_ids[:, prompt_length:]
    explanation = processor.batch_decode(
        trimmed_generated_ids,
        skip_special_tokens=True,
    )[0].lstrip()
    
    return explanation

def is_scanned_pdf(pdf_path):
    """Check if PDF is scanned by analyzing text content"""
    extracted_text = ''.join([page.get_text() for page in fitz.open(pdf_path)])
    return len(extracted_text.strip()) == 0 or len(extracted_text) < 100

def process_scanned_pdf(pdf_file, output_file, processor, model, device, images_dir):
    """Process a scanned PDF by treating each page as an image"""
    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        
        # Write page header
        output_file.write(f"# Page {page_index + 1}\n\n")
        
        # Convert page to image
        pix = page.get_pixmap()
        image_name = f"page_{page_index + 1}.png"
        image_path = images_dir / image_name
        pix.save(str(image_path))
        
        # Get explanation for the page image
        explanation = explain_image(str(image_path), processor, model, device)
        
        # Write to markdown
        output_file.write(f"![Page {page_index + 1}](images/{image_name})\n\n")
        output_file.write(f"*Page {page_index + 1} content:*\n\n{explanation}\n\n")
        output_file.write("\n---\n\n")

def process_regular_pdf(pdf_file, output_file, processor, model, device, images_dir):
    """Process a regular PDF with text and images"""
    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        
        # Write page header
        output_file.write(f"# Page {page_index + 1}\n\n")
        
        # Get all elements (text blocks and images) with their locations
        elements = []
        
        # Get text blocks
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                elements.append({"type": "text", "data": block})
        
        # Get images
        image_list = page.get_images(full=True)
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            image_rects = page.get_image_rects(xref)
            if image_rects:
                elements.append({
                    "type": "image",
                    "rect": image_rects[0],
                    "xref": xref,
                    "index": image_index
                })
        
        # Sort elements by their y-coordinate (top to bottom)
        elements.sort(key=lambda x: (
            x["rect"].y0 if x["type"] == "image" 
            else x["data"]["bbox"][1]
        ))
        
        # Process elements in order
        for element in elements:
            if element["type"] == "image":
                # Handle image
                xref = element["xref"]
                rect = element["rect"]
                image_index = element["index"]
                
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_name = f"image{page_index+1}_{image_index}.{image_ext}"
                image_path = images_dir / image_name
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                    print(f"[+] Image saved as {image_path}")
                
                explanation = explain_image(str(image_path), processor, model, device)
                output_file.write(f"![Image {page_index+1}_{image_index}](images/{image_name})\n")
                output_file.write(f"*Image location: ({rect.x0:.0f}, {rect.y0:.0f}) to ({rect.x1:.0f}, {rect.y1:.0f})*\n\n")
                output_file.write(f"*Image explanation: {explanation}*\n\n")
            
            else:
                # Handle text block
                block = element["data"]
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text.strip():
                            font_size = span["size"]
                            font_flags = span["flags"]
                            
                            formatted_text = clean_text_for_markdown(text)
                            
                            if font_size >= 18:
                                formatted_text = f"## {formatted_text}"
                            elif font_size >= 14:
                                formatted_text = f"### {formatted_text}"
                            
                            if font_flags & 2**4:  # Bold
                                formatted_text = f"**{formatted_text}**"
                            if font_flags & 2**1:  # Italic
                                formatted_text = f"*{formatted_text}*"
                            
                            output_file.write(f"{formatted_text}\n\n")
        
        output_file.write("\n---\n\n")  # Page separator

# Main processing logic
markdown_dir = Path("markdown")
markdown_dir.mkdir(exist_ok=True)

images_dir = markdown_dir / "images"
images_dir.mkdir(exist_ok=True)

file = "pdfs\Incident Management SOP.pdf"
output_filename = Path(file).stem + "_extracted.md"
output_path = markdown_dir / output_filename

# Check if PDF is scanned
is_scanned = is_scanned_pdf(file)
print(f"Processing {'scanned' if is_scanned else 'regular'} PDF...")

pdf_file = fitz.open(file)
processor, model, device = initialize_image_explainer()

with open(output_path, "w", encoding="utf-8") as output_file:
    if is_scanned:
        process_scanned_pdf(pdf_file, output_file, processor, model, device, images_dir)
    else:
        process_regular_pdf(pdf_file, output_file, processor, model, device, images_dir)

print(f"Conversion complete. Check '{output_path}' for the Markdown output.")
