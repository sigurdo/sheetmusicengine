import cv2
import time
import pytesseract
import PyPDF2
import os
import yaml
import argparse
import sheeetmusicEngine as engine

# print("Hello sheet music")

def getPdfPaths(directory):
	pdfPaths = []
	sheetNames = []
	for (dirpath, dirnames, filenames) in os.walk(directory):
		for filename in filenames:
			name, extension = os.path.splitext(filename)
			if (extension.lower() == ".pdf"):
				pdfPaths.append(os.path.join(dirpath, filename))
				sheetNames.append(name)
	return pdfPaths, sheetNames

def clearDir(directory):
	for (dirpath, dirnames, filenames) in os.walk(directory):
		for filename in filenames:
			os.remove(os.path.join(directory, filename))

formatter = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=50)
parser = argparse.ArgumentParser(description="Develop and test sheetmusicUploader", formatter_class=formatter)
parser.add_argument("-p", "--pdf", type=str, default="all", metavar="PDF_PATH", help="Select a pdf to analyze")
parser.add_argument("-s", "--start-page", type=int, default=1, metavar="PAGE_NR", help="Select a page in the sheet pdf to start from")
parser.add_argument("-e", "--end-page", type=int, default=None, metavar="PAGE_NR", help="Select a page in the sheet pdf to end with")
parser.add_argument("-x", "--single-page", type=int, default=None, metavar="PAGE_NR", help="Select a single page in the sheet pdf to analyze. Overrides any specified start-page and end-page")
args = parser.parse_args()

if args.single_page:
	args.start_page = args.single_page
	args.end_page = args.single_page

INPUT_PDF_DIR = "input_pdfs"
OUTPUT_PDF_DIR = "output_pdfs"
TMP_PATH = "tmp"
BOUNDING_BOX_PATH = "images_with_bounding_boxes"
INSTRUMENTS_YAML_PATH = "instruments.yaml"
with open(INSTRUMENTS_YAML_PATH, "r") as file:
	INSTRUMENTS = yaml.safe_load(file)

if not os.path.exists(INPUT_PDF_DIR): os.mkdir(INPUT_PDF_DIR)
if not os.path.exists(OUTPUT_PDF_DIR): os.mkdir(OUTPUT_PDF_DIR)
if not os.path.exists(TMP_PATH): os.mkdir(TMP_PATH)
if not os.path.exists(BOUNDING_BOX_PATH): os.mkdir(BOUNDING_BOX_PATH)

clearDir(TMP_PATH)
pdfPaths, sheetNames = getPdfPaths(INPUT_PDF_DIR) if args.pdf == "all" else \
	([args.pdf], [os.path.splitext(os.path.basename(args.pdf))[0]])

for sheetName in sheetNames:
	if not os.path.exists(os.path.join(BOUNDING_BOX_PATH, sheetName)): os.mkdir(os.path.join(BOUNDING_BOX_PATH, sheetName))
	if not os.path.exists(os.path.join(OUTPUT_PDF_DIR, sheetName)): os.mkdir(os.path.join(OUTPUT_PDF_DIR, sheetName))

for i, pdfPath in enumerate(pdfPaths):
	sheetName = sheetNames[i]
	print("Analyzing ", sheetNames[pdfPaths.index(pdfPath)], ":", sep="")
	parts, instrumentsDefaultParts = engine.processUploadedPdf(pdfPath, TMP_PATH, INSTRUMENTS)
	print("Splitting pdf...")
	for part in parts:
		pdf = PyPDF2.PdfFileReader(pdfPath)
		pdf_writer = PyPDF2.PdfFileWriter()
		for page in range(part["fromPage"] - 1, part["toPage"]):
			pdf_writer.addPage(pdf.getPage(page))

		with open(os.path.join(OUTPUT_PDF_DIR, sheetName, part["name"]+".pdf"), 'wb') as output_pdf:
			pdf_writer.write(output_pdf)
	print("Done!")
