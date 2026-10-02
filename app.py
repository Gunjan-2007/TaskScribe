import os
import tempfile

import streamlit as st
from faster_whisper import WhisperModel
from ollama import chat


st.set_page_config(
    page_title="TaskScribe",
    page_icon="🎙️",
    layout="centered"
)
if "result" not in st.session_state:
    st.session_state.result = None

if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "raw_transcript" not in st.session_state:
    st.session_state.raw_transcript = None

if "edited_transcript" not in st.session_state:
    st.session_state.edited_transcript = None

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #07111f 0%, #102a43 50%, #0f172a 100%);
            color: #f8fafc;
        }

        .block-container {
            max-width: 850px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        h1 {
            font-size: 3.3rem !important;
            font-weight: 800 !important;
            margin-bottom: 0.2rem !important;
        }

        h2, h3 {
            color: #e2e8f0 !important;
        }

        .hero-text {
            color: #cbd5e1;
            font-size: 1.15rem;
            margin-bottom: 1.2rem;
        }

        .privacy-box {
            background: rgba(34, 197, 94, 0.12);
            border: 1px solid rgba(34, 197, 94, 0.35);
            border-radius: 14px;
            padding: 16px 18px;
            color: #dcfce7;
            margin: 1rem 0 1.5rem 0;
        }

        .step-card {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            min-height: 110px;
        }

        .result-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(96, 165, 250, 0.40);
            border-radius: 16px;
            padding: 20px;
            margin-top: 16px;
        }

        .footer {
            color: #94a3b8;
            text-align: center;
            padding-top: 2rem;
            font-size: 0.9rem;
        }

        .stButton > button {
            width: 100%;
            border: none;
            border-radius: 10px;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 700;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            color: white;
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #1d4ed8, #6d28d9);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_resource
def load_whisper_model():
    return WhisperModel(
        "small",
        device="cpu",
        compute_type="int8"
    )


def transcribe_audio(uploaded_file):
    file_extension = os.path.splitext(uploaded_file.name)[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file_extension
    ) as temporary_file:
        temporary_file.write(uploaded_file.getbuffer())
        temporary_audio_path = temporary_file.name

    try:
        whisper_model = load_whisper_model()

        segments, info = whisper_model.transcribe(
            temporary_audio_path,
             beam_size=5,
            language="hi",
            vad_filter=True,
        initial_prompt="This is a Hindi and Hinglish voice note. Preserve English words, names, task names, dates, and deadlines exactly as spoken."
        )

        transcript = " ".join(segment.text for segment in segments)
        return transcript

    finally:
        if os.path.exists(temporary_audio_path):
            os.remove(temporary_audio_path)
def clean_hinglish_transcript(transcript):
    prompt = f"""
You are helping clean a speech-to-text transcript from a Hindi/Hinglish voice note.

The transcript may contain Hindi written in Devanagari script and phonetically incorrect spellings of English words.

Your job is to rewrite the transcript in clear Roman Hinglish.

Examples:
- "अंटर्षिप प्रम समिट" may mean "internship form submit"
- "रेज्यूमे" means "resume"
- "तास्क्रिः प्रुज्यक्त" may mean "TaskScribe project"
- "मोग अंटर्व्य" may mean "mock interview"
- "प्रप्रेष्यन" may mean "preparation"

Rules:
- Return only the corrected Roman Hinglish transcript.
- Do not add tasks, summaries, deadlines, or explanations.
- Preserve the intended meaning.
- Correct obvious phonetic errors.
- Do not invent new details.
- Keep dates and deadlines exactly as spoken.

Raw transcript:
{transcript}
"""

    response = chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content

def create_summary_and_tasks(transcript):
    prompt = f"""
You are TaskScribe, a privacy-first assistant that converts Hindi and Hinglish voice notes into useful tasks.

Read the transcript carefully.

Transcript:
{transcript}

Return the answer in simple Roman Hinglish with exactly these headings.

IMPORTANT LANGUAGE RULES:
- Write all output only in English/Roman alphabet.
- Do not use Devanagari or Hindi script.
- Use simple Roman Hinglish.
- Example: Write "Kal tak internship form submit karna hai."
- Do not write: "कल तक इंटर्नशिप फॉर्म सबमिट करना है।"
- Keep English words such as internship, resume, TaskScribe, mock interview, deadline, and priority in English.

SUMMARY
Write a short summary in 1 or 2 lines.

ACTION ITEMS
Write every clearly mentioned task as a numbered list.

For every task, use exactly this format:

Task: [task name]
Deadline: [deadline written directly with the task, such as Aaj, Kal, Kal tak, Saturday, Monday, or Not mentioned]
Priority: [High, Medium, or Low]

Deadline mapping rules:
- If the transcript says "Kal tak internship form submit karna hai", write Deadline: Kal tak.
- If the transcript says "Aaj resume mein TaskScribe project add karna hai", write Deadline: Aaj.
- If the transcript says "Saturday ko mock interview ki preparation karni hai", write Deadline: Saturday.
- Only write "Not mentioned" if there is truly no date, day, or time word connected to that task.

IMPORTANT POINTS
Write useful details that are clearly mentioned but are not tasks.

NEXT STEP
Give one simple immediate action based only on the transcript.

STRICT RULES:
- Never invent deadlines, dates, time periods, names, tasks, or facts.
- Do not write "tomorrow", "2 days", "1 day", "next week", or any date unless the speaker explicitly said it.
- If no deadline is mentioned, write exactly: "Not mentioned".
- Do not suggest searching online, using Google, or visiting any website unless the speaker explicitly asked for it.
- If the transcript is unclear, say: "Not clearly mentioned in the voice note".
- Use concise and friendly Hinglish.
- Use the exact names of tasks from the transcript whenever possible.
- Do not change "internship" into another word.
- Do not change "resume" into another word.
- Do not change "mock interview" into another word.
- If a transcript phrase looks unclear or incorrect, do not invent a new meaning.
- Do not mention any project, summit, vlog, transcription project, or topic unless it appears clearly in the transcript.
- All summaries, task names, important points, and next steps must be written only in Roman Hinglish.
- Never copy Devanagari text from the transcript into the final output.
- Correctly connect deadline words that appear before a task with that task.
- "Aaj" means Today, "Kal" means Tomorrow, and "Kal tak" means By tomorrow.
- Do not ignore deadline words when they are clearly present in the corrected transcript.
"""

    response = chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content


st.markdown("# 🎙️ TaskScribe")
st.markdown(
    '<p class="hero-text">Turn Hindi and Hinglish voice notes into clear summaries, tasks, and next steps.</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="privacy-box">
        🔒 <b>Private by design:</b> Your audio is transcribed and analysed locally on your laptop.
        No voice note is sent to a paid cloud AI API.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="step-card">
            <h3>1. Speak</h3>
            <p>Record or upload a voice note.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="step-card">
            <h3>2. Understand</h3>
            <p>Local AI transcribes and analyses it.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="step-card">
            <h3>3. Act</h3>
            <p>Get clear tasks and next steps.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

record_tab, upload_tab = st.tabs(["🎤 Record now", "📁 Upload voice note"])

audio_to_process = None

with record_tab:
    recorded_audio = st.audio_input(
        "Tap below and record your voice note",
        sample_rate=16000
    )

    if recorded_audio is not None:
        audio_to_process = recorded_audio
        st.success("Recording ready!")

with upload_tab:
    uploaded_audio = st.file_uploader(
        "Upload a voice note from your device",
        type=["mp3", "wav", "m4a", "mp4", "ogg", "opus"]
    )

    if uploaded_audio is not None:
        audio_to_process = uploaded_audio
        st.success("Voice note uploaded successfully!")

if audio_to_process is not None:
    st.audio(audio_to_process)

    st.write("")

    if st.button("🎙️ Transcribe Voice Note"):
        try:
            with st.spinner("TaskScribe is transcribing your voice note locally..."):
                raw_transcript = transcribe_audio(audio_to_process)

                st.session_state.raw_transcript = raw_transcript
                st.session_state.transcript = raw_transcript
                st.session_state.edited_transcript = raw_transcript
                st.session_state.result = None

            st.success("Transcript is ready. Please review it before generating tasks.")

        except Exception as error:
            st.error("Something went wrong while transcribing the audio.")
            st.code(str(error))

else:
    st.caption("🎤 Record a voice note or upload an audio file to get started.")


if st.session_state.edited_transcript is not None and st.session_state.result is None:
    st.divider()
    st.subheader("📝 Review and Correct Transcript")

    st.info(
        "Hindi/Hinglish voice notes can sometimes have spelling mistakes. "
        "Please correct any important words, names, dates, or deadlines before generating tasks."
    )

    edited_transcript = st.text_area(
        "Edit the transcript if needed",
        value=st.session_state.edited_transcript,
        height=220
    )

    if st.button("✨ Generate Tasks from Corrected Transcript"):
        try:
            with st.spinner("TaskScribe is creating your summary and tasks..."):
                result = create_summary_and_tasks(edited_transcript)

                st.session_state.transcript = edited_transcript
                st.session_state.edited_transcript = edited_transcript
                st.session_state.result = result

            st.success("Your summary and tasks are ready!")
            st.rerun()

        except Exception as error:
            st.error("Something went wrong while creating tasks.")
            st.code(str(error))


if st.session_state.result is not None:
    st.divider()

    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    st.subheader("📌 Summary, Tasks & Next Step")
    st.markdown(st.session_state.result)

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📝 View corrected transcript"):
        st.write(st.session_state.transcript)

    with st.expander("🔍 View original speech-to-text transcript"):
        st.write(st.session_state.raw_transcript)

    download_content = f"""TASKSCRIBE RESULT

SUMMARY, TASKS & NEXT STEP

{st.session_state.result}


CORRECTED TRANSCRIPT

{st.session_state.transcript}


ORIGINAL SPEECH-TO-TEXT TRANSCRIPT

{st.session_state.raw_transcript}
"""

    st.download_button(
        label="⬇️ Download Summary, Tasks & Transcript",
        data=download_content.encode("utf-8"),
        file_name="taskscribe-result.txt",
        mime="text/plain"
    )

    st.write("")

    if st.button("🗑️ Start New Voice Note"):
        st.session_state.result = None
        st.session_state.transcript = None
        st.session_state.raw_transcript = None
        st.session_state.edited_transcript = None
        st.rerun()


st.markdown(
    """
    <div class="footer">
        Built locally with faster-whisper, Gemma 3, Ollama, and Streamlit.<br>
        Your voice. Your device. Your data.
    </div>
    """,
    unsafe_allow_html=True
)