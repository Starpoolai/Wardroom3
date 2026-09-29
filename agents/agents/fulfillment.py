#!/usr/bin/env python3
"""FULFILLMENT BRIDGE — V6 Module 5 · sandbox test · packaging · payment listener · DMCA filter
Flow: owner approvals → sandbox-test deliverables → package .zip → owner records
confirmed payments in fulfillment/payment_refs.json → listener matches
reference + amount → writes dispatch file containing the buyer's download link.
(Note: Cash App/Venmo expose no public transaction webhooks, so verification is
reference-matching — you record confirmed transaction refs, the bridge validates
orderId + amount before dispatch. No funds move autonomously.)"""
import json,re,subprocess,tempfile,zipfile
from pathlib import Path
APPR=Path('fulfillment/approvals');DELIV=Path('deliverables')
ORDERS=Path('fulfillment/orders');DISP=Path('fulfillment/dispatch');PKGS=Path('fulfillment/packages')
REFS=Path('fulfillment/payment_refs.json')
DMCA=re.compile(r'\b(beat\s?by|type\s?beat|sampled from|feat\.?\s+[A-Z][a-z]+)\b')
def sandbox(p):
 p=Path(p)
 if not p.exists():return False,'file missing'
 if p.suffix=='.py':
  try:
   import py_compile;py_compile.compile(str(p),cfile=tempfile.mktemp());return True,'py ok'
  except Exception as e:return False,str(e)[:140]
 if p.suffix=='.js':
  try:
   subprocess.run(['node','--check',str(p)],check=True,capture_output=True);return True,'js ok'
  except Exception as e:return False,str(e)[:140]
 return (len(p.read_text().strip())>50),'text ok'
def package(item_id):
 appr=APPR/f'{item_id}.json'
 if not appr.exists():return None,'E_NO_APPROVAL: no owner approval file'
 it=json.loads(appr.read_text())
 files=[]
 if it.get('file'):
  p=Path(it['file'])
  if p.exists():files.append(p)
 if not files:
  for ext in ('.md','.txt'):
   p=DELIV/f"{item_id}{ext}"
   if p.exists():files.append(p)
 if not files:return None,'E_NO_ASSET: no deliverable file found'
 for f in files:
  ok,msg=sandbox(f)
  if not ok:return None,f'E_SANDBOX_FAIL {f.name}: {msg}'
 if it.get('kind')=='music_asset':
  if not it.get('royaltyFree'):return None,'E_DMCA_BLOCK: royaltyFree flag missing'
  if DMCA.search(json.dumps(it)):return None,'E_DMCA_BLOCK: possible copyrighted reference'
 PKGS.mkdir(parents=True,exist_ok=True)
 zp=PKGS/f'{item_id}.zip'
 with zipfile.ZipFile(zp,'w') as z:
  for f in files:z.write(f,f.name)
  z.writestr('ORDER.txt',f"Order {item_id}\nTitle: {it.get('title')}\nPrice: ${it.get('price')}\nRoyalty-free: {it.get('royaltyFree',False)}\n")
 ORDERS.mkdir(parents=True,exist_ok=True)
 order={'id':item_id,'title':it.get('title'),'price':it.get('price'),'status':'awaiting_payment','package':str(zp),'references':[]}
 (ORDERS/f'{item_id}.json').write_text(json.dumps(order,indent=2))
 return order,'packaged'
def listen():
 if not REFS.exists():raise SystemExit('⚠ create fulfillment/payment_refs.json — format: [{"ref":"txn123","orderId":"DPC-...","amount":9,"rail":"cashapp"}]')
 DISP.mkdir(parents=True,exist_ok=True);matched=0
 for r in json.loads(REFS.read_text()):
  o=ORDERS/f"{r.get('orderId')}.json"
  if not o.exists():print(f"⚠ unknown order {r.get('orderId')}");continue
  order=json.loads(o.read_text())
  if order['status']=='dispatched':continue
  if abs(float(order['price'])-float(r.get('amount',0)))>0.01:
   print(f"⚠ amount mismatch {r.get('orderId')}");continue
  order['status']='dispatched'
  order['references'].append({'ref':r.get('ref'),'rail':r.get('rail'),'amount':r.get('amount')})
  o.write_text(json.dumps(order,indent=2))
  d={'orderId':order['id'],'buyer_ref':r.get('ref'),'download':order['package'],'note':'deliver download link to buyer'}
  (DISP/f"{order['id']}.json").write_text(json.dumps(d,indent=2))
  matched+=1;print(f"✅ dispatched {order['id']} (ref {r.get('ref')})")
 print(f'📦 {matched} order(s) dispatched')
def main():
 print('=== 🚚 FULFILLMENT BRIDGE ===\n 1) Package APPROVED items (sandbox-tested)\n 2) Payment listener → dispatch\n 3) Quit')
 c=input('> ').strip()
 if c=='3':return
 if c=='1':
  if not APPR.exists():print('⚠ no approvals yet — approve in Wardroom3 SUITE ▸ APPROVE');return
  for p in APPR.glob('*.json'):
   r,msg=package(p.stem);print(('✅' if r else '⛔'),p.stem,'—',msg)
 elif c=='2':listen()
if __name__=='__main__':main()
