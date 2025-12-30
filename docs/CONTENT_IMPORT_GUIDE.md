# Content Import Guide

This guide explains how to import educational content (Lessons from CSV and Assessments from DOCX) into the BharatGen platform.

## Command Overview

The project includes a Django management command `import_kef_content` that automates the import process.

```bash
python manage.py import_kef_content --csv <path_to_csv> --docx <path_to_docx>
```

If paths are not provided, it defaults to:
- CSV: `kefdata/CE-FR Year 1 (Bud) Sample Content - Sheet1.csv`
- DOCX: `kefdata/KEF - CE-FR Year 1 Pre Test-Post Test Paper.docx`

## CSV Format (Lessons)

The CSV file is used to generate the **Learning Path structure** and **Video Lessons**.

**Expected Columns:**
- `Name of the lesson`: Becomes the **Module** title (e.g., "Let's Get Active").
- `Modules and its title`: Becomes the **Content** title (e.g., "Module 01 Action song").
- `Link for the Content`: YouTube/Video URL.
- `Video duration`: Duration string (e.g., "3:46").

**Structure Mapping:**
- **Learning Path**: Created automatically as "CE-FR Year 1 (Bud)".
- **Modules**: Grouped by "Name of the lesson".
- **Content**: Created as `video` type within the corresponding module.

## DOCX Format (Assessments)

The DOCX file is used to generate **Practice/Assessment** sessions.

**Parsing Logic:**
- The command reads the entire DOCX text.
- It detects questions starting with "Question X:" or "Q1.".
- It extracts the full text and puts it into a `text_content` Content item.
- It extracts structured questions into the `questions` JSON field for interactive use.

**Missing Assets (Audio/Images):**
- Since the DOCX references external audio/images not embedded in the text, the importer inserts **Placeholders** (e.g., `[**MISSING AUDIO**]`) into the content text.

## Post-Import Steps: Adding Images/Audio

Since the source DOCX does not contain the actual image/audio files (only references to them), you must manually add them after import.

### Step 1: Place Files in Media Directory
Copy your image and audio files to the server's media folder. It is recommended to create a subfolder:
```bash
# Example structure
media/
  └── kef_assets/
      ├── image1.jpg
      ├── audio_clip1.mp3
      └── ...
```

### Step 2: Update Content in Admin Panel
1.  Log in to the Django Admin Panel (`/admin`).
2.  Navigate to **Learning -> Contents**.
3.  Find "Year 1 Pre-Test Paper".
4.  Edit the **Text Content** field.
5.  Replace the placeholders (e.g., `[**MISSING IMAGE...**]`) with the correct Markdown/HTML:
    -   **For Images**: `![Description](/media/kef_assets/image1.jpg)`
    -   **For Audio**: `<audio controls src="/media/kef_assets/audio_clip1.mp3"></audio>`
6.  Save the content.

### Step 3: Verify Questions
Check the "Questions" JSON field in the admin to ensure the extraction matches your expectations for the interactive quiz mode.
