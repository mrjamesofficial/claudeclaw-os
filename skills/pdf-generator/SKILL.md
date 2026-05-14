---
name: pdf-generator
description: Generate a branded Toys For Trucks® PDF document and send it as a Telegram file attachment. Compatible with desktop (Windows, Mac) and mobile (iPhone, Android).
user_invocable: false
global: true
---

# PDF Generator Skill

Use this skill any time an agent needs to produce a document, flyer, report, summary, or formatted output as a PDF. The output is a branded Toys For Trucks® PDF — logo placeholder, bold title, structured sections, tagline footer — sent directly to Telegram as a downloadable file attachment.

## When to invoke

- James asks for a document, report, flyer, summary, or any formatted output
- Any agent needs to deliver structured information as a file rather than a message
- Content is too long or complex for a Telegram message
- Output will be shared, printed, or saved

## Script location

```
/home/adminjames/claudeclaw/skills/pdf-generator/generate_pdf.py
```

Python 3 + reportlab required. reportlab is installed at `~/.local/lib/python3.14/`.

## Usage

### Basic call

```bash
python3 /home/adminjames/claudeclaw/skills/pdf-generator/generate_pdf.py \
  --title "Document Title" \
  --subtitle "Optional subtitle" \
  --output "/tmp/my-document.pdf" \
  --sections '[
    {"heading": "Section One", "items": ["Point one", "Point two", "Point three"]},
    {"heading": "Section Two", "text": "Paragraph text goes here. Can be multi-line."},
    {"heading": "Section Three", "items": ["Bullet A", "Bullet B"]}
  ]'
```

### Plain text (no sections)

```bash
python3 /home/adminjames/claudeclaw/skills/pdf-generator/generate_pdf.py \
  --title "Document Title" \
  --output "/tmp/my-document.pdf" \
  --text "Full plain text content here. Line breaks become paragraphs."
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--title` | Yes | Bold document title at top |
| `--output` | Yes | Absolute path for the output PDF |
| `--subtitle` | No | Smaller subtitle below title |
| `--meta` | No | Meta line override (default: brand name + date) |
| `--sections` | No* | JSON array of sections (see format below) |
| `--text` | No* | Plain text content (use if no sections) |

*One of `--sections` or `--text` is required.

### Sections JSON format

```json
[
  {
    "heading": "Section heading (bold orange)",
    "items": ["Bullet point one", "Bullet point two"]
  },
  {
    "heading": "Paragraph section",
    "text": "Multi-line paragraph text.\nSecond line here."
  },
  {
    "heading": "Mixed section",
    "text": "Intro paragraph.",
    "items": ["Then bullets", "Like this"]
  }
]
```

## Sending the PDF via Telegram

After generating, include a `[SEND_FILE:]` marker in your response. The bot will attach the file to the Telegram message automatically.

```
[SEND_FILE:/tmp/my-document.pdf|Optional caption here]
```

## Full example

```bash
python3 /home/adminjames/claudeclaw/skills/pdf-generator/generate_pdf.py \
  --title "TFT® Off-Road — Trail Season Report" \
  --subtitle "Stoddard Valley & Johnson Valley — Spring 2026" \
  --output "/tmp/trail-report.pdf" \
  --sections '[
    {"heading": "Trails Covered", "items": ["Stoddard Valley OHV", "Johnson Valley OHV", "Big Bear National Forest"]},
    {"heading": "Crew Notes", "text": "Full send on every run. No recovery needed. Rigs performed."},
    {"heading": "Next Run", "items": ["Date: TBD", "Location: Stoddard Valley", "Meet time: 0700"]}
  ]'
```

Then in the response:
```
Here's the trail report.
[SEND_FILE:/tmp/trail-report.pdf|TFT® Off-Road Trail Report]
```

## Brand output

Every PDF includes:
- TFT® logo block (black, top left)
- Bold document title + subtitle
- Orange accent rule below header
- Brand + date meta line
- Sections with orange headings and bullet points
- Footer rule with tagline: **We Are LifeStyle Driven**
- Footer line: Toys For Trucks® | www.toysfortrucksofficial.com | @toysfortrucksofficial | 855-TFT-LIFT
