# 🎙️ TaskScribe

> Turn Hindi and Hinglish voice notes into clear summaries, tasks, deadlines, and next steps — privately on your own laptop.

TaskScribe is a local AI-powered voice-note assistant built for people who receive important Hindi or Hinglish voice notes and do not want action items to get lost in chats.

The app records or uploads a voice note, transcribes it locally, lets the user review and correct the transcript, and then uses a local Gemma model to create a summary, tasks, deadlines, and a next step.

---

## ✨ Features

- Record voice notes directly in the browser
- Upload MP3, WAV, M4A, MP4, OGG, and OPUS files
- Support Hindi and Hinglish voice notes
- Local speech-to-text with faster-whisper
- Editable transcript for better reliability
- Roman Hinglish summaries and task lists
- Deadline and priority extraction
- Download results as a text file
- No paid AI API key required
- Privacy-first local processing

---

## 🧠 How It Works

```text
Record or upload a voice note
            ↓
faster-whisper transcribes audio locally
            ↓
User reviews and corrects the transcript
            ↓
Gemma 3 through Ollama extracts tasks and deadlines
            ↓
TaskScribe shows a summary, action items, and next step
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Frontend web application |
| faster-whisper | Local audio transcription |
| Gemma 3 1B | Local open-weight language model |
| Ollama | Runs Gemma locally |
| PyAV | Audio decoding support |

---

## 🔓 Why Local AI?

TaskScribe processes personal Hindi/Hinglish voice notes.

Using local AI makes it possible to:

- Keep voice notes and transcripts on the user's own laptop
- Avoid paid cloud AI APIs
- Avoid per-request API costs
- Use the app after models are downloaded
- Swap or upgrade models later
- Give the user control over transcript corrections

The app uses faster-whisper for local speech-to-text and Gemma 3 through Ollama for local task extraction.

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone [https://github.com/YOUR-GITHUB-USERNAME/TaskScribe.git](https://github.com/YOUR-GITHUB-USERNAME/TaskScribe.git)
```

```bash
cd TaskScribe
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

For Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

For PowerShell on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Install Ollama

Download Ollama from [ollama.com/download](https://ollama.com/download).

### 6. Download Gemma

```bash
ollama pull gemma3:1b
```

### 7. Run TaskScribe

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

## 🎙️ How to Use

1. Record a voice note or upload an audio file.
2. Click **Transcribe Voice Note**.
3. Review and correct the transcript if needed.
4. Click **Generate Tasks from Corrected Transcript**.
5. View the summary, action items, priorities, and deadlines.
6. Download the result as a text file.

---

## ⚠️ Limitations

TaskScribe works best with short, clearly spoken voice notes.

Hindi/Hinglish transcription can sometimes incorrectly recognise mixed-language words, names, dates, or English terms. To address this, TaskScribe allows users to review and correct the transcript before generating tasks.

---

## 🏆 Hackathon Submission

This project was built for the Hacktoberfest Weekend Challenge: **Build for a Friend**.

TaskScribe was created for a friend who receives internship, college, project, and career updates through Hindi/Hinglish voice notes. Important tasks often get lost in chats, so TaskScribe converts them into clear action items.

### Prize Category

- Best Use of Gemma

---

## 👩‍💻 Built By

Gunjan Mirchandani

Built with Python, Streamlit, faster-whisper, Gemma 3, and Ollama.