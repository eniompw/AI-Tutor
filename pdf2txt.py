import urllib.request
import glob
from pypdf import PdfReader
import re

url = "https://ocr.org.uk/Images/676742-question-paper-computer-systems.pdf"
# url = "https://ocr.org.uk/Images/676943-mark-scheme-computer-systems.pdf"
# Download the file and specify the filename
urllib.request.urlretrieve(url, "h446-01-qp.pdf")
print("File downloaded")

# Search for all files ending with ".pdf" in the current directory
pdf_files = glob.glob("*.pdf")
# Read the first PDF file in the list
reader = PdfReader(pdf_files[0])

def strip_dots(text):
    # Replace sequences of 2 or more periods with a single period
    cleaned_text = re.sub(r'\.{2,}', '', text)
    return cleaned_text

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
f = open("ms.txt", "w")
# Write the contents of the variable "text" to the opened file
f.write(text)
# Close the file to release resources
f.close()
