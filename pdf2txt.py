import urllib.request
import glob
from pypdf import PdfReader
import os
import re

qpurl = "https://ocr.org.uk/Images/676742-question-paper-computer-systems.pdf"
msurl = "https://ocr.org.uk/Images/676943-mark-scheme-computer-systems.pdf"
# Download the file and specify the filename
urllib.request.urlretrieve(qpurl, "/tmp/qp.pdf")
urllib.request.urlretrieve(msurl, "/tmp/ms.pdf")

def strip_dots(text):
    # Replace sequences of 2 or more periods with a single period
    cleaned_text = re.sub(r'\.{2,}', '', text)

    # Remove specific phrases that are not needed
    cleaned_text = cleaned_text.replace("© OCR 2022 ", "")
    cleaned_text = cleaned_text.replace("Turn over ", "")
    
    # Remove any empty lines that may be left
    cleaned_text = "\n".join([line for line in cleaned_text.split("\n") if line.strip() != ""])
    return cleaned_text

# Search for all files ending with ".pdf" in the current directory
pdf_files = glob.glob("/tmp/*.pdf")
# Iterate through the list of PDF files
for pdf_file in pdf_files:
    # Create a PdfReader object for each file
    reader = PdfReader(pdf_file)
    # Get the file name from the file path
    fullname = os.path.basename(pdf_file)
    file_name, _ = os.path.splitext(fullname)
    # Initialize an empty string to store the extracted text
    text = ""
    # Loop through all pages except the first and last (indexing starts from 0)
    for i in range(1, len(reader.pages) - 1):
        # Check if the current page doesn't contain "BLANK PAGE" text
        if "BLANK PAGE" not in reader.pages[i].extract_text():
            # Extract text from the page and remove any trailing dots using strip_dots function
            text += strip_dots(reader.pages[i].extract_text())
            # Check if the accumulated text contains "END OF QUESTION PAPER"
            if "END OF QUESTION PAPER" in text:
                # Exit the loop if the end of question paper is found
                break

    # Open the file named "ms.txt" in write mode ("w")
    f = open("/tmp/" + file_name + ".txt", "w")
    # Write the contents of the variable "text" to the opened file
    f.write(text)
    # Close the file to release resources
    f.close()
