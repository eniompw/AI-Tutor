import glob
from pypdf import PdfReader
import re

# Search for all files ending with ".pdf" in the current directory
pdf_files = glob.glob("*.pdf")
reader = PdfReader(pdf_files[1])

def strip_dots(text):
    # Replace sequences of 2 or more periods with a single period
    cleaned_text = re.sub(r'\.{2,}', '', text)
    return cleaned_text

text = ""
for i in range(7,len(reader.pages)-1):
    if "BLANK PAGE" not in reader.pages[i].extract_text():
        text += strip_dots(reader.pages[i].extract_text())
        if "END OF QUESTION PAPER" in text:
            break

f = open("ms.txt", "w")
f.write(text)
f.close()
