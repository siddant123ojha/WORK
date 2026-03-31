# ∑ MathAI Student — Streamlit App

AI-powered math tutor for all student levels, built with Google Gemini.

## Features
- **Math Solver** — Step-by-step solutions for any problem
- **Q&A Chat** — Conversational tutoring with Gemini
- **Camera Input** — Solve problems directly from photos (Gemini Vision)
- **Image Generator** — Generate math diagrams with Gemini Imagen
- **Function Grapher** — Plot & analyze functions with Plotly

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API Key
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIza..."
```
Get your key free at: https://aistudio.google.com/app/apikey

### 3. Run the app
```bash
streamlit run math_ai_app.py
```

## Project Structure
```
├── math_ai_app.py       # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .streamlit/
│   └── secrets.toml     # Your API key (do NOT commit this)
└── README.md
```

## Deployment (Streamlit Cloud)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect your repo
4. Add GEMINI_API_KEY in Secrets settings

## Gemini Models Used
| Feature | Model |
|---|---|
| Math Solver | `gemini-1.5-flash` |
| Q&A Chat | `gemini-1.5-flash` |
| Camera/Vision | `gemini-1.5-flash` (multimodal) |
| Image Gen | `imagen-3.0-generate-002` |
