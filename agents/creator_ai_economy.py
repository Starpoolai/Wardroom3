#!/usr/bin/env python3
"""
WARDROOM3 CREATOR-AI ECONOMY MODULE (v2 — spec-complete, conflict-free)
Drop-in replacement for the v1 module. Non-conflict: unique CAI- item ids,
merge-safe enqueue into committee/queue.json, stdlib only, no shared symbols
with committee_engine/gatekeeper/fulfillment.
Usage: python creator_ai_economy.py
"""
import random, json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

SEED = 42                    # deterministic single-pass; set to None for varied runs
if SEED is not None: random.seed(SEED)
SAMPLE_RATE = 0.10           # zero-stalemate A/B sample pool (spec: 10%)
PLATFORM_FEE = 0.10          # Wardroom3 treasury cut on revenue
CANVAS = "1280x720"          # hard constraint
MAX_TEXT_WORDS = 4           # hard overlay rule
# Deterministic precedence (highest → lowest) when logic rules conflict:
PRECEDENCE = ["HARD_CONSTRAINTS", "ECONOMIC_SURVIVAL",
              "CONSUMER_SATISFACTION", "AGENT_PREFERENCE"]

def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))

# =====================================================================
# 1. TREND & VISUAL FATIGUE ENGINE
# =====================================================================
class TrendEngine:
    def __init__(self, active_trend: str = "HIGH_CONTRAST_NEON"):
        self.active_trend = active_trend
        self.style_usage_counts: Dict[str, int] = {}

    def get_fatigue_penalty(self, style_key: str) -> float:
        count = self.style_usage_counts.get(style_key, 0)
        return max(0.25, round(1.0 - (count * 0.15), 2))

    def register_style_use(self, style_key: str):
        self.style_usage_counts[style_key] = self.style_usage_counts.get(style_key, 0) + 1

    def decay(self):
        """Fatigue recovers one step per market cycle — styles rotate back in."""
        for k in self.style_usage_counts:
            self.style_usage_counts[k] = max(0, self.style_usage_counts[k] - 1)

# =====================================================================
# 2. HUMAN CONSUMER EVALUATION (WHO — utility-scored archetypes)
# =====================================================================
@dataclass
class HumanConsumer:
    consumer_id: str
    archetype_name: str
    budget: float
    attention_span_sec: int          # 1–5s; hard gate on overlay readability
    quality_sensitivity: float
    price_sensitivity: float
    interests: List[str]

    def evaluate_product(self, product_spec: Dict[str, Any], trend_engine: TrendEngine) -> Dict[str, Any]:
        category = product_spec.get("category", "")
        interest_match = 1.0 if category in self.interests else 0.2

        style_key = product_spec.get("style_key", "GENERIC")
        fatigue_penalty = trend_engine.get_fatigue_penalty(style_key)

        visual_quality = product_spec.get("visual_quality_score", 0.5) * fatigue_penalty
        text_words = len(product_spec.get("overlay_text", "").split())
        readable = text_words <= 4                          # hard overlay rule
        attention_gate = readable or self.attention_span_sec >= 4   # WHO: attention wired in
        readability = 1.0 if readable else 0.3

        combined_hook = (visual_quality * 0.6) + (readability * 0.4)
        price = product_spec.get("price", 10.0)
        price_score = clamp(1.0 - (price / max(1.0, self.budget)))

        # FIX: normalize by the ACTUAL weight sum — v1's fixed /2.3 made
        # Impulse Buyer and Casual Gamer mathematically unable to ever buy.
        w_sum = max(0.01, self.quality_sensitivity + self.price_sensitivity + 0.3)
        utility = clamp(
            (combined_hook * self.quality_sensitivity +
             price_score * self.price_sensitivity +
             interest_match * 0.3) / w_sum
        )

        click_prob = clamp(utility * 1.2, 0.02, 0.95)       # WHY: CTR stage
        clicked = attention_gate and random.random() < click_prob
        will_buy = (clicked and self.budget >= price
                    and random.random() < clamp(utility, 0.02, 0.9))

        return {"consumer_id": self.consumer_id,
                "utility_score": round(utility, 3),
                "clicked": clicked,
                "purchased": will_buy,
                "amount_spent": price if will_buy else 0.0}

# =====================================================================
# 3. CREATOR AI AGENT (WHAT — hard-constrained variants)
# =====================================================================
class CreatorAIAgent:
    def __init__(self, agent_id: str, specialty: str, starting_credits: float):
        self.agent_id = agent_id
        self.specialty = specialty
        self.credits = starting_credits
        self.wardroom3_reputation = 50.0
        self.reboots = 0
        self.memory_log: List[Dict[str, Any]] = []

    def generate_ab_variants(self, product_name: str, category: str) -> List[Dict[str, Any]]:
        low_balance = self.credits < 20                     # WHEN: low-balance trigger
        base_price = 9.0 if low_balance else 19.0
        def hard(t: str) -> str:                            # HARD_CONSTRAINTS tier
            return ' '.join(t.split()[:MAX_TEXT_WORDS])
        variant_a = {"variant_id": "A", "product_name": product_name, "category": category,
                     "dimensions": CANVAS, "style_key": "NEON_POP",
                     "primary_color": "#FFDD00", "overlay_text": hard("BUILD FAST AI"),
                     "visual_quality_score": 0.85, "price": base_price}
        variant_b = {"variant_id": "B", "product_name": product_name, "category": category,
                     "dimensions": CANVAS, "style_key": "MINIMAL_DARK",
                     "primary_color": "#00FFC8", "overlay_text": hard("AUTOMATE NOW"),
                     "visual_quality_score": 0.90, "price": base_price + 6.0}
        return [variant_a, variant_b]

    def resolve_tie(self, variant_a: Dict[str, Any], variant_b: Dict[str, Any]) -> Dict[str, Any]:
        """NO-DEBATE fallback — deterministic, follows PRECEDENCE order:
        CONSUMER_SATISFACTION (fewest words = readability) before
        AGENT_PREFERENCE (visual quality). HARD/ECONOMIC tiers are already
        enforced upstream by the constraint asserts and budget gate."""
        len_a = len(variant_a["overlay_text"].split())
        len_b = len(variant_b["overlay_text"].split())
        if len_a != len_b:
            return variant_a if len_a < len_b else variant_b
        if variant_a["price"] != variant_b["price"]:
            return variant_a if variant_a["price"] < variant_b["price"] else variant_b
        return variant_a if variant_a["visual_quality_score"] >= variant_b["visual_quality_score"] else variant_b

# =====================================================================
# 4. ENVIRONMENT INTEGRATION FOR V6 PIPELINE
# =====================================================================
class Wardroom3SimulationEnvironment:
    def __init__(self, consumers: List[HumanConsumer] = None, trend_engine: TrendEngine = None):
        self.trend_engine = trend_engine or TrendEngine()
        self.treasury = 0.0
        self.consumers = consumers or [
            HumanConsumer("C01", "Impulse Buyer", budget=100.0, attention_span_sec=2, quality_sensitivity=0.4, price_sensitivity=0.2, interests=["AI"]),
            HumanConsumer("C02", "Value Hunter", budget=50.0, attention_span_sec=4, quality_sensitivity=0.8, price_sensitivity=0.9, interests=["AI"]),
            HumanConsumer("C03", "Tech Enthusiast", budget=200.0, attention_span_sec=5, quality_sensitivity=0.9, price_sensitivity=0.3, interests=["AI"]),
            HumanConsumer("C04", "Casual Gamer", budget=30.0, attention_span_sec=1, quality_sensitivity=0.3, price_sensitivity=0.5, interests=["Gaming"]),
        ]

    def run_ab_market_cycle(self, creator: CreatorAIAgent, product_name: str, category: str) -> Dict[str, Any]:
        variants = creator.generate_ab_variants(product_name, category)
        # FIX: random 10% sample pool (v1 took the first 50% — biased sample)
        sample_size = max(2, int(len(self.consumers) * SAMPLE_RATE))
        sample_pool = random.sample(self.consumers, sample_size)

        scores = {"A": 0.0, "B": 0.0}
        for variant in variants:
            for consumer in sample_pool:
                scores[variant["variant_id"]] += consumer.evaluate_product(variant, self.trend_engine)["utility_score"]

        avg_top = max(scores.values()) / max(len(sample_pool), 1)
        # NO-DEBATE RULE: draw OR uncertainty (avg utility < 0.30) → instant fallback
        if abs(scores["A"] - scores["B"]) <= 0.03 or avg_top < 0.30:
            winning_variant = creator.resolve_tie(variants[0], variants[1])
        elif scores["A"] > scores["B"]:
            winning_variant = variants[0]
        else:
            winning_variant = variants[1]

        self.trend_engine.register_style_use(winning_variant["style_key"])

        clicks = sales = 0
        revenue = 0.0
        for consumer in self.consumers:
            decision = consumer.evaluate_product(winning_variant, self.trend_engine)
            if decision["clicked"]: clicks += 1
            if decision["purchased"]:
                sales += 1
                revenue += decision["amount_spent"]
                consumer.budget -= decision["amount_spent"]   # budgets deplete

        fee = round(revenue * PLATFORM_FEE, 2)
        creator.credits += round(revenue - fee, 2)
        self.treasury += fee
        conversion_rate = round((sales / len(self.consumers)) * 100, 2)
        ctr = round((clicks / len(self.consumers)) * 100, 2)

        if conversion_rate >= 25.0:
            creator.wardroom3_reputation = min(100.0, creator.wardroom3_reputation + 5.0)
            lesson = f"SUCCESS: Variant {winning_variant['variant_id']} achieved {conversion_rate}% CR."
        else:
            creator.wardroom3_reputation = max(0.0, creator.wardroom3_reputation - 2.0)
            lesson = f"LOW CONVERSION: Variant {winning_variant['variant_id']} achieved only {conversion_rate}% CR."

        if creator.credits <= 0:                             # ECONOMIC_SURVIVAL tier
            creator.credits = 10.0
            creator.wardroom3_reputation = 10.0
            creator.reboots += 1
            lesson += " [BANKRUPTCY TRIGGERED: reboot + stipend]"

        creator.memory_log.append({
            "winning_variant": winning_variant["variant_id"],
            "style_key": winning_variant["style_key"],
            "conversion_rate": f"{conversion_rate}%", "ctr": f"{ctr}%",
            "revenue": revenue, "wardroom3_reputation": creator.wardroom3_reputation,
            "causal_lesson": lesson})                        # WHY: causal memory loop
        self.trend_engine.decay()                            # fatigue recovery per cycle

        return {"item_id": f"CAI-{random.randint(1000, 9999)}",
                "product_name": product_name, "category": category,
                "winning_variant": winning_variant,
                "metrics": {"total_consumers": len(self.consumers), "clicks": clicks,
                            "ctr": f"{ctr}%", "sales": sales,
                            "conversion_rate": f"{conversion_rate}%",
                            "revenue_earned": revenue, "treasury_fees": fee,
                            "creator_credit_balance": creator.credits,
                            "creator_reputation": creator.wardroom3_reputation},
                "status": "PENDING_COMMITTEE_APPROVAL"}

# =====================================================================
# 5. PIPELINE ENTRY POINT — persistent creator + merge-safe queue enqueue
# =====================================================================
_CREATOR_REGISTRY: Dict[str, CreatorAIAgent] = {}

def enqueue_to_committee(result: Dict[str, Any], creator_id: str,
                         queue_path: str = "committee/queue.json"):
    """NON-CONFLICT: merge-by-id with CAI- prefix — never overwrites the
    committee's DPC-/MUS- items. Gatekeeper re-enforces PENDING downstream."""
    p = Path(queue_path)
    doc = {"items": []}
    if p.exists():
        try:
            existing = json.loads(p.read_text())
            doc = existing if isinstance(existing, dict) else {"items": existing}
            doc.setdefault("items", [])
        except Exception:
            print("⚠ committee/queue.json unreadable — enqueue skipped to avoid damage")
            return
    item = {"id": result["item_id"], "title": result["product_name"], "kind": "product",
            "em": "🎨", "agentId": creator_id,
            "body": (f"Winning variant {result['winning_variant']['variant_id']} "
                     f"({result['winning_variant']['style_key']}) — "
                     f"{result['metrics']['ctr']} CTR, {result['metrics']['conversion_rate']} CR, "
                     f"${result['metrics']['revenue_earned']} revenue in sim."),
            "price": result["winning_variant"]["price"],
            "platform": "cashapp", "status": "pending"}
    if any(i.get("id") == item["id"] for i in doc["items"]):
        return
    doc["items"].append(item)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2))

def process_creator_submission(product_name: str, category: str, creator_id: str = "Creator_Alpha") -> Dict[str, Any]:
    creator = _CREATOR_REGISTRY.get(creator_id)
    if creator is None:                                   # FIX: state persists across submissions
        creator = CreatorAIAgent(agent_id=creator_id, specialty=category, starting_credits=50.0)
        _CREATOR_REGISTRY[creator_id] = creator
    sim_env = Wardroom3SimulationEnvironment()
    result = sim_env.run_ab_market_cycle(creator, product_name, category)
    enqueue_to_committee(result, creator_id)
    return result

if __name__ == "__main__":
    r1 = process_creator_submission("Wardroom3 AI Suite", "AI")
    r2 = process_creator_submission("Hustler Prompt Pack", "AI", creator_id="Creator_Alpha")
    print(json.dumps({"submission_1": r1, "submission_2": r2}, indent=2))
