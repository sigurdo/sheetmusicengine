import cv2
import time
import pytesseract
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
TMP_PATH = "tmp"
BOUNDING_BOX_PATH = "images_with_bounding_boxes"
INSTRUMENTS_YAML_PATH = "instruments.yaml"
with open(INSTRUMENTS_YAML_PATH, "r") as file:
	INSTRUMENTS = yaml.safe_load(file)

if not os.path.exists(INPUT_PDF_DIR): os.mkdir(INPUT_PDF_DIR)
if not os.path.exists(TMP_PATH): os.mkdir(TMP_PATH)
if not os.path.exists(BOUNDING_BOX_PATH): os.mkdir(BOUNDING_BOX_PATH)

clearDir(TMP_PATH)
pdfPaths, sheetNames = getPdfPaths(INPUT_PDF_DIR) if args.pdf == "all" else \
	([args.pdf], [os.path.splitext(os.path.basename(args.pdf))[0]])

for sheetName in sheetNames:
	if not os.path.exists(os.path.join(BOUNDING_BOX_PATH, sheetName)): os.mkdir(os.path.join(BOUNDING_BOX_PATH, sheetName))

for pdfPath in pdfPaths:
	imagePaths = engine.generateImagesFromPdf(pdfPath, TMP_PATH, args.start_page, args.end_page)
	predictionsTables = ""
	for i in range(len(imagePaths)):
		imagePath = imagePaths[i]
		print("Analyzing ", imagePath, " from ", sheetNames[pdfPaths.index(pdfPath)], ":", sep="")
		img = engine.cropImage(cv2.imread(imagePath))
		detectionData = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config="--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng")
		imgWithBoxes, nicePrint = engine.processDetectionData(detectionData, img)
		cv2.imwrite(os.path.join(BOUNDING_BOX_PATH, sheetNames[pdfPaths.index(pdfPath)], f"boxes_{i}.jpg"), imgWithBoxes)
		print(nicePrint)
		predictionsTables += f"{sheetNames[pdfPaths.index(pdfPath)]}, {imagePath}:\n{nicePrint}\n"
		partNames, instrumentses = engine.predictParts(detectionData, INSTRUMENTS, img.shape[1], img.shape[0])
		nicePrint = f"partNames: {partNames}, instrumentses: {instrumentses}\n"
		print(nicePrint)
		predictionsTables += f"{nicePrint}\n\n"
	with open(os.path.join(BOUNDING_BOX_PATH, sheetNames[pdfPaths.index(pdfPath)], "predictions.txt"), "w") as file:
		file.write(predictionsTables)
