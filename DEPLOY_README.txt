PUBLIC DEPLOY VERSION

Local:
- Double-click START.bat.

Render:
- Push this folder to a GitHub repository.
- Create a Render Web Service from that repository.
- Build Command: pip install -r requirements.txt
- Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
- Health Check: /health

After deployment:
https://YOUR-SERVICE.onrender.com/admin
https://YOUR-SERVICE.onrender.com/go/naver01
https://YOUR-SERVICE.onrender.com/go/instagram01
https://YOUR-SERVICE.onrender.com/go/youtube01

IMPORTANT:
SQLite is suitable for this MVP test, but durable production analytics should use a persistent database.
