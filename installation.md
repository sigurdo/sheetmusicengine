# Hvordan installere sheetmusicengine

## 1. Klon repo:

```
git clone ...
```

## 2. Installer nødvendige programmer

- Python
- Poppler
    - Linux: `sudo apt install poppler-utils`
    - Windows: http://blog.alivate.com.au/poppler-windows/
- Tesseract
    - Linux: https://github.com/tesseract-ocr/tessdoc/blob/master/Installation.md
    - Windows: https://github.com/UB-Mannheim/tesseract/wiki

## 3. Lag virtual environment (må ikke, men det er ryddig og enkelt)

Lage:
```
python -m venv venv
```

Aktivere:
```
source venv/bin/activate
```

Deaktivere:
```
deactivate
```

## 4. Installer python-pakker

Dette må gjøres når virtual environmentet er aktivert
```
pip install -r requirements.txt
```

## 5. Kjøre koden

Scriptet kjører du med (virtual environment må forstatt være aktivert)
```
python splitter.py
```

Det vil nå bli lagd noen undermapper i mappa du kjører det fra. Putt pdfene du vil analysere i mappa som heter `input_pdfs` og så kjør scriptet på nytt. Scriptet bruker noen få sekunder på hver side som skal analyseres, så det tar relativt lang tid. Når hver pdf er ferdig analysert vil de ligge ferdig splitta i `output_pdfs`.
