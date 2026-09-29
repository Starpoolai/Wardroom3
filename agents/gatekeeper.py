#!/usr/bin/env python3
"""GATEKEEPER — V6 Module 4 · Cash App/Venmo deep links + ABSOLUTE owner permission
Stage rules enforced in code: every item forced PENDING; payment links generated
ONLY for items with an owner approval file in fulfillment/approvals/.
QR payloads saved as text (PNG via `pip install qrcode` when available)."""
import json,os
from pathlib import Path
from urllib.parse import quote
Q=Path('committee/queue.json');APPR=Path('fulfillment/approvals');LINKS=Path('committee/payment_links.json')
CASHTAG=os.getenv('CASHTAG','$YourCashtag');VENMO=os.getenv('VENMO_USER','your-venmo')
def enforce_pending():
 if not Q.exists():raise SystemExit('⚠ no committee/queue.json')
 doc=json.loads(Q.read_text());fixed=0
 for it in doc['items']:
  if it.get('status')!='pending':it['status']='pending';fixed+=1   # Stage 2 restriction
  if it.get('released') and not (APPR/f"{it['id']}.json").exists():it['released']=False;fixed+=1
 Q.write_text(json.dumps(doc,indent=2));print(f'🔒 enforced PENDING on {fixed} item(s)')
def approved_ids():return {p.stem for p in APPR.glob('*.json')} if APPR.exists() else set()
def links_for(it):
 note=quote(f"Order {it['id']}")
 cash=f"https://cash.me/${CASHTAG.lstrip('$')}/{it['price']}?note={note}"
