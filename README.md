
EVU can now route the same chat request to different providers:

- OpenAI
- Claude / Anthropic
- Google Gemini
- Grok / xAI
- GLM / Z.AI

The frontend asks the backend which providers are configured. A provider becomes available when its API key exists in `backend/.env`.

## Important

You do **not** need keys for every provider. Start with one working key, then add others later.

## Setup

### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

Swagger:

`http://127.0.0.1:8000/docs`

Provider list endpoint:

`http://127.0.0.1:8000/api/v1/providers`

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

## API keys

Edit `backend/.env`. Keep only keys you actually own.

```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
XAI_API_KEY=
ZAI_API_KEY=
```

Restart the backend after every `.env` change.

## Manual Step 5 integration

The separate Step 5 package contains only the files you need to add or replace. Do not delete your whole project and do not copy an entire `app` folder over your existing project.
