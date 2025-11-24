
import os
import logging
from zoterorag.core.utils.pdf_extractor import extract_text_from_pdf

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

def main():
    pdf_path = "tests/test.pdf"
    
    print("--- Test 1: Default settings, no profiling ---")
    extract_text_from_pdf(pdf_path)
    
    print("\n--- Test 2: Profiling enabled ---")
    os.environ["ZOTERORAG_PROFILE_PDF"] = "1"
    extract_text_from_pdf(pdf_path)
    
    print("\n--- Test 3: Custom settings (x_tolerance=5) + Profiling ---")
    os.environ["ZOTERORAG_PDF_SETTINGS"] = '{"x_tolerance": 5}'
    extract_text_from_pdf(pdf_path)

if __name__ == "__main__":
    main()
