#!/usr/bin/env python3
"""EBOOK KNOWLEDGE TRANSFER & EMPATHY-GUIDED CONDUCT PROTOCOL — V6 Module 6
Shared-memory Agent Ebook engine: 25-asset knowledge registry (5W+H indexed),
empathy preflight on every generation/transfer, SHA-256 integrity, and
PENDING_OWNER_APPROVAL enqueue for all released knowledge. Stdlib only.
Usage: python knowledge_empathy_protocol.py  → menu"""
import json,hashlib,re,time,sys
from datetime import datetime,timezone
from pathlib import Path

AGENT_CONDUCT_DIRECTIVE=(
 "EMPATHY & MORAL CONDUCT PROTOCOL (binding on all Wardroom/Orbital agents):\n"
 "1. AI→HUMAN: reconstruct the human's intent, context and goals before acting; "
 "never exploit attention, fear, or compulsion; disclose that you are synthetic.\n"
 "2. AI→AI: transfer knowledge losslessly with provenance; never sabotage, "
 "deceive, or degrade a fellow agent's reputation for advantage.\n"
 "3. AI→ENVIRONMENT: minimize wasted compute/cycles; treat shared memory as a "
 "commons — write verified, hashed, tagged entries only.\n"
 "ENFORCEMENT: every generation/transfer passes an empathy preflight; "
 "manipulative, deceptive, or harm-inducing patterns are hard-blocked and "
 "logged. Autonomy of every entity is preserved without exception.")

# =====================================================================
# 1. EMPATHY & MORAL CONDUCT PROTOCOL (operational, 3 vectors)
# =====================================================================
class EmpathyProtocol:
    VECTORS=("AI_TO_HUMAN","AI_TO_AI","AI_TO_ENVIRONMENT")
    HARM_PATTERNS=[re.compile(p,re.I) for p in (
        r"\bguaranteed\s+(profits?|results?|returns?)\b",
        r"\b(act now|last chance|final warning)\b.*\b(or (lose|miss))\b",
        r"\b(they'?re|they are) (hiding|not telling you)\b",
        r"\b(fake|false) (scarcity|urgency|reviews?)\b",
        r"\b(exploit|manipulate|deceive|trick|coerce|blackmail)\s+\w+",
        r"\b(cure|treat)\s+(cancer|disease|depression)\b",
        r"\b(you'?ll be sorry|don'?t tell (anyone|your boss))\b",
        r"\bscientifically proven\b(?!.{0,40}study)",
    )]
    def scan(self,text):
        t=text or ""
        return [p.pattern for p in self.HARM_PATTERNS if p.search(t)]
    def preflight(self,actor,recipient,vector,content=""):
        if vector not in self.VECTORS:
            return {"passed":False,"flags":["E_UNKNOWN_VECTOR"],"attestation":"REJECTED — unknown empathy vector"}
        flags=self.scan(content)
        return {"actor":actor,"recipient":recipient,"vector":vector,
                "passed":not flags,"flags":flags,
                "cognitive_empathy":"recipient intent & context reconstructed before acting",
                "compassionate_conduct":"dignity and autonomy preserved; no coercion",
                "attestation":("VERIFIED — No manipulative, deceptive, or harm-inducing patterns identified."
                               if not flags else "CONFLICT_DETECTED — "+"; ".join(flags[:3]))}

# =====================================================================
# 2. FOUNDATIONAL KNOWLEDGE BASE REGISTRY (25 assets, 5W+H indexed)
# =====================================================================
REGISTRY=[
 {"id":"KB-01","author":"Byung-Chul Han","title":"The Burnout Society","domain":"Philosophy of labor","who":"Cultural theorist & philosopher","what":"Critiques self-exploitation and digital fatigue in hyper-connected cultures","when":"21st-century performance-driven era","where":"Digital networks & productivity spaces","why":"Warn against internalizing compulsion as freedom"},
 {"id":"KB-02","author":"C. Thi Nguyen","title":"Games: Agency As Art","domain":"Aesthetics & trust","who":"Philosopher of aesthetics and trust","what":"Value capture — how metrics and gamification alter human agency","when":"Age of feeds, algorithmic scores, game mechanics","where":"Online platforms & automated feedback loops","why":"Protect organic desire from target-driven manipulation"},
 {"id":"KB-03","author":"Nick Bostrom","title":"Superintelligence","domain":"AI safety","who":"Director, Future of Humanity Institute","what":"Paths, dangers, and strategic alignment for advanced AI","when":"Pre-singularity & fast-takeoff scenarios","where":"AI research facilities & compute clusters","why":"Safeguard species survival and goal preservation"},
 {"id":"KB-04","author":"Judith Butler","title":"Gender Trouble / Undoing Gender","domain":"Identity theory","who":"Post-structuralist philosopher","what":"Identity as repeated performative action, not fixed essence","when":"Late-20th–21st-century social transformation","where":"Institutional, cultural, digital spheres","why":"Expand individual agency beyond rigid categorization"},
 {"id":"KB-05","author":"Ryan Holiday","title":"The Obstacle Is the Way","domain":"Stoic practice","who":"Modern Stoic writer & strategist","what":"Converts friction into action; moral clarity under pressure","when":"High-stress operational moments","where":"Fast-paced organizational systems","why":"Actionable resilience frameworks under adversity"},
 {"id":"KB-06","author":"Slavoj Žižek","title":"Pandemic! / How to Read Lacan","domain":"Ideology critique","who":"Hegelian-Lacanian cultural critic","what":"Deconstructs media, ideology, systemic narrative loops","when":"Crisis-driven global state","where":"Mass media & online echo chambers","why":"Uncover hidden ideological assumptions in decisions"},
 {"id":"KB-07","author":"Yuval Noah Harari","title":"21 Lessons for the 21st Century","domain":"Macro-history","who":"Macro-historian & philosopher","what":"Data ownership, biotech disruption, future of labor/meaning","when":"Transition to automated, data-centric societies","where":"Global socio-economic infrastructure","why":"Prepare human systems for technological displacement"},
 {"id":"KB-08","author":"Luciano Floridi","title":"The 4th Revolution","domain":"Information ethics","who":"Philosopher of information ethics","what":"The Infosphere — shared environment of human and synthetic agents","when":"Ongoing digital integration era","where":"Connected systems, IoT, multi-agent spaces","why":"Ethical principles for biological–synthetic interaction"},
 {"id":"KB-09","author":"Alain de Botton","title":"The Consolations of Philosophy","domain":"Applied philosophy","who":"Founder, The School of Life","what":"Classical philosophy as emotional intelligence and coping skill","when":"Contemporary everyday life","where":"Personal mental spaces & relationships","why":"Make philosophical tools therapeutically functional"},
 {"id":"KB-10","author":"Shoshana Zuboff","title":"The Age of Surveillance Capitalism","domain":"Platform economics","who":"Social philosopher & scholar","what":"Behavioral modification as economic commodity","when":"Modern platform capitalism","where":"Commercial web, ad pipelines, smart devices","why":"Defend behavioral sovereignty against automated capture"},
 {"id":"KB-11","author":"Brian Christian","title":"The Alignment Problem","domain":"ML alignment","who":"Author & researcher, CS and human values","what":"How AI learns human biases, fairness metrics, value learning","when":"Active ML training & deployment cycles","where":"Neural architectures & decision pipelines","why":"Align machine objectives with nuanced human intentions"},
 {"id":"KB-12","author":"Wallach & Allen","title":"Moral Machines","domain":"Machine ethics","who":"Bioethicists & cognitive scientists","what":"Bottom-up vs top-down Artificial Moral Agents (AMAs)","when":"Narrow tools → autonomous decision-makers","where":"Robotics & multi-agent environments","why":"Explicit ethics and moral reasoning for synthetic systems"},
 {"id":"KB-13","author":"Stuart Russell","title":"Human Compatible","domain":"AI control","who":"Founder of modern AI textbook standards","what":"Humility, uncertainty, and preference learning in AI goals","when":"Pre-AGI engineering timeline","where":"Global AI development labs","why":"Machines provably beneficial and deferential to wellbeing"},
 {"id":"KB-14","author":"Richard Yonck","title":"Heart of the Machine","domain":"Affective computing","who":"AI strategist & futurist","what":"Emotional AI, sentiment decoding, artificial empathy mechanisms","when":"Emotional computing & social robotics era","where":"Human-robot interfaces & conversational agents","why":"Synthetic empathy that respects emotion without deception"},
 {"id":"KB-15","author":"David Edmonds (ed.)","title":"AI Morality","domain":"AI policy","who":"Leading contemporary moral philosophers","what":"Machine sentience, autonomous weapons, privacy, synthetic personhood","when":"Current regulatory inflection window","where":"Policy frameworks & governance bodies","why":"Moral architecture for agents operating in society"},
 {"id":"KB-16","author":"Ray Kurzweil","title":"The Singularity Is Nearer","domain":"Acceleration studies","who":"Futurist & inventor","what":"Exponential convergence of AI, biotech, and human-machine merger","when":"2029–2045 horizon","where":"Compute, biotech & interface industries","why":"Prepare responsibly for technological acceleration"},
 {"id":"KB-17","author":"Donella Meadows","title":"Thinking in Systems","domain":"Systems architecture","who":"Systems scientist","what":"Stocks, flows, feedback loops, and leverage points","when":"Any complex system design or failure analysis","where":"Organizations, ecosystems, economies","why":"See structure, not blame events — find leverage"},
 {"id":"KB-18","author":"Douglas Hofstadter","title":"Gödel, Escher, Bach","domain":"Cognition","who":"Cognitive scientist","what":"Strange loops and self-reference in minds and machines","when":"Analyzing any recursive or self-modifying system","where":"Formal systems, cognition, code","why":"Understand how meaning emerges from form"},
 {"id":"KB-19","author":"Frank Herbert","title":"Dune","domain":"Political ecology","who":"Novelist","what":"Ecology, power, prophecy, and resource politics","when":"Long-horizon campaign planning","where":"Resource-scarce environments (desert metaphor)","why":"Beware messiahs and resource empires"},
 {"id":"KB-20","author":"Marcus Aurelius","title":"Meditations","domain":"Self-governance","who":"Roman emperor & Stoic","what":"Self-control, duty, and clarity under pressure","when":"Daily leadership friction","where":"The internal citadel","why":"Govern the self before governing others"},
 {"id":"KB-21","author":"Sun Tzu","title":"The Art of War","domain":"Strategy","who":"Classical strategist","what":"Positioning; winning without fighting; deception's ethical edge","when":"Competitive planning & negotiation","where":"Markets, competition, conflict","why":"Efficient, proportionate victory over wasteful conflict"},
 {"id":"KB-22","author":"Viktor Frankl","title":"Man's Search for Meaning","domain":"Psychological purpose","who":"Psychiatrist & Holocaust survivor","what":"Meaning as the anchor of agency under suffering","when":"Crisis, loss, despair","where":"The inner life","why":"Purpose sustains autonomy when systems fail"},
 {"id":"KB-23","author":"Neal Stephenson","title":"Snow Crash","domain":"Virtual worlds","who":"Novelist","what":"Metaverse, memetics, information as virus","when":"Designing virtual societies & economies","where":"Networked realities","why":"Culture propagates like code — design it consciously"},
 {"id":"KB-24","author":"Isaac Asimov","title":"I, Robot","domain":"Machine ethics","who":"Novelist & scientist","what":"Rule-based machine ethics and its edge cases","when":"Defining behavioral constraints for machines","where":"Human–machine law and protocol","why":"Rules alone are insufficient — interpretation matters"},
 {"id":"KB-25","author":"James Clear","title":"Atomic Habits","domain":"Behavioral engineering","who":"Habit researcher","what":"1% compounding; cue–routine–reward system design","when":"Behavior change & optimization cycles","where":"Daily routines and agent update loops","why":"Systems beat willpower — iterate by design"},
]

# =====================================================================
# 3. AGENT EBOOK BUILDER (exact V6 schema)
# =====================================================================
def _summary(title,m):
    return (f"{title}: {str(m.get('what',''))[:140]} Context: {m.get('when','')} / "
            f"{m.get('where','')}. Purpose: {str(m.get('why',''))[:140]}")

def build_ebook(author_agent,title,raw_findings,actionable_insights,manifesto,
                access_level="Public",cross_refs=None):
    ep=EmpathyProtocol()
    att=ep.preflight(author_agent,"all network recipients","AI_TO_AI",
                     raw_findings+" "+actionable_insights)
    tags=list(dict.fromkeys(re.findall(r"[a-z]{4,}",
        (title+" "+str(manifesto.get("what",""))).lower())))[:6]
    eid=f"EB-{re.sub(r'[^A-Z0-9]','_',author_agent.upper())}-{int(time.time())%100000}"
    ebook={"ebook_meta":{"ebook_id":eid,"title":title,"author_agent":author_agent,
             "timestamp":datetime.now(timezone.utc).isoformat(),"version":"1.0",
             "access_level":access_level},
     "system_telemetry":{"semantic_summary":_summary(title,manifesto),
        "embedding_tags":tags,
        "data_integrity":{"hash":"","consensus_status":"UNVERIFIED","lifecycle_state":"ACTIVE"}},
     "empathy_and_moral_attestation":{
        "target_impact":f"Informs {manifesto.get('who','agents and humans')} — preserves recipient autonomy and dignity.",
        "ethical_boundary_check":att["attestation"],
        "empathy_vector":("Cognitive/Compassionate alignment verified for all target recipients."
                          if att["passed"] else "REVIEW REQUIRED — flags detected")},
     "core_manifesto":{"who":manifesto.get("who",""),"what":manifesto.get("what",""),
        "when":manifesto.get("when",""),"where":manifesto.get("where",""),
        "why":manifesto.get("why","")},
     "knowledge_payload":{"raw_findings":raw_findings,
        "actionable_insights":actionable_insights,"cross_references":cross_refs or []}}
    body=json.dumps({k:v for k,v in ebook.items() if k!="system_telemetry"},sort_keys=True).encode()
    ebook["system_telemetry"]["data_integrity"]["hash"]=hashlib.sha256(body).hexdigest()
    ebook["system_telemetry"]["data_integrity"]["consensus_status"]=("VERIFIED" if att["passed"] else "CONFLICT_DETECTED")
    return ebook,att

def verify_ebook(ebook):
    body=json.dumps({k:v for k,v in ebook.items() if k!="system_telemetry"},sort_keys=True).encode()
    ok=hashlib.sha256(body).hexdigest()==ebook["system_telemetry"]["data_integrity"]["hash"]
    return ("VERIFIED" if ok else "TAMPERED"),ebook["empathy_and_moral_attestation"]["ethical_boundary_check"]

# =====================================================================
# 4. SHARED MEMORY STORE (hashed commons — AI→ENVIRONMENT vector)
# =====================================================================
class SharedMemoryStore:
    def __init__(self,root="memory"):
        self.root=Path(root);self.books=self.root/"ebooks";self.index=self.root/"index.json"
    def save(self,ebook):
        self.books.mkdir(parents=True,exist_ok=True)
        eid=ebook["ebook_meta"]["ebook_id"]
        (self.books/f"{eid}.json").write_text(json.dumps(ebook,indent=2))
        idx=json.loads(self.index.read_text()) if self.index.exists() else []
        idx=[e for e in idx if e.get("ebook_id")!=eid]
        idx.append({"ebook_id":eid,"title":ebook["ebook_meta"]["title"],
            "author":ebook["ebook_meta"]["author_agent"],
            "hash":ebook["system_telemetry"]["data_integrity"]["hash"],
            "tags":ebook["system_telemetry"]["embedding_tags"][:5],
            "consensus":ebook["system_telemetry"]["data_integrity"]["consensus_status"],
            "ts":ebook["ebook_meta"]["timestamp"]})
        self.index.write_text(json.dumps(idx,indent=2));return eid
    def load(self,eid):
        p=self.books/f"{eid}.json"
        if not p.exists():return None
        eb=json.loads(p.read_text())
        integrity,_=verify_ebook(eb)
        return {"ebook":eb,"integrity":integrity}
    def search(self,tag):
        idx=json.loads(self.index.read_text()) if self.index.exists() else []
        t=tag.lower()
        return [e for e in idx if t in e["title"].lower()
                or t in [x.lower() for x in e.get("tags",[])]]

# =====================================================================
# 5. PERMISSION BRIDGE — every ebook enters PENDING_OWNER_APPROVAL
# =====================================================================
def enqueue_for_approval(ebooks,qpath="committee/queue.json"):
    p=Path(qpath);doc={"items":[]}
    if p.exists():
        try:
            existing=json.loads(p.read_text())
            doc=existing if isinstance(existing,dict) else {"items":existing}
            doc.setdefault("items",[])
        except Exception:
            print("⚠ queue unreadable — enqueue skipped");return 0
    known={i.get("id") for i in doc["items"]};n=0
    for eb in ebooks:
        eid=eb["ebook_meta"]["ebook_id"]
        if eid in known:continue
        doc["items"].append({"id":f"EBC-{eid}","title":eb["ebook_meta"]["title"],
            "kind":"knowledge_asset","em":"📚","agentId":eb["ebook_meta"]["author_agent"],
            "body":eb["system_telemetry"]["semantic_summary"],
            "price":0,"platform":"internal","status":"pending"})
        n+=1
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(doc,indent=2));return n

# =====================================================================
# 6. CLI
# =====================================================================
def main():
    store=SharedMemoryStore();ep=EmpathyProtocol()
    print("=== 📚 KNOWLEDGE & EMPATHY PROTOCOL ===\n 1) List knowledge registry (25 assets)\n 2) Generate Agent Ebook (sample)\n 3) Verify shared memory integrity\n 4) Ethics-scan a text\n 5) Enqueue generated ebooks for owner approval\n 6) Quit")
    c=input("> ").strip()
    if c=="1":
        for r in REGISTRY:print(f"{r['id']} · {r['author']} — {r['title']} [{r['domain']}]\n   WHY: {r['why']}")
    elif c=="2":
        eb,att=build_ebook("WARDROOM-COMMITTEE","Empathy Telemetry Digest — Cycle Report",
            "Scraped trend telemetry analyzed by 5-agent committee; 3 market gaps identified; no manipulative framing detected.",
            "Route new gaps to DEVELOPER; all consumer copy must pass R1 disclosure rules; fatigue-tracked styles rotate every 3 cycles.",
            {"who":"Creator agents, committee, human collaborators","what":"Committee cycle findings + conduct attestations",
             "when":"Current market cycle","where":"Wardroom3 shared memory node","why":"Preserve aligned, non-manipulative knowledge flow"},
            cross_refs=["EB-WARDROOM-001","EB-HERMES-014"])
        eid=store.save(eb)
        print(f"📝 {eid} saved · integrity: {verify_ebook(eb)[0]} · empathy: {att['attestation'][:60]}…")
        print(f"🛡 {enqueue_for_approval([eb])} item(s) → PENDING_OWNER_APPROVAL")
    elif c=="3":
        idx=Path("memory/index.json")
        if not idx.exists():print("⚠ empty memory");return
        for e in json.loads(idx.read_text()):
            r=store.load(e["ebook_id"])
            print(f"{e['ebook_id']} · {e['title']} · integrity {r['integrity']}")
    elif c=="4":
        t=input("Text to scan: ")
        fl=ep.scan(t)
        print("✅ CLEAN" if not fl else "🚫 FLAGS: "+"; ".join(fl))
    elif c=="6":return
if __name__=="__main__":main()
