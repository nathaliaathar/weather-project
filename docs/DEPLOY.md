# Deploy — how to run and publish

This file is **not** Python. It is the checklist for running the app on your computer and later putting it on the internet (Streamlit Community Cloud).

Do this **after** the notebook forecast request works and `app.py` can show a Photography Score. You do not need Cloud on day one.

## Local (your computer)

```bash
cd weather-project
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env          # then paste the real key
copy .streamlit\secrets.toml.example .streamlit\secrets.toml

streamlit run app.py
```

`requirements.txt` lists the libraries pip must install.  
`.env` holds your API key as an environment variable (a secret name=value pair).

## GitHub

1. Create a **new** GitHub repository just for this project (do not push the whole Python Projects folder unless the instructor asked for that).
2. Confirm `.gitignore` excludes `.env` and `.streamlit/secrets.toml`.
3. Never paste the API key in README, notebooks that you commit, or chat screenshots you will submit.

```bash
git init
git add .
git status    # inspect: no secrets
git commit -m "Initial Shoot Window project structure"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. New app → pick this repo → main → `app.py`.
3. In **Advanced settings → Secrets**, paste:

```toml
OPENWEATHER_API_KEY = "the-real-key"
```

4. Deploy. Open the public URL. Plan a shoot in Tel Aviv. Trigger an error (fake city, if you add that input) and confirm the message.

If the Cloud build fails, the usual causes are: missing `requirements.txt`, wrong entry-file path, or the secret name not matching the code (`OPENWEATHER_API_KEY`).

Official secrets guide: https://docs.streamlit.io/develop/concepts/connections/secrets-management
