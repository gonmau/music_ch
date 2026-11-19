@echo off
chcp 65001 >nul
pip install google-auth-oauthlib >nul 2>&1
python get_token.py client_secret.json
pause
