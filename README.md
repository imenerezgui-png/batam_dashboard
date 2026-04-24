# Batam Meta Ads Dashboard

Interactive Streamlit dashboard for Facebook / Instagram (Meta Ads) campaign analytics.

## Run locally

```powershell
cd batam_dashboard
pip install -r requirements.txt
# Place mg_batam.xlsx in this folder (or upload from sidebar)
copy ..\mg_batam.xlsx .
streamlit run dashboard.py
```

The app opens at http://localhost:8501.

## Features

- **KPI cards**: Impressions, Reach, Clicks, Spend, CTR, CPC, CPM, Purchases
- **Filters**: Campaign, Age group, Objective
- **Tabs**:
  1. Reach & Impressions (by campaign / objective / age)
  2. Cost & Efficiency (CTR vs CPC bubble, spend ranking)
  3. Engagement (likes, reactions, comments, shares, video, IG followers)
  4. Audience & Funnel (age performance + conversion funnel + ROAS)
  5. Raw data (browse + CSV download)
- **File upload**: drop any new Meta Ads export (`.xlsx`) into the sidebar

## Deploy online (free) — Streamlit Community Cloud

1. Create a GitHub repo and push these files:
   ```
   batam_dashboard/
     dashboard.py
     requirements.txt
     mg_batam.xlsx          # optional; users can upload instead
   ```
2. Go to https://share.streamlit.io → **New app**
3. Pick your repo, branch, and `batam_dashboard/dashboard.py` as the main file
4. Click **Deploy** — you get a public URL like `https://your-app.streamlit.app`

> Tip: if your data is sensitive, *don't* commit `mg_batam.xlsx`. The sidebar uploader lets users provide it at runtime.

## Other free hosting options

- **Hugging Face Spaces** (Streamlit SDK) — drag & drop deploy
- **Render.com** / **Railway** — Docker or buildpack
- **Azure App Service** / **AWS App Runner** — production-grade
