import urllib.request

url = "https://ocr.org.uk/Images/676742-question-paper-computer-systems.pdf"
# url = "https://ocr.org.uk/Images/676943-mark-scheme-computer-systems.pdf"

# Download the file and specify the filename
urllib.request.urlretrieve(url, "h446-01-qp.pdf")

print("File downloaded")
