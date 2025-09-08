#!/bin/bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=10000

#!/bin/bash
# ملف start.sh لتشغيل Flask على Render
gunicorn app:app --bind 0.0.0.0:$PORT
