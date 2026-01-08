# `snapcitr`

A desktop application for capturing text from screen screenshots and automatically extracting bibliographic citations to add to Zotero.

(*Caveat utor et contributor: Much (most, counting by the number of lines) of this code was written by Claude Sonnet 4.5 and Opus 4.5.*)

## Usage

(Once everything is set up, see later in this section.)

- Press `Ctrl-Left + PrintScreen` to enter the selection mode and `Escape` to exit.
- While in selection mode, press `Alt-Left` to (de)activate the selection overlay.
- With activated selection overlay, click and drag a rectangle to select a text with a citation.
- Having selected a proper citation, the text will be extracted (using Tesseract), processed to BibTeX (using OpenAI API), and imported to Zotero.
- The app is then ready for extracting the next citation.

(Script activity is being logged to `<repo-address>/logs/snapcitr.log`.)

Putting all the keyboard controls in one neat table:

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Ctrl + PrintScreen` | Launch snapshot app (when service is running) |
| Click + Drag | Select rectangle area |
| `Alt` | Toggle overlay visibility (hide to interact with windows) |
| `Escape` | Exit selection mode and close app |

## Installation & Configuration

### Prerequisites

- Python 3.10+
- Tesseract OCR installed on your system
- Zotero application with API key (in `.env`)
- OpenAI API key (in `.env`)

### System Dependencies

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install tesseract-ocr
```

**macOS:**

```bash
brew install tesseract
```

**Windows:**

Download and install Tesseract OCR from:

- Official installer: https://github.com/UB-Mannheim/tesseract/wiki
- Or via Chocolatey: `choco install tesseract`

Add Tesseract to your PATH or note the installation path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)

### Python Setup

**Linux/macOS:**

1. Clone/navigate to the repository.

2. Create virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

**Windows:**

1. Clone/navigate to the repository.

2. Create virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

3. Install Python dependencies:

```cmd
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:

```bash
cp .env.example .env
```

Edit `.env` with:

```bash
OPENAI_API_KEY=your_openai_api_key_here
ZOTERO_USER_ID=your_zotero_user_id_here
ZOTERO_API_KEY=your_zotero_api_key_here
```

### Obtaining Zotero Credentials

1. **User ID**: Go to https://www.zotero.org/mylibrary - look at the URL: `https://www.zotero.org/users/1234567/library` → your ID is `1234567`

2. **API Key**: Go to https://www.zotero.org/settings/security#applications → Create a new private key with Read/Write permissions

### Launch

#### Option 1: Global Hotkey Setup (recommended)

Recommended option. Allows auto-launch of `snapcitr` with `Ctrl + PrintScreen` from anywhere:

**Linux:**

1. Make setup script executable:

```bash
chmod +x setup_hotkey.sh
```

2. Run setup:

```bash
./setup_hotkey.sh
```

This installs a systemd user service that runs in the background.

**macOS:**

The hotkey listener should work when running manually:

```bash
python hotkey_listener.py
```

For auto-start on login, add the script to your login items or create a LaunchAgent plist file.

**Windows:**

The hotkey listener can be run manually:

```cmd
python hotkey_listener.py
```

For auto-start on login:

1. Create a shortcut to `hotkey_listener.py`
2. Press `Win + R`, type `shell:startup`, press Enter
3. Move the shortcut to the Startup folder

Or use Task Scheduler:

- Open Task Scheduler
- Create Basic Task → Name it "Snapcitr Hotkey"
- Trigger: "When I log on"
- Action: "Start a program"
- Program: `C:\path\to\your\.venv\Scripts\python.exe`
- Arguments: `C:\path\to\your\hotkey_listener.py`
- Working directory: `C:\path\to\your\snapcitr`

#### Option 2: Manual Launch (good for testing & debugging)

Run directly:

```bash
python3 main.py
```

**Windows/macOS:**

To stop the hotkey listener:

- Find the `python hotkey_listener.py` process and kill it
- Windows: Task Manager → Details tab → find `python.exe` running `hotkey_listener.py` → End task
- macOS: Activity Monitor → search for `python` → Quit process
- Or use terminal: `pkill -f hotkey_listener.py` (Linux/macOS) or `taskkill /F /IM python.exe` (Windows, kills all Python processes)

For Task Scheduler (Windows):

- Open Task Scheduler → Task Scheduler Library → find "Snapcitr Hotkey"
- Right-click → Disable (to prevent auto-start) or Delete (to remove completely)

## Logging

Application logs are located in the repo: `logs/snapcitr.log`.

### Application Logging

Logs are saved to: `logs/snapcitr.log`

View in real-time:

**Linux/macOS:**

```bash
tail -f logs/snapcitr.log
```

**Windows (PowerShell):**

```powershell
Get-Content logs\snapcitr.log -Wait -Tail 50
```

**Windows (Command Prompt):**

```cmd
type logs\snapcitr.log
```

(No built-in tail equivalent - use PowerShell or a text editor with auto-refresh)

Log levels: INFO (general flow), ERROR (failures with stack traces)

## Citation Support

Supports 14 BibTeX entry types:

- `article` - Journal article
- `book` - Published book
- `booklet` - Unpublished bound work
- `conference` / `inproceedings` - Conference paper
- `incollection` - Part of an edited book
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

## Management & Troubleshooting

### Hotkey Service

**Linux (systemd):**

Check status:

```bash
systemctl --user status snapcitr-hotkey
```

Stop (kill the service):

```bash
systemctl --user stop snapcitr-hotkey
```

Start:

```bash
systemctl --user start snapcitr-hotkey
```

Restart (after code changes):

```bash
systemctl --user restart snapcitr-hotkey
```

Disable auto-start on login:

```bash
systemctl --user disable snapcitr-hotkey
```

Re-enable auto-start:

```bash
systemctl --user enable snapcitr-hotkey
```

View real-time logs:

```bash
journalctl --user -u snapcitr-hotkey -f
```

### Hotkey not working

**Linux:**

Check if the service is running:

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

**Windows/macOS:**

Check if `hotkey_listener.py` is running:
- Task Manager (Windows) or Activity Monitor (macOS)
- Or try the hotkey - if nothing happens, the listener isn't running

To start manually:
```bash
python hotkey_listener.py
```

### "ModuleNotFoundError: No module named 'pynput'"

**Linux:**

Service is using a wrong Python. Reinstall with:

```bash
./setup_hotkey.sh
```

**Windows/macOS:**

Make sure you activated the virtual environment before running:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Then run:
```bash
python hotkey_listener.py
```

### OCR not extracting text

**Linux:**

Ensure Tesseract is installed:

```bash
which tesseract
```

If not: `sudo apt-get install tesseract-ocr`

**macOS:**

```bash
which tesseract
```

If not: `brew install tesseract`

**Windows:**

Check if Tesseract is in PATH:

```cmd
where tesseract
```

If not found, download from https://github.com/UB-Mannheim/tesseract/wiki or install via `choco install tesseract`

### Zotero import failing

- Check `ZOTERO_USER_ID` and `ZOTERO_API_KEY` in `.env`
- Verify API key has Read/Write permissions
- Check application logs: `tail -f logs/snapcitr.log`

### OpenAI API errors

- Verify `OPENAI_API_KEY` is correct and has quota
- Check logs for detailed error messages

## Contributing

Contributions welcome, e.g., extending it to other LLM APIs or other citation managers (such as Mendeley).
