# Snapcitr

A desktop application for capturing text from screen screenshots and automatically extracting bibliographic citations to add to Zotero.

## Features

- **Global hotkey activation**: Press `Ctrl+PrintScreen` from anywhere to launch
- **Interactive rectangle selection**: Click and drag to select text area on screen
- **Alt toggle overlay**: Press `Alt` to hide/show the selection overlay while preparing
- **OCR text extraction**: Uses Tesseract to extract text from selected area
- **AI citation parsing**: Uses OpenAI API to intelligently identify bibliographic information
- **Automatic Zotero import**: Adds extracted citations directly to your Zotero library
- **Comprehensive logging**: All operations logged to `logs/snapcitr.log`
- **Flexible exit**: Press `Escape` anytime to exit selection mode

## Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR installed on your system
- Zotero application with API key
- OpenAI API key

### System Dependencies

**Ubuntu/Debian:**

```bash
sudo apt-get install tesseract-ocr
```

**macOS:**

```bash
brew install tesseract
```

### Python Setup

1. Clone/navigate to the repository:

```bash
cd /home/matthewbaggins/code/snapcitr
```

2. Create virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:

```bash
cp .env.example .env
```

Edit `.env` with:

```
OPENAI_API_KEY=your_openai_api_key_here
ZOTERO_USER_ID=your_zotero_user_id_here
ZOTERO_API_KEY=your_zotero_api_key_here
```

### Get Your Zotero Credentials

1. **User ID**: Go to https://www.zotero.org/mylibrary - look at the URL: `https://www.zotero.org/users/1234567/library` → your ID is `1234567`

2. **API Key**: Go to https://www.zotero.org/settings/security#applications → Create a new private key with Read/Write permissions

## Usage

### Manual Launch

Run directly:

```bash
python3 main.py
```

### Global Hotkey Setup

Auto-launch with `Ctrl+PrintScreen` from anywhere:

1. Make setup script executable:

```bash
chmod +x setup_hotkey.sh
```

2. Run setup:

```bash
./setup_hotkey.sh
```

This installs a systemd user service that runs in the background.

### Citation Extraction Workflow

1. Press **Ctrl+PrintScreen** to launch the app
2. The selection overlay appears
3. **Click and drag** to select the citation text on screen
4. Text is extracted and sent to OpenAI for parsing
5. Citation is automatically added to Zotero
6. App is ready for next citation (or press **Escape** to exit)

### Keyboard Controls

| Key | Action |
|-----|--------|
| **Ctrl+PrintScreen** | Launch snapshot app (when service is running) |
| **Click + Drag** | Select rectangle area |
| **Alt** | Toggle overlay visibility (hide to interact with windows) |
| **Escape** | Exit selection mode and close app |

## Configuration

### Hotkey Service Management

Status:

```bash
systemctl --user status snapcitr-hotkey
```

Stop:

```bash
systemctl --user stop snapcitr-hotkey
```

Start:

```bash
systemctl --user start snapcitr-hotkey
```

Restart:

```bash
systemctl --user restart snapcitr-hotkey
```

Logs:

```bash
journalctl --user -u snapcitr-hotkey -f
```

### Application Logging

Logs are saved to: `logs/snapcitr.log`

View in real-time:

```bash
tail -f logs/snapcitr.log
```

Log levels: INFO (general flow), ERROR (failures with stack traces)

## Citation Support

Supports 14 BibTeX entry types:

- `article` - Journal article
- `book` - Published book
- `booklet` - Unpublished bound work
- `conference` / `inproceedings` - Conference paper
- `incollection` - Part of edited book
- `inbook` - Chapter in book
- `manual` - Technical documentation
- `mastersthesis` / `phdthesis` - Academic thesis
- `misc` - Miscellaneous
- `proceedings` - Conference proceedings
- `techreport` - Technical report
- `unpublished` - Unpublished document

### Supported Citation Fields

**Required per type** (validated): author, title, year, publication context, etc.

**Optional**: journal, booktitle, publisher, volume, issue, pages, DOI, URL, ISBN, ISSN, edition, series, address, abstract, keywords, and more.

All available fields are extracted and mapped to Zotero's item types.

## Architecture

```
main.py                          # Entry point, main loop, logging
├── rectangle_selector.py        # Screenshot selection UI
├── processing.py                # OCR & citation extraction
├── bibtex.py                    # Citation data model & validation
├── import_to_zotero.py          # Zotero API integration
├── utils.py                     # Logging utilities
└── hotkey_listener.py           # Global hotkey daemon
```

## Troubleshooting

### Hotkey not working

Check if service is running:

```bash
systemctl --user status snapcitr-hotkey
```

View service logs:

```bash
journalctl --user -u snapcitr-hotkey -n 50
```

Restart service:

```bash
systemctl --user restart snapcitr-hotkey
```

### "ModuleNotFoundError: No module named 'pynput'"

Service is using wrong Python. Reinstall with:

```bash
./setup_hotkey.sh
```

### OCR not extracting text

Ensure Tesseract is installed:

```bash
which tesseract
```

If not: `sudo apt-get install tesseract-ocr`

### Zotero import failing

- Check `ZOTERO_USER_ID` and `ZOTERO_API_KEY` in `.env`
- Verify API key has Read/Write permissions
- Check application logs: `tail -f logs/snapcitr.log`

### OpenAI API errors

- Verify `OPENAI_API_KEY` is correct and has quota
- Check logs for detailed error messages

## Logs Location

Application logs: `logs/snapcitr.log` (in repo)

Hotkey service logs: `journalctl --user -u snapcitr-hotkey -f`

## Dependencies

See `requirements.txt` for Python packages:

- `pynput` - Global keyboard/mouse listener
- `pyzotero` - Zotero API client
- `openai` - OpenAI API client
- `pillow` - Image processing
- `pytesseract` - OCR wrapper
- `pydantic` - Citation data validation
- `python-dotenv` - Environment variable loading

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
