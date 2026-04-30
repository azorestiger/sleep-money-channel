#!/usr/bin/env python3
"""
One-time YouTube OAuth authorization.
Run this once to generate config/token.json for automated uploads.
"""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS = Path(__file__).parent.parent / "config" / "client_secrets.json"
TOKEN_FILE     = Path(__file__).parent.parent / "config" / "token.json"

flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
creds = flow.run_local_server(port=8080, open_browser=True)

TOKEN_FILE.write_text(creds.to_json())
print(f"\nAuthorization complete! Token saved to: {TOKEN_FILE}")
print("You can now run make_video.py for automated YouTube uploads.")
