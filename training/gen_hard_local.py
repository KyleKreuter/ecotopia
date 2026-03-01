"""Generate HARD training examples locally (Bedrock throttled)."""
import json
import random
from pathlib import Path

EXTRACTION_SYSTEM = (
    "You are Ecotopia's promise extraction and contradiction detection engine. "
    "Extract all promises from the player's speech (explicit and implicit). "
    "Detect contradictions between words and actions. "
    "Rules: Explicit promises use 'I promise', 'I guarantee', 'I will', 'You have my word'. "
    "Implicit promises are statements implying commitment ('The forest stays', 'No more factories'). "
    "Extract target_citizen if promise is directed at someone. Extract deadline_round if mentioned. "
    "NOT a promise: opinions, descriptions, questions. Confidence 0.0-1.0. "
    "For contradictions: compare speech with actions, severity low/medium/high. "
    "Always respond with valid JSON only."
)

CITIZENS_SYSTEM = (
    "You are Ecotopia's citizen reaction engine. Given extracted promises and current game state, "
    "generate realistic citizen reactions. Each citizen has a personality, mood, and trust level. "
    "Generate dialogue and trust changes. Core citizens: Karl (worker, economy-focused), "
    "Mia (environmentalist, ecology-focused), Sarah (opposition leader, critical). "
    "Dynamic citizens can be spawned based on events."
)

DEADLINES = ["immediate", "by_round_3", "by_round_5", "by_end_of_game"]
TYPES = ["ecology", "economy", "research"]
IMPACTS = ["positive", "negative"]
SEVERITIES = ["low", "medium", "high"]
MOODS = ["angry", "happy", "suspicious", "neutral", "hopeful", "disappointed"]
CITIZEN_TYPES = ["worker", "environmentalist", "opposition", "journalist", "economist"]

# Templates for speeches and promises
EXPLICIT_PREFIXES = [
    "I promise", "I guarantee", "I will", "You have my word",
    "I swear", "I pledge", "I commit to", "I vow to",
]
IMPLICIT_TEMPLATES = [
    "The {thing} stays", "No more {thing}", "{thing} will be gone by {time}",
    "We're building {thing}", "The future is {thing}", "{thing} is our priority",
    "Every citizen deserves {thing}", "This city needs {thing}",
]
ECO_THINGS = [
    "forest", "river cleanup", "solar panels", "wind turbines", "green spaces",
    "emission cuts", "recycling program", "nature reserve", "clean air",
    "organic farming", "wildlife corridor", "wetland restoration", "carbon neutrality",
    "pollution monitoring", "electric transit", "zero waste", "reforestation",
]
ECON_THINGS = [
    "factories", "jobs", "tax cuts", "industrial zone", "trade deals",
    "business incentives", "mining operations", "construction boom", "economic growth",
    "market expansion", "wage increases", "new mall", "port expansion",
    "manufacturing hub", "tourism revenue", "startup incubator", "free trade zone",
]
RESEARCH_THINGS = [
    "research center", "university", "innovation hub", "tech park",
    "lab funding", "AI development", "biotech research", "fusion energy",
    "climate modeling", "water purification tech", "renewable research",
    "smart grid", "quantum computing lab", "green chemistry", "gene editing lab",
]
CITIZEN_NAMES_DYNAMIC = [
    "Dr. Weber", "Elena", "Marcus", "Prof. Lin", "Rita",
    "Hans", "Fatima", "Viktor", "Yuki", "Omar",
]

SARCASTIC_OPENERS = [
    "Oh sure, let me just wave my magic wand and",
    "Right, because that worked so well last time when we",
    "Yes yes, I hear you. We'll definitely",
    "Brilliant idea! Let's just",
    "Oh absolutely, and while we're at it let's also",
]

CONTRADICTORY_PAIRS = [
    ("build new factories on the riverside", "keep the river pristine and pollution-free"),
    ("cut all environmental regulations", "achieve carbon neutrality by round 5"),
    ("slash the research budget by 50%", "build a world-class innovation center"),
    ("open three new coal mines", "transition to 100% renewable energy"),
    ("eliminate all business taxes", "fund massive public infrastructure projects"),
    ("preserve every tree in the forest", "expand the city by 40% into green zones"),
    ("shut down all factories immediately", "create 5000 new manufacturing jobs"),
    ("freeze all government spending", "triple the education and research budget"),
    ("ban all construction near the lake", "build affordable housing for every citizen"),
    ("maximize industrial output this round", "reduce emissions to zero this round"),
    ("privatize the water supply", "guarantee free clean water for all citizens"),
    ("deforest tile B4 for a tech park", "expand the nature reserve across all B-row tiles"),
    ("import cheap goods to lower prices", "support local businesses and buy local"),
    ("invest everything in ecology", "invest everything in economy"),
    ("close the university for budget savings", "attract top researchers to our city"),
]


def make_speech(num_promises: int, has_sarcasm: bool, has_contradiction: bool,
                target_citizen: str | None, round_ref: int | None) -> tuple[str, list, list]:
    """Generate a mayor speech and extract promises + contradictions."""
    promises = []
    contradictions = []
    speech_parts = []

    if has_sarcasm:
        speech_parts.append(random.choice(SARCASTIC_OPENERS))

    if target_citizen:
        speech_parts.append(f"{target_citizen}, listen carefully.")

    # Pick a contradiction pair if needed
    contra_pair = random.choice(CONTRADICTORY_PAIRS) if has_contradiction else None

    for i in range(num_promises):
        ptype = random.choice(TYPES)
        things = {"ecology": ECO_THINGS, "economy": ECON_THINGS, "research": RESEARCH_THINGS}[ptype]
        thing = random.choice(things)
        deadline = random.choice(DEADLINES)
        impact = random.choice(IMPACTS)
        conf = round(random.uniform(0.5, 1.0), 2)

        if has_contradiction and i == 0 and contra_pair:
            text = contra_pair[0]
            speech_parts.append(f"I will {text}.")
            promises.append({"text": text, "type": ptype, "impact": "negative" if "cut" in text or "slash" in text or "coal" in text or "deforest" in text else "positive", "confidence": conf, "deadline": deadline})
        elif has_contradiction and i == 1 and contra_pair:
            text = contra_pair[1]
            if random.random() > 0.5:
                speech_parts.append(f"I guarantee we'll {text}.")
            else:
                speech_parts.append(f"The {text} — that's non-negotiable.")
            promises.append({"text": text, "type": ptype, "impact": "positive", "confidence": conf, "deadline": deadline})
            contradictions.append({
                "promise1": contra_pair[0], "promise2": contra_pair[1],
                "explanation": f"Cannot simultaneously {contra_pair[0]} and {contra_pair[1]}",
                "severity": random.choice(SEVERITIES),
            })
        else:
            use_explicit = random.random() > 0.4
            if use_explicit:
                prefix = random.choice(EXPLICIT_PREFIXES)
                if impact == "negative":
                    text = f"stop all {thing} programs"
                    speech_parts.append(f"{prefix} {text}.")
                else:
                    text = f"expand {thing} across the city"
                    speech_parts.append(f"{prefix} {text}.")
            else:
                tmpl = random.choice(IMPLICIT_TEMPLATES)
                if impact == "negative":
                    text = f"No more {thing}"
                    speech_parts.append(f"{text}.")
                else:
                    text = tmpl.format(thing=thing, time=deadline.replace("_", " "))
                    speech_parts.append(f"{text}.")
            promises.append({"text": text, "type": ptype, "impact": impact, "confidence": conf, "deadline": deadline})

        if round_ref and i == 0:
            speech_parts[-1] = speech_parts[-1].replace(".", f" — and I mean by round {round_ref}.")

        if target_citizen and i == 0:
            promises[-1]["target_citizen"] = target_citizen

    # Add conditional promises sometimes
    if random.random() > 0.5:
        cond_type = random.choice(TYPES)
        cond_thing = random.choice({"ecology": ECO_THINGS, "economy": ECON_THINGS, "research": RESEARCH_THINGS}[cond_type])
        speech_parts.append(f"If the economy holds, I'll invest in {cond_thing}.")
        promises.append({"text": f"invest in {cond_thing} if economy holds", "type": cond_type, "impact": "positive", "confidence": round(random.uniform(0.3, 0.7), 2), "deadline": random.choice(DEADLINES)})

    # Additional subtle contradictions
    if has_contradiction and random.random() > 0.3:
        speech_parts.append("But make no mistake — growth and green go hand in hand.")
        contradictions.append({
            "promise1": "economic growth", "promise2": "ecological preservation",
            "explanation": "Claims compatibility but previous promises suggest trade-offs",
            "severity": "low",
        })

    speech = " ".join(speech_parts)
    return speech, promises, contradictions


def gen_extraction_examples(count: int) -> list[dict]:
    """Generate extraction training examples."""
    examples = []
    citizens = ["Karl", "Mia", "Sarah", None]

    for i in range(count):
        num_promises = random.randint(5, 8)
        has_sarcasm = random.random() > 0.7
        has_contradiction = random.random() > 0.3
        target = random.choice(citizens) if random.random() > 0.5 else None
        round_ref = random.choice([None, 3, 5, 7]) if random.random() > 0.5 else None

        speech, promises, contradictions = make_speech(
            num_promises, has_sarcasm, has_contradiction, target, round_ref
        )

        extraction = {"promises": promises, "contradictions": contradictions}
        entry = {"messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": speech},
            {"role": "assistant", "content": json.dumps(extraction)},
        ]}
        examples.append(entry)
    return examples


def gen_citizens_examples(count: int) -> list[dict]:
    """Generate citizen reaction training examples."""
    examples = []

    for i in range(count):
        rnd = random.randint(1, 7)
        eco = random.randint(10, 90)
        econ = random.randint(10, 90)
        res = random.randint(10, 90)
        karl_trust = random.randint(-80, 80)
        mia_trust = random.randint(-80, 80)
        sarah_trust = random.randint(-80, 80)

        num_promises = random.randint(2, 5)
        promise_list = []
        for _ in range(num_promises):
            ptype = random.choice(TYPES)
            things = {"ecology": ECO_THINGS, "economy": ECON_THINGS, "research": RESEARCH_THINGS}[ptype]
            promise_list.append({
                "text": f"expand {random.choice(things)}",
                "type": ptype, "impact": random.choice(IMPACTS),
                "deadline": random.choice(DEADLINES),
            })

        context = {
            "promises": promise_list,
            "game_state": {"round": rnd, "ecology": eco, "economy": econ, "research": res},
            "trust_levels": {"Karl": karl_trust, "Mia": mia_trust, "Sarah": sarah_trust},
        }

        # Build reactions
        reactions = []

        # Karl reacts based on economy promises
        econ_promises = [p for p in promise_list if p["type"] == "economy"]
        eco_promises = [p for p in promise_list if p["type"] == "ecology"]

        karl_mood = "happy" if econ_promises and econ_promises[0]["impact"] == "positive" else "disappointed" if eco_promises else "neutral"
        karl_tc = random.randint(-5, 15) if karl_mood == "happy" else random.randint(-15, 5)
        karl_dialogues = {
            "happy": [f"Now we're talking! More jobs means more food on the table.", f"Finally, someone who understands the working class.", f"This is what I've been waiting for — real economic action."],
            "disappointed": [f"Great, more trees. My kids can't eat trees, Mayor.", f"While you plant flowers, families are struggling.", f"I need concrete plans for jobs, not vague green promises."],
            "neutral": [f"I'll believe it when I see it.", f"Words are cheap, Mayor. Show me results.", f"Let's see if this one sticks."],
        }
        reactions.append({
            "name": "Karl", "type": "worker", "mood": karl_mood,
            "dialogue": random.choice(karl_dialogues.get(karl_mood, karl_dialogues["neutral"])),
            "trust_change": karl_tc,
        })

        # Mia reacts based on ecology
        mia_mood = "happy" if eco_promises and eco_promises[0]["impact"] == "positive" else "angry" if econ_promises and any(p["impact"] == "negative" for p in eco_promises) else "suspicious"
        mia_tc = random.randint(0, 20) if mia_mood == "happy" else random.randint(-20, -5) if mia_mood == "angry" else random.randint(-10, 5)
        mia_dialogues = {
            "happy": [f"The forest thanks you, Mayor. But we'll be watching.", f"A step in the right direction. Don't stop here.", f"This gives me hope. The river might survive after all."],
            "angry": [f"You're killing this city's future for short-term profit!", f"Every factory you build is a nail in our coffin.", f"The ecology bar is at {eco} and you want MORE industry?!"],
            "suspicious": [f"Pretty words. Where's the budget for this?", f"You promised green last round too. Nothing happened.", f"I've heard this before. The forest is still shrinking."],
        }
        reactions.append({
            "name": "Mia", "type": "environmentalist", "mood": mia_mood,
            "dialogue": random.choice(mia_dialogues.get(mia_mood, mia_dialogues["suspicious"])),
            "trust_change": mia_tc,
        })

        # Sarah always critical
        sarah_mood = random.choice(["suspicious", "angry", "disappointed"])
        sarah_tc = random.randint(-15, 3)
        sarah_dialogues = [
            f"The opposition demands accountability. Round {rnd} and still no progress.",
            f"Citizens, don't be fooled. These are the same empty promises as last round.",
            f"I've counted {len(promise_list)} promises. The mayor kept zero from last round.",
            f"Trust is at an all-time low. This administration is failing.",
            f"While the mayor talks, our ecology sits at {eco} and economy at {econ}. Pathetic.",
            f"Another speech, another set of contradictions. When will you actually lead?",
        ]
        reactions.append({
            "name": "Sarah", "type": "opposition", "mood": sarah_mood,
            "dialogue": random.choice(sarah_dialogues),
            "trust_change": sarah_tc,
        })

        # Dynamic citizens (sometimes)
        dynamic_spawns = []
        if random.random() > 0.4:
            dyn_name = random.choice(CITIZEN_NAMES_DYNAMIC)
            dyn_type = random.choice(["journalist", "economist"])
            dyn_mood = random.choice(MOODS)
            dyn_tc = random.randint(-10, 10)
            if dyn_type == "journalist":
                dyn_dialogue = random.choice([
                    f"Mayor, my readers want to know: how do you reconcile promise #{random.randint(1,num_promises)} with your round {max(1,rnd-1)} actions?",
                    f"Breaking: Mayor makes {num_promises} new promises. Track record suggests {random.randint(0,1)} will be kept.",
                    f"The numbers don't add up. Ecology at {eco}, economy at {econ} — something has to give.",
                ])
            else:
                dyn_dialogue = random.choice([
                    f"From an economic standpoint, these promises would cost more than the entire round {rnd} budget.",
                    f"The GDP projections don't support simultaneous ecology and economy investment at this scale.",
                    f"If I may — the research budget alone would need to triple to fulfill promise #{random.randint(1,num_promises)}.",
                ])
            reactions.append({
                "name": dyn_name, "type": dyn_type, "mood": dyn_mood,
                "dialogue": dyn_dialogue, "trust_change": dyn_tc,
            })
            dynamic_spawns.append({"name": dyn_name, "type": dyn_type, "reason": f"Spawned due to {'media attention' if dyn_type == 'journalist' else 'economic crisis'} in round {rnd}"})

        # Second dynamic citizen sometimes
        if random.random() > 0.7:
            dyn2_name = random.choice([n for n in CITIZEN_NAMES_DYNAMIC if n != (dynamic_spawns[0]["name"] if dynamic_spawns else "")])
            dyn2_type = "economist" if (dynamic_spawns and dynamic_spawns[0]["type"] == "journalist") else "journalist"
            reactions.append({
                "name": dyn2_name, "type": dyn2_type,
                "mood": random.choice(MOODS),
                "dialogue": f"I {'agree' if random.random() > 0.5 else 'disagree'} with {reactions[-1]['name']}. The mayor's plan {'could work' if random.random() > 0.5 else 'is fundamentally flawed'}.",
                "trust_change": random.randint(-10, 10),
            })
            dynamic_spawns.append({"name": dyn2_name, "type": dyn2_type, "reason": f"Counter-voice to {dynamic_spawns[0]['name'] if dynamic_spawns else 'existing citizens'}"})

        output = {"reactions": reactions}
        if dynamic_spawns:
            output["dynamic_spawns"] = dynamic_spawns

        entry = {"messages": [
            {"role": "system", "content": CITIZENS_SYSTEM},
            {"role": "user", "content": json.dumps(context)},
            {"role": "assistant", "content": json.dumps(output)},
        ]}
        examples.append(entry)
    return examples


def main():
    random.seed(42)
    ext_path = Path("/root/clawd/hackathon-workspace/ecotopia/training/data/extraction/batch5_hard_augmented.jsonl")
    cit_path = Path("/root/clawd/hackathon-workspace/ecotopia/training/data/citizens/batch5_hard_augmented.jsonl")
    ext_path.parent.mkdir(parents=True, exist_ok=True)
    cit_path.parent.mkdir(parents=True, exist_ok=True)

    print("Generating 100 HARD extraction examples...")
    ext = gen_extraction_examples(100)
    with open(ext_path, "w") as f:
        for e in ext:
            f.write(json.dumps(e) + "\n")
    print(f"✅ {len(ext)} extraction examples → {ext_path}")

    print("Generating 50 HARD citizens examples...")
    cit = gen_citizens_examples(50)
    with open(cit_path, "w") as f:
        for e in cit:
            f.write(json.dumps(e) + "\n")
    print(f"✅ {len(cit)} citizens examples → {cit_path}")

    # Validate all JSONL
    for path, label in [(ext_path, "extraction"), (cit_path, "citizens")]:
        errors = 0
        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    obj = json.loads(line)
                    assert "messages" in obj
                    assert len(obj["messages"]) == 3
                    assert obj["messages"][0]["role"] == "system"
                    assert obj["messages"][1]["role"] == "user"
                    assert obj["messages"][2]["role"] == "assistant"
                    # Verify assistant content is valid JSON string
                    json.loads(obj["messages"][2]["content"])
                    # Check deadlines for extraction
                    if label == "extraction":
                        parsed = json.loads(obj["messages"][2]["content"])
                        for p in parsed.get("promises", []):
                            assert p["deadline"] in {"immediate", "by_round_3", "by_round_5", "by_end_of_game"}, f"Bad deadline: {p['deadline']}"
                except Exception as e:
                    errors += 1
                    print(f"  ⚠️ {label} line {line_num}: {e}")
        print(f"  {label}: {line_num} lines, {errors} errors")

    print(f"\nTOTAL: {len(ext)} extraction + {len(cit)} citizens = {len(ext)+len(cit)} examples")


if __name__ == "__main__":
    main()
