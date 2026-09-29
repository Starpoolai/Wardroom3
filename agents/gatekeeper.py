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
d
def links_for(it):
 note=quote(f"Order {it['id']}")
 cash=f"https://cash.me/${CASHTAG.lstrip('$')}/{it['price']}?note={note}"
 venmo=f"https://venmo.com/{VENMO.lstrip('@')}?txn=pay&amount={it['price']}&note={note}"
 return {'cashapp':{'url':cash,'qr_payload':cash},'venmo':{'url':venmo,'qr_payload':venmo}}
def main():
 print('=== 🛡 GATEKEEPER ===\n 1) Enforce PENDING + build links for APPROVED items\n 2) Quit')
 c=input('> ').strip()
 if c=='2':return
 enforce_pending()
 appr=approved_ids();doc=json.loads(Q.read_text());out=[]
 for it in doc['items']:
  if it['id'] in appr:
   it['released']=True
   out.append({'id':it['id'],'title':it['title'],'price':it['price'],'rails':links_for(it),'note':f"Order {it['id']}",'status':'released'})
  else:
   it['released']=False
 Q.write_text(json.dumps(doc,indent=2))
 LINKS.parent.mkdir(parents=True,exist_ok=True);LINKS.write_text(json.dumps(out,indent=2))
 print(f'🔗 {len(out)} released item(s) → committee/payment_links.json')
 try:
  import qrcode
  for o in out:
   qrcode.make(o['rails']['cashapp']['url']).save(f"committee/{o['id']}-cashapp-qr.png")
  print('🖼 QR PNGs written (pip install qrcode)')
 except ImportError:print('ℹ qrcode not installed — QR payloads saved as text only')
if __name__=='__main__':main()
 
