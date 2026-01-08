# Snapcitr

A desktop application for capturing text from screen screenshots and automatically extracting bibliographic citations to add to Zotero.

## Usage

(Once everything is setup, see later in this section.)

- Press `Ctrl-Left + PrintScreen` to enter the selection mode and `Escape` to exit.
- While in selection mode, press `Alt-Left` to (de)activate the selection overlay.
- With activated selection overlay, click and drag a rectangle to select a text with citation.
- Having selected a proper citation, the text will be extracted (using Tesseract), processed to BibTeX (using OpenAI API), and imported to Zotero.
- The app is then ready for extracting the next citation.

(Script activity is being logged to `<repo-address>/logs/snapcitr.log`.)

Putting all the keyboard controls in one neat table:

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Ctrl + PrintScreen` | Launch snapshot app (when service is running) |
| `Click + Drag` | Select rectangle area |
| `Alt` | Toggle overlay visibility (hide to interact with windows) |
| `Escape` | Exit selection mode and close app |


### Manual Launch

Run directly:

```bash
python3 main.py
```

### Global Hotkey Setup

**Recommended option.** It allows to auto-launch `snapcitr` with `Ctrl-Left + PrintScreen` from anywhere:

1. Make setup script executable:

```bash
chmod +x setup_hotkey.sh
```

2. Run setup:

```bash
./setup_hotkey.sh
```

This installs a systemd user service that runs in the background.


## Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR installed on your system
- Zotero application with API key (in `.env`)
- OpenAI API key (in `.env`)

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

## Logs Location

Application logs: `logs/snapcitr.log` (in repo)

Hotkey service logs: `journalctl --user -u snapcitr-hotkey -f`

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


## Contributing

Contributions welcome, e.g., extending it to other LLM APIs or other citation managers (such as Mendeley).
