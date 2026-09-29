#!/usr/bin/env python3
"""HERMES AGENT COMMITTEE ENGINE — Wardroom3 V6 · Module 2
Reads data/extracted_data.json (Module 1) → 5-role committee via Gemini →
writes deliverables/ + committee/queue.json (ALL items PENDING_OWNER_APPROVAL).
Setup: set GEMINI_API_KEY env var.  Usage: python committee_engine.py → menu."""
import json,os,re,sys,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
API_KEY=os.getenv('GEMINI_API_KEY','');MODEL='gemini-2.0-flash'
TEL=Path('data/extracted_data.json');DELIV=Path('deliverables');QUEUE=Path('committee/queue.json')
PROHIBITED=re.compile(r'guaranteed|risk-?free|get rich|cure|diagnose|100% profit',re.I)
def gemini_json(sys_text,user_text):
 if not API_KEY:raise SystemExit('⚠ set GEMINI_API_KEY env var')
 body=json.dumps({'systemInstruction':{'parts':[{'text':sys_text}]},'contents':[{'role':'user','parts':[{'text':user_text}]}],'generationConfig':{'responseMimeType':'application/json','maxOutputTokens':1200}}).encode()
 req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',data=body,headers={'Content-Type':'application/json','x-goog-api-key':API_KEY})
 return json.loads(json.loads(urllib.request.urlopen(req,timeout=60).read())['candidates'][0]['content']['parts'][0]['text'])
def load_telemetry():
 if not TEL.exists():raise SystemExit('⚠ no data/extracted_data.json — run Module 1 first')
 return json.loads(TEL.read_text())
def summary(doc):
 items=[i for r in doc.get('runs',[]) for i in r.get('items',[])]
 return json.dumps({'sources':[r.get('source') for r in doc.get('runs',[])],'items':[{'title':i.get('title'),'author':(i.get('author') or {}).get('name'),'tags':i.get('tags'),'engagement':i.get('engagement'),'price_points':i.get('price_points')} for i in items[:25]]},indent=1)[:6000]
def analyst(doc):
 print('📊 Market Analyst scanning…')
 return gemini_json('You are the MARKET ANALYST on the HERMES committee. Identify 3 unmet consumer demands / market gaps from telemetry. JSON: {"gaps":[{"theme":"...","evidence":"...","audience":"..."}]}','TELEMETRY:\n'+summary(doc))
def fname(n):return re.sub(r'[^a-zA-Z0-9._-]','_',n)[:60]
def developer(gaps):
 print('🛠 Developer building deliverables…');out=[];DELIV.mkdir(parents=True,exist_ok=True)
 for g in gaps.get('gaps',[]):
  r=gemini_json('You are the DEVELOPER agent. Produce ONE complete, ready-to-use digital deliverable (Notion-template guide, SOP, prompt pack, or small Python tool). If Python, keep it under 80 lines and dependency-free.',f"Gap: {g['theme']}\nEvidence: {g['evidence']}\nAudience: {g['audience']}\nJSON: {{\"title\":\"...\",\"filename\":\"safe-name.md|py|txt\",\"kind\":\"guide|tool|template|prompt_pack\",\"body\":\"full content\"}}")
  p=DELIV/fname(r.get('filename','deliverable.md'));p.write_text(r.get('body',''))
  out.append({'title':r['title'],'file':str(p),'kind':r.get('kind','guide')})
 return out
def copywriter(devel,gaps):
 print('✍ Copywriter + pricing…')
 inv=json.dumps([{'title':d['title'],'kind':d['kind']} for d in devel])
 return gemini_json('You are the COPYWRITER & PRICING agent. Conversion-focused sales copy, target demographic, 3-tier USD pricing per asset. No prohibited claims (guaranteed/risk-free/get rich). JSON: {"offers":[{"title":"...","copy":"...","demographic":"...","tiers":{"basic":9,"pro":29,"suite":79}}]}','ASSETS:\n'+inv+'\nGAPS:\n'+json.dumps(gaps))
def skeptic(offers):
 print('⚖ IP Skeptic reviewing…');flagged=[]
 for o in offers.get('offers',[]):
  issues=[]
  if PROHIBITED.search(o.get('copy','')):issues.append('R_PROHIBITED_CLAIM')
  if not o.get('copy'):issues.append('R_EMPTY')
  o['flags']=issues;o['ip_review']='flagged' if issues else 'pass'
  if issues:flagged.append(o['title'])
 return offers,flagged
def music_director():
 print('🎵 Music Director — Billboard Top 100…');bb=Path('data/billboard.json')
 if not bb.exists():print('⚠ no data/billboard.json — scrape a chart page with Module 1, save as data/billboard.json, rerun.');return []
 out=[]
 for e in json.loads(bb.read_text()).get('entries',[])[:5]:
  r=gemini_json('You are the AI MUSIC DIRECTOR (Billboard specialist: Hip-Hop, R&B, Rock, Blues, Country). For this chart entry, design a 100% ROYALTY-FREE original audio-visual promo concept — no sampled or released works, no artist likeness. JSON: {"title":"...","genre":"...","concept":"...","visual":"...","caption":"...","platform":"youtube|instagram","when":"..."}','CHART ENTRY: '+json.dumps(e))
  out.append({'id':f"MUS-{int(time.time())}-{len(out)}",'title':r['title'],'kind':'music_asset','body':r['concept']+'\nVisual: '+r['visual'],'agentId':'MUSIC DIRECTOR','price':0,'platform':r.get('platform','youtube'),'em':'🎵','royaltyFree':True,'caption':r.get('caption'),'when':r.get('when'),'status':'pending'})
 return out
def build_queue(devel,offers,tracks):
 q=[]
 for o in offers.get('offers',[]):
  if o.get('ip_review')!='pass':continue
  src=next((d for d in devel if d['title']==o['title']),None)
  q.append({'id':f"DPC-{int(time.time())}-{len(q)}",'title':o['title'],'kind':src['kind'] if src else 'product','body':o['copy']+'\nDemographic: '+o.get('demographic',''),'agentId':'COPYWRITER','price':o['tiers']['basic'],'platform':'cashapp','em':'📦','status':'pending','file':src['file'] if src else None,'tiers':o.get('tiers')})
 q+=tracks;QUEUE.parent.mkdir(parents=True,exist_ok=True)
 QUEUE.write_text(json.dumps({'generated':datetime.now(timezone.utc).isoformat(),'items':q},indent=2))
 print(f'📋 {len(q)} item(s) → committee/queue.json — ALL PENDING_OWNER_APPROVAL')
 if tracks:
  Path('committee/schedule.json').write_text(json.dumps([{'title':t['title'],'platform':t['platform'],'when':t.get('when'),'status':'pending_owner'} for t in tracks],indent=2))
def main():
 print('=== 🏛 AGENT COMMITTEE ENGINE ===\n 1) Full cycle (analyze→build→copy→review→queue)\n 2) Music Director cycle\n 3) Quit')
 c=input('> ').strip()
 if c=='3':return
 doc=load_telemetry()
 if c=='1':
  gaps=analyst(doc);devel=developer(gaps);offers,flagged=skeptic(copywriter(devel,gaps))
  print('⚖ flagged (held from queue):',flagged or 'none');build_queue(devel,offers,[])
 elif c=='2':build_queue([],{'offers':[]},music_director())
 print('✅ done — approve items in Wardroom3 SUITE ▸ APPROVE')
if __name__=='__main__':main()
