<div align="center">
  <h1>File Converter</h1>
  <img width="400" height="211" alt="File Converter demo" src="https://github.com/user-attachments/assets/71f12407-6554-4dab-9e13-488d5ce78b8e" />
</div>

## About

File Converter is a Django web app that handles everyday file conversion tasks in one place:

- **CSV → XLSX** — convert spreadsheet data between formats
- **PDF → DOCX** — turn PDFs into editable Word documents
- **Voice → Text** — transcribe audio recordings
- **Images → PDF** — combine one or more images into a single PDF

## Prerequisites

- Python 3.10+
- pip

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv_name
```

### 2. Activate the virtual environment

**macOS / Linux**
```bash
source venv_name/bin/activate
```

**Windows**
```bash
venv_name\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Collect static files

```bash
python manage.py collectstatic
```

### 6. Run the development server

```bash
python manage.py runserver
```
## Note
The user interface you see in `http://127.0.0.1:8000/` is different from the one in the video. The updated frontend with Next.js will be added soon
The app will be available at `http://127.0.0.1:8000/`.
