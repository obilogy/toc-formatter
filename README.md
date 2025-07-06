# TOC Formatter Web App

A simple web application that cleans up messy table of contents in Word documents by removing arrows/dots and applying professional dot leaders.

## Features

- Upload .docx files with messy TOCs
- Automatically detects TOC entries and abbreviation definitions
- Removes messy arrows (→) and dots (...) 
- Adds professional dot leaders
- Preserves hierarchy and indentation
- Supports Roman numerals and special characters
- Download processed document

## Prerequisites

- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python 3** (v3.8 or higher) - [Download here](https://python.org/)
- **Git** (for cloning/pushing to GitHub) - [Download here](https://git-scm.com/)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/toc-formatter.git
   cd toc-formatter
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   npm run setup
   ```
   
   Or manually:
   ```bash
   cd python
   pip install -r requirements.txt
   cd ..
   ```

4. **Create required directories**
   ```bash
   mkdir uploads outputs
   ```

## Usage

1. **Start the development server**
   ```bash
   npm run dev
   ```

2. **Open your browser**
   - Go to [http://localhost:3000](http://localhost:3000)

3. **Upload and process**
   - Select a .docx file with messy table of contents
   - Click "Format TOC"
   - Download the processed document

## How It Works

The web app uses your existing Python TOC formatter as a subprocess:

1. User uploads .docx file through the web interface
2. File is temporarily stored in `/uploads` directory
3. Node.js calls the Python script as a subprocess
4. Python processes the document and saves to `/outputs`
5. User downloads the formatted document
6. Temporary files are cleaned up automatically

## File Structure

```
toc-formatter/
├── python/
│   ├── toc_formatter.py    # Your original Python script
│   └── requirements.txt    # Python dependencies
├── pages/
│   ├── api/
│   │   ├── upload.js      # File upload handler
│   │   ├── process.js     # Python subprocess caller
│   │   └── download.js    # File download handler
│   └── index.js           # Main web interface
├── uploads/               # Temporary upload storage
├── outputs/               # Temporary processed files
└── package.json           # Node.js dependencies
```

## Troubleshooting

**Python not found error:**
- Make sure Python is installed and accessible as `python3`
- On Windows, you might need to use `python` instead of `python3`

**Permission errors:**
- Make sure the `uploads` and `outputs` directories exist and are writable

**File size limits:**
- Current limit is 10MB per file
- Adjust in `pages/api/upload.js` if needed

## GitHub Setup

To push this to GitHub:

1. **Create a new repository on GitHub**

2. **Initialize and push**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/toc-formatter.git
   git push -u origin main
   ```

## License

MIT License - feel free to fork and modify!