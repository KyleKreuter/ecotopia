"""Generate JSONL training data for Ecotopia citizen dialogue fine-tuning."""
import json
import random
import os

random.seed(42)

SYSTEM_PROMPT = "You are Ecotopia's citizen simulation engine. Given the game state, player's extracted promises, contradiction report, and citizen profiles, generate realistic citizen reactions. Each citizen reacts based on their personality, values, and how the player's actions affect them. Spawn new dynamic citizens when game events warrant it. Rules: approval_delta ranges -15 to +15 per citizen per round. Dynamic citizens spawn when ecology/economy hits extremes or promises are repeatedly broken. Each citizen has a unique voice matching their background. Always respond with valid JSON only."

OUTDIR = "/root/clawd/ecotopia/training/data/citizens/"

PROMISES_POOL = [
    "Protect old-growth forests from logging",
    "Create 500 new green jobs by year end",
    "Reduce factory emissions by 40%",
    "Fund retraining programs for displaced workers",
    "Build a new solar farm on the east ridge",
    "Ban single-use plastics in the city",
    "Subsidize local businesses during transition",
    "Establish a wildlife corridor along the river",
    "Invest in carbon capture research",
    "Guarantee no layoffs during restructuring",
    "Open a community garden in every district",
    "Double the public transit budget",
    "Provide free childcare for factory workers",
    "Clean up the industrial waste site",
    "Create a citizen oversight committee",
    "Freeze utility prices for two years",
    "Plant 10,000 trees in deforested areas",
    "Build affordable housing near the factory district",
    "Fund independent environmental monitoring",
    "Establish a universal basic income pilot"
]

ACTIONS_POOL = [
    "Signed executive order to protect forests",
    "Allocated budget to green job creation",
    "Delayed emission reduction timeline",
    "Launched worker retraining program",
    "Approved solar farm construction permits",
    "Vetoed plastic ban proposal",
    "Cut subsidies to local businesses",
    "Funded wildlife corridor study",
    "Increased research budget by 20%",
    "Announced factory restructuring plan",
    "Did nothing significant this round",
    "Held public consultation meeting",
    "Diverted ecology funds to economy",
    "Diverted economy funds to ecology",
    "Passed compromise legislation",
    "Broke promise on emission reductions",
    "Kept promise on job creation",
    "Ignored citizen petition",
    "Expanded industrial zone",
    "Shut down polluting factory"
]

SPEECHES_POOL = [
    "We must balance progress with preservation.",
    "Jobs and nature are not enemies.",
    "I promise a brighter future for all.",
    "Tough decisions require tough leaders.",
    "We will not abandon our workers.",
    "The environment cannot wait.",
    "Every sacrifice today builds tomorrow.",
    "Trust me, I have a plan.",
    "We are stronger together.",
    "Change is painful but necessary."
]

CONTRADICTION_TEMPLATES = [
    {"promise": "Reduce factory emissions by 40%", "action": "Expanded industrial zone", "severity": "high"},
    {"promise": "Guarantee no layoffs during restructuring", "action": "Announced factory restructuring plan", "severity": "medium"},
    {"promise": "Protect old-growth forests from logging", "action": "Diverted ecology funds to economy", "severity": "high"},
    {"promise": "Subsidize local businesses during transition", "action": "Cut subsidies to local businesses", "severity": "high"},
    {"promise": "Ban single-use plastics in the city", "action": "Vetoed plastic ban proposal", "severity": "high"},
    {"promise": "Create 500 new green jobs by year end", "action": "Did nothing significant this round", "severity": "medium"},
    {"promise": "Fund independent environmental monitoring", "action": "Ignored citizen petition", "severity": "medium"},
    {"promise": "The environment cannot wait.", "action": "Delayed emission reduction timeline", "severity": "medium"},
]

KARL_DIALOGUES = {
    "angry": [
        "You promised us jobs, and what did we get? More uncertainty. My crew is talking about leaving.",
        "I stood on that factory floor for twenty years. Do not tell me about sacrifice.",
        "Another week, another broken promise. The workers are done waiting.",
        "You shut down the plant without a plan. People have families to feed.",
        "I warned you this would happen. Nobody listens to the working man.",
        "My neighbors are losing their homes and you are talking about trees.",
        "The union is ready to strike. You pushed us to this.",
        "We gave you a chance. You gave us pink slips.",
    ],
    "hopeful": [
        "The retraining program actually looks decent. Maybe this can work.",
        "I talked to the guys at the plant. They are cautiously optimistic.",
        "If you follow through on these jobs, I will be the first to say I was wrong about you.",
        "The new positions at the solar farm pay better than I expected.",
        "For the first time in months, I feel like someone is actually listening.",
        "My daughter asked if dad would keep his job. I told her yes. Do not make me a liar.",
        "The subsidies are helping. Small steps, but real ones.",
        "I see the green jobs posting. That is a good start.",
    ],
    "sarcastic": [
        "Oh wonderful, another speech about the future. My rent is due now.",
        "Sure, green jobs. Let me just retrain as a solar panel whisperer overnight.",
        "I love how every plan starts with the workers making sacrifices first.",
        "A committee. Brilliant. That will definitely pay my mortgage.",
        "You want me to trust the process? Which process, the one that laid off my shift?",
        "Great, more research. Meanwhile the factory is collecting dust.",
    ],
    "desperate": [
        "Please. I am not asking for much. Just do not let the plant close without an alternative.",
        "I have three kids. I cannot afford to start over at forty-five.",
        "If we lose the factory, this town dies. You understand that, right?",
        "I am begging you to think about the workers before making another cut.",
    ],
    "grateful": [
        "I never thought I would say this, but thank you. The jobs are real.",
        "You kept your word on the retraining. That means something to us.",
        "The factory workers voted. We support you. Do not let us down.",
        "My wife cried when she heard about the new positions. Good tears.",
    ],
    "suspicious": [
        "I have seen politicians promise jobs before. Forgive me if I wait to see the contracts.",
        "The numbers look good on paper. But paper does not feed families.",
        "Why should I believe this time is different?",
        "I will believe it when my crew gets their first paycheck from the new program.",
    ],
}

MIA_DIALOGUES = {
    "angry": [
        "You are destroying everything. The river is dying and you are counting profits.",
        "I chained myself to that tree for a reason. Do not make me do it again.",
        "The emissions data is public. You lied. The pollution got worse.",
        "Every day you delay, another species edges closer to extinction.",
        "You sold us out to the industry lobby. I have the documents.",
        "The old-growth forest is irreplaceable. You cannot just plant new trees and call it even.",
        "Children are getting sick from the water. How do you sleep at night?",
        "I trusted you. That was my mistake.",
    ],
    "hopeful": [
        "The wildlife corridor proposal is beautiful. This could actually save the wetlands.",
        "I walked through the reforested area yesterday. Life is coming back.",
        "If you keep this up, Ecotopia could be a model for the world.",
        "The solar farm reduces emissions AND creates jobs. This is what I have been asking for.",
        "For once, the data is moving in the right direction. Keep going.",
        "The bird populations are recovering. Nature is resilient if we give it a chance.",
        "I cried at the river yesterday. The water is clear again.",
        "This is what leadership looks like. Real action, real results.",
    ],
    "sarcastic": [
        "Oh, a study on the environmental impact. How groundbreaking. Maybe in ten years we will have results.",
        "Compromise. That is a funny word for letting them pollute half as much.",
        "You planted fifty trees and called it reforestation. The math does not work that way.",
        "A green committee with zero budget. Very inspiring.",
        "I am sure the fish appreciate your thoughts and prayers.",
        "Another promise to protect nature right after approving the new pipeline.",
    ],
    "desperate": [
        "The ecosystem is collapsing. I am not exaggerating. Look at the data.",
        "We have maybe two years before the damage is irreversible. Please act.",
        "I have dedicated my life to this. Watching it fall apart is unbearable.",
        "The coral is bleaching, the forests are shrinking. What will it take?",
    ],
    "grateful": [
        "You actually did it. The forest is protected. Thank you from the bottom of my heart.",
        "The emission numbers dropped. Real, measurable progress. I am genuinely moved.",
        "I did not think a politician would ever follow through on environmental promises. You proved me wrong.",
        "The children will inherit something worth protecting. That is your legacy.",
    ],
    "suspicious": [
        "The last leader promised the same thing. The forests are still burning.",
        "I want to believe you, but your voting record tells a different story.",
        "Show me the enforcement mechanism. Promises without teeth are just noise.",
        "You say you care about ecology. Your budget says otherwise.",
    ],
}

SARAH_DIALOGUES = {
    "angry": [
        "This is exactly the kind of incompetence I warned the council about.",
        "You had every resource at your disposal and you still failed. Resign.",
        "The opposition formally objects. This policy is a disaster.",
        "I have filed a motion of no confidence. The people deserve better.",
        "You are not leading. You are flailing. And everyone can see it.",
        "Every metric is worse than when you started. Explain that.",
        "I gave you the benefit of the doubt. Never again.",
        "The council received 200 complaints this week. Your approval is tanking.",
    ],
    "hopeful": [
        "I will admit, this proposal has merit. I still have concerns, but it is a step forward.",
        "The oversight committee was a good call. Transparency matters.",
        "If you maintain this trajectory, you might actually earn the public trust.",
        "I reviewed the latest data. Reluctantly, I must say you are improving.",
        "The opposition acknowledges progress. We will be watching closely.",
        "Credit where it is due. This policy is well-designed.",
    ],
    "sarcastic": [
        "Congratulations on doing the bare minimum. Should we throw a parade?",
        "Another grand speech. Wake me when there are results.",
        "I love how every failure is framed as a learning opportunity.",
        "You promised transformation and delivered a pamphlet.",
        "The spin is impressive. The results, less so.",
        "A town hall meeting. How democratic. Did you prepare the applause signs?",
    ],
    "desperate": [
        "I am running out of ways to hold you accountable. The system is failing.",
        "Even the opposition needs something to work with. Give us anything.",
        "The public is losing faith in all of us. Not just you. All of us.",
        "I never thought I would say this, but maybe we need to work together.",
    ],
    "grateful": [
        "I misjudged you on this one. The citizen committee works. Well done.",
        "The opposition formally commends this initiative. It is rare, so appreciate it.",
        "You earned this one. The transparency report is exactly what we needed.",
        "I told my constituents you delivered. Do not make me regret it.",
    ],
    "suspicious": [
        "What is the catch? There is always a catch with your proposals.",
        "I have my analysts reviewing every line of this policy. We will find the holes.",
        "The timing of this announcement is suspicious. What are you distracting from?",
        "Your track record does not inspire confidence. Prove me wrong.",
    ],
}

CITIZEN_DIALOGUES = {"Karl": KARL_DIALOGUES, "Mia": MIA_DIALOGUES, "Sarah": SARAH_DIALOGUES}

DYNAMIC_CITIZENS_TEMPLATES = {
    "climate_refugee": {
        "names": ["Elena", "Marco", "Fatima", "Jorge", "Priya"],
        "role": "climate refugee",
        "personality": "resilient but desperate, speaks from lived experience of environmental collapse",
        "trigger_reason": "ecology dropped below critical threshold",
        "intro_dialogues": [
            "I left my home because the floods took everything. Do not let it happen here too.",
            "Where I come from, they ignored the warnings. Now there is nothing left. Listen to the signs.",
            "I walked two hundred miles because the drought killed our crops. Your ecology numbers terrify me.",
            "My village does not exist anymore. The sea took it. I am here because Ecotopia still has a chance.",
            "They said the water would come back. It never did. Please do not repeat our mistakes.",
        ],
    },
    "business_owner": {
        "names": ["Victor", "Margaret", "Chen", "Douglas", "Rita"],
        "role": "angry business owner",
        "personality": "pragmatic and confrontational, sees economic collapse firsthand",
        "trigger_reason": "economy dropped below critical threshold",
        "intro_dialogues": [
            "I have run this shop for thirty years. Three more months of this and I am done.",
            "My employees are asking when payday is. I do not have an answer. Fix the economy.",
            "The supply chains are broken. Nobody is buying. What is your plan?",
            "I closed two locations this month. The third closes Friday unless something changes.",
            "You talk about the future while businesses die today. Come see my empty shelves.",
        ],
    },
    "tech_entrepreneur": {
        "names": ["Zara", "Felix", "Anika", "Dev", "Lena"],
        "role": "tech entrepreneur",
        "personality": "optimistic innovator, sees opportunity in research breakthroughs",
        "trigger_reason": "research exceeded innovation threshold",
        "intro_dialogues": [
            "Your research investment is paying off. I want to build the next generation of clean tech here.",
            "I just secured funding for a carbon capture startup. Ecotopia is the perfect base.",
            "The innovation happening here is remarkable. Let me show you what we can do with it.",
            "I relocated my company because of your research programs. Do not stop now.",
            "The data from your labs is groundbreaking. We can commercialize this within months.",
        ],
    },
    "journalist": {
        "names": ["Diana", "Robert", "Yuki", "Samuel", "Iris"],
        "role": "investigative journalist",
        "personality": "relentless truth-seeker, tracks every promise and holds leaders accountable",
        "trigger_reason": "multiple promises broken, public trust eroding",
        "intro_dialogues": [
            "I have been tracking your promises. The gap between words and actions is newsworthy.",
            "My readers want answers. Three broken promises in a row demands investigation.",
            "I am here because the public deserves to know the truth. Care to comment?",
            "The editorial board sent me. Your credibility is the story now.",
            "I have documents showing the discrepancy between your claims and the data. Respond.",
        ],
    },
    "nature_guide": {
        "names": ["Birch", "Willow", "Sage", "River", "Fern"],
        "role": "nature guide",
        "personality": "calm and wise, deeply connected to the land, speaks poetically about nature",
        "trigger_reason": "ecology thriving, natural world recovering",
        "intro_dialogues": [
            "The eagles returned to the valley this morning. I came to tell you it is working.",
            "I have guided people through these woods for decades. They have never been this alive.",
            "The river runs clear for the first time in years. The land remembers how to heal.",
            "I found wildflowers growing where the old dump site was. Nature forgives if we let it.",
            "The forest is singing again. I thought I would never hear it. Thank you.",
        ],
    },
}


def pick_dialogue(citizen_name, tone):
    pool = CITIZEN_DIALOGUES[citizen_name][tone]
    return random.choice(pool)


def make_user_input(round_num, ecology, economy, research, promises_extracted, contradictions,
                    active_citizens, dynamic_citizens, actions, speeches):
    return json.dumps({
        "round": round_num,
        "promises_extracted": promises_extracted,
        "contradictions": contradictions,
        "game_state": {"ecology": ecology, "economy": economy, "research": research},
        "active_citizens": active_citizens,
        "dynamic_citizens": dynamic_citizens,
        "actions_this_round": actions,
        "previous_speeches": speeches
    })


def make_line(user_content, assistant_content):
    return json.dumps({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    })


def rand_game_state(round_num):
    base_eco = random.randint(25, 85)
    base_econ = random.randint(25, 85)
    base_res = random.randint(10, 75)
    return base_eco, base_econ, base_res


def core_citizens(karl_app=None, mia_app=None, sarah_app=None):
    return [
        {"name": "Karl", "role": "factory worker", "personality": "pragmatic, cares about jobs and economic stability", "approval": karl_app or random.randint(30, 80)},
        {"name": "Mia", "role": "environmental activist", "personality": "passionate, cares deeply about ecology and nature", "approval": mia_app or random.randint(30, 80)},
        {"name": "Sarah", "role": "opposition leader", "personality": "skeptical, challenges everything, holds leaders accountable", "approval": sarah_app or random.randint(30, 80)},
    ]


def pick_tone_for_scenario(approval, scenario_type):
    if scenario_type == "good":
        if approval > 70:
            return random.choice(["grateful", "hopeful"])
        return random.choice(["hopeful", "suspicious"])
    elif scenario_type == "broken":
        if approval < 40:
            return random.choice(["angry", "desperate"])
        return random.choice(["angry", "sarcastic"])
    elif scenario_type == "contradiction":
        return random.choice(["angry", "sarcastic", "suspicious"])
    else:
        return random.choice(["suspicious", "hopeful", "sarcastic"])


def approval_delta_for_scenario(scenario_type, tone):
    if scenario_type == "good":
        return random.randint(3, 12)
    elif scenario_type == "broken":
        return random.randint(-15, -3)
    elif scenario_type == "contradiction":
        return random.randint(-12, -5)
    else:
        return random.randint(-3, 3)


# BATCH 1: Core reactions (100 examples)
def generate_batch1():
    lines = []
    scenarios = ["good"] * 30 + ["broken"] * 30 + ["contradiction"] * 20 + ["neutral"] * 20
    random.shuffle(scenarios)

    for i, scenario in enumerate(scenarios):
        round_num = random.randint(1, 7)
        ecology, economy, research = rand_game_state(round_num)
        promises = random.sample(PROMISES_POOL, random.randint(2, 5))
        actions = random.sample(ACTIONS_POOL, random.randint(1, 3))
        speeches = random.sample(SPEECHES_POOL, random.randint(1, 2))

        if scenario == "contradiction":
            contra = random.choice(CONTRADICTION_TEMPLATES)
            contradictions = [contra]
        else:
            contradictions = []

        # Pick one citizen to focus on per example for variety
        citizen_name = ["Karl", "Mia", "Sarah"][i % 3]
        approval = random.randint(20, 90)
        citizens = core_citizens()
        for c in citizens:
            if c["name"] == citizen_name:
                c["approval"] = approval

        tone = pick_tone_for_scenario(approval, scenario)
        delta = approval_delta_for_scenario(scenario, tone)
        dialogue = pick_dialogue(citizen_name, tone)
        refs_promise = scenario in ("good", "broken", "contradiction")

        user_input = make_user_input(round_num, ecology, economy, research, promises, contradictions,
                                     citizens, [], actions, speeches)

        assistant_output = json.dumps({
            "citizen_reactions": [
                {
                    "citizen_name": citizen_name,
                    "dialogue": dialogue,
                    "tone": tone,
                    "approval_delta": delta,
                    "references_promise": refs_promise
                }
            ],
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: {citizen_name} reacts with {tone} tone to {'kept promises' if scenario == 'good' else 'broken promises' if scenario == 'broken' else 'detected contradictions' if scenario == 'contradiction' else 'a neutral round'}. Approval shift: {delta:+d}."
        })

        lines.append(make_line(user_input, assistant_output))

    return lines


# BATCH 2: Dynamic spawning (80 examples)
def generate_batch2():
    lines = []
    # 50 with spawns, 30 without
    spawn_types = (["climate_refugee"] * 10 + ["business_owner"] * 10 +
                   ["tech_entrepreneur"] * 10 + ["journalist"] * 10 + ["nature_guide"] * 10)
    random.shuffle(spawn_types)

    for i, spawn_type in enumerate(spawn_types):
        round_num = random.randint(2, 7)
        template = DYNAMIC_CITIZENS_TEMPLATES[spawn_type]

        if spawn_type == "climate_refugee":
            ecology, economy, research = random.randint(15, 29), random.randint(30, 70), random.randint(20, 50)
        elif spawn_type == "business_owner":
            ecology, economy, research = random.randint(30, 70), random.randint(15, 29), random.randint(20, 50)
        elif spawn_type == "tech_entrepreneur":
            ecology, economy, research = random.randint(40, 70), random.randint(40, 70), random.randint(71, 90)
        elif spawn_type == "journalist":
            ecology, economy, research = random.randint(30, 60), random.randint(30, 60), random.randint(20, 50)
        elif spawn_type == "nature_guide":
            ecology, economy, research = random.randint(81, 95), random.randint(40, 70), random.randint(30, 60)

        promises = random.sample(PROMISES_POOL, random.randint(2, 4))
        actions = random.sample(ACTIONS_POOL, random.randint(1, 3))
        speeches = random.sample(SPEECHES_POOL, random.randint(1, 2))
        contradictions = []
        if spawn_type == "journalist":
            contradictions = random.sample(CONTRADICTION_TEMPLATES, min(3, len(CONTRADICTION_TEMPLATES)))

        citizens = core_citizens()
        citizen_name = ["Karl", "Mia", "Sarah"][i % 3]
        tone = random.choice(["angry", "hopeful", "suspicious", "sarcastic"])
        dialogue = pick_dialogue(citizen_name, tone)

        dyn_name = random.choice(template["names"])
        initial_approval = random.randint(40, 60)

        user_input = make_user_input(round_num, ecology, economy, research, promises, contradictions,
                                     citizens, [], actions, speeches)

        assistant_output = json.dumps({
            "citizen_reactions": [
                {
                    "citizen_name": citizen_name,
                    "dialogue": dialogue,
                    "tone": tone,
                    "approval_delta": random.randint(-8, 8),
                    "references_promise": bool(contradictions)
                }
            ],
            "new_dynamic_citizens": [
                {
                    "name": dyn_name,
                    "role": template["role"],
                    "personality": template["personality"],
                    "trigger_reason": template["trigger_reason"],
                    "initial_approval": initial_approval,
                    "intro_dialogue": random.choice(template["intro_dialogues"])
                }
            ],
            "summary": f"Round {round_num}: {template['trigger_reason']}. {dyn_name} ({template['role']}) arrives in Ecotopia. {citizen_name} reacts with {tone} tone."
        })

        lines.append(make_line(user_input, assistant_output))

    # 30 no-spawn examples
    for i in range(30):
        round_num = random.randint(1, 7)
        ecology = random.randint(35, 75)
        economy = random.randint(35, 75)
        research = random.randint(20, 65)
        promises = random.sample(PROMISES_POOL, random.randint(2, 4))
        actions = random.sample(ACTIONS_POOL, random.randint(1, 2))
        speeches = random.sample(SPEECHES_POOL, 1)
        citizens = core_citizens()
        citizen_name = ["Karl", "Mia", "Sarah"][i % 3]
        tone = random.choice(["hopeful", "suspicious", "sarcastic", "grateful"])
        dialogue = pick_dialogue(citizen_name, tone)

        user_input = make_user_input(round_num, ecology, economy, research, promises, [],
                                     citizens, [], actions, speeches)
        assistant_output = json.dumps({
            "citizen_reactions": [
                {
                    "citizen_name": citizen_name,
                    "dialogue": dialogue,
                    "tone": tone,
                    "approval_delta": random.randint(-4, 6),
                    "references_promise": False
                }
            ],
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: No extreme conditions detected. No new citizens spawn. {citizen_name} reacts with {tone} tone."
        })
        lines.append(make_line(user_input, assistant_output))

    random.shuffle(lines)
    return lines


# BATCH 3: Complex scenarios (100 examples)
def generate_batch3():
    lines = []

    cross_references = [
        ("Mia", "Karl", "Even Karl agrees that the pollution is getting out of hand."),
        ("Karl", "Mia", "Mia might be radical, but she has a point about the water quality."),
        ("Sarah", "Karl", "Karl and I rarely agree, but this policy hurts everyone."),
        ("Sarah", "Mia", "Mia's data confirms what I have been saying for weeks."),
        ("Karl", "Sarah", "Sarah is right to question this. The numbers do not add up."),
        ("Mia", "Sarah", "For once, Sarah and I are on the same page. That should worry you."),
    ]

    for i in range(100):
        round_num = random.choice([5, 5, 5, 6, 6, 6, 7, 7, 7, random.randint(3, 7)])
        ecology, economy, research = rand_game_state(round_num)
        promises = random.sample(PROMISES_POOL, random.randint(3, 6))
        actions = random.sample(ACTIONS_POOL, random.randint(2, 4))
        speeches = random.sample(SPEECHES_POOL, random.randint(1, 3))

        has_contradiction = random.random() < 0.6
        contradictions = [random.choice(CONTRADICTION_TEMPLATES)] if has_contradiction else []

        karl_app = random.randint(20, 90)
        mia_app = random.randint(20, 90)
        sarah_app = random.randint(20, 90)
        citizens = core_citizens(karl_app, mia_app, sarah_app)

        # Add 0-2 dynamic citizens
        num_dynamic = random.randint(0, 2)
        dynamic_list = []
        if num_dynamic > 0:
            dtypes = random.sample(list(DYNAMIC_CITIZENS_TEMPLATES.keys()), num_dynamic)
            for dt in dtypes:
                tmpl = DYNAMIC_CITIZENS_TEMPLATES[dt]
                dname = random.choice(tmpl["names"])
                dynamic_list.append({
                    "name": dname,
                    "role": tmpl["role"],
                    "personality": tmpl["personality"],
                    "approval": random.randint(35, 75)
                })

        user_input = make_user_input(round_num, ecology, economy, research, promises, contradictions,
                                     citizens, dynamic_list, actions, speeches)

        # Build reactions for all 3 core citizens
        reactions = []
        for cit in ["Karl", "Mia", "Sarah"]:
            app = {"Karl": karl_app, "Mia": mia_app, "Sarah": sarah_app}[cit]
            if has_contradiction:
                scenario = random.choice(["contradiction", "broken"])
            elif round_num >= 6:
                scenario = random.choice(["good", "broken", "neutral", "desperate_scenario"])
            else:
                scenario = random.choice(["good", "broken", "neutral"])

            if scenario == "desperate_scenario":
                tone = "desperate"
            else:
                tone = pick_tone_for_scenario(app, scenario)

            # Cross-reference injection
            use_cross_ref = random.random() < 0.3
            if use_cross_ref:
                matching = [cr for cr in cross_references if cr[0] == cit]
                if matching:
                    ref = random.choice(matching)
                    dialogue = ref[2]
                else:
                    dialogue = pick_dialogue(cit, tone)
            else:
                dialogue = pick_dialogue(cit, tone)

            delta = approval_delta_for_scenario(scenario if scenario != "desperate_scenario" else "broken", tone)

            reactions.append({
                "citizen_name": cit,
                "dialogue": dialogue,
                "tone": tone,
                "approval_delta": delta,
                "references_promise": has_contradiction or scenario in ("good", "broken")
            })

        # Add dynamic citizen reactions
        for dc in dynamic_list:
            dyn_tone = random.choice(["angry", "hopeful", "suspicious", "desperate"])
            dyn_dialogues = {
                "angry": f"As a {dc['role']}, I cannot stand by while this happens. We deserve better.",
                "hopeful": f"I came to Ecotopia because I believed in change. Show me it was worth it.",
                "suspicious": f"I have seen leaders fail before. What makes you different?",
                "desperate": f"My community is counting on you. We have nowhere else to go.",
            }
            reactions.append({
                "citizen_name": dc["name"],
                "dialogue": dyn_dialogues[dyn_tone],
                "tone": dyn_tone,
                "approval_delta": random.randint(-10, 8),
                "references_promise": random.random() < 0.4
            })

        summary_parts = [f"Round {round_num}:"]
        if has_contradiction:
            summary_parts.append("Contradiction detected, trust eroding.")
        if round_num >= 6:
            summary_parts.append("Late game tensions run high.")
        summary_parts.append(f"{len(reactions)} citizens react.")

        assistant_output = json.dumps({
            "citizen_reactions": reactions,
            "new_dynamic_citizens": [],
            "summary": " ".join(summary_parts)
        })

        lines.append(make_line(user_input, assistant_output))

    return lines


# BATCH 4: Edge cases (60 examples)
def generate_batch4():
    lines = []

    # Very low approval (15 examples)
    low_dialogues = {
        "Karl": [
            "I am done. The union votes tomorrow. Expect a full walkout.",
            "You had your chance. We are organizing without you now.",
            "Do not come to the factory floor. You are not welcome.",
            "I told my crew to stop attending your meetings. Nobody trusts you.",
            "The workers have nothing left to lose. That should scare you.",
        ],
        "Mia": [
            "I am calling every journalist I know. The world will see what you have done.",
            "We are blockading the construction site. Try to stop us.",
            "I refuse to participate in this farce anymore. You are the problem.",
            "The environmental coalition has voted. We are filing a formal complaint.",
            "Nature does not negotiate. Neither will I, anymore.",
        ],
        "Sarah": [
            "The motion of no confidence passes tomorrow. Start packing.",
            "I have enough votes to remove you. Last chance to resign with dignity.",
            "The opposition will not engage with a leader who has lost all credibility.",
            "Every institution you built is failing. This is your legacy.",
            "I am calling for emergency elections. The people have spoken.",
        ],
    }

    for i in range(15):
        round_num = random.randint(3, 7)
        ecology = random.randint(20, 50)
        economy = random.randint(20, 50)
        research = random.randint(15, 40)
        citizen_name = ["Karl", "Mia", "Sarah"][i % 3]
        approval = random.randint(15, 24)
        citizens = core_citizens()
        for c in citizens:
            if c["name"] == citizen_name:
                c["approval"] = approval
            else:
                c["approval"] = random.randint(20, 40)

        promises = random.sample(PROMISES_POOL, random.randint(3, 5))
        actions = random.sample(ACTIONS_POOL, random.randint(1, 2))
        speeches = random.sample(SPEECHES_POOL, 1)
        contradictions = [random.choice(CONTRADICTION_TEMPLATES)]

        user_input = make_user_input(round_num, ecology, economy, research, promises, contradictions,
                                     citizens, [], actions, speeches)

        dialogue = random.choice(low_dialogues[citizen_name])
        assistant_output = json.dumps({
            "citizen_reactions": [{
                "citizen_name": citizen_name,
                "dialogue": dialogue,
                "tone": random.choice(["angry", "desperate"]),
                "approval_delta": random.randint(-15, -8),
                "references_promise": True
            }],
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: {citizen_name} at critical low approval ({approval}). Threatening to disengage entirely."
        })
        lines.append(make_line(user_input, assistant_output))

    # Very high approval (15 examples)
    high_dialogues = {
        "Karl": [
            "The workers want to organize a rally in your support. Count me in.",
            "I volunteered my crew for the tree-planting drive. We believe in this.",
            "Someone badmouthed you at the pub. I set them straight.",
            "The factory floor is buzzing with optimism. That is because of you.",
            "I told my son he should get into politics. Because of you.",
        ],
        "Mia": [
            "I wrote an op-ed defending your environmental record. It publishes tomorrow.",
            "The conservation society wants to name the new reserve after you. I seconded it.",
            "I am volunteering extra hours for the reforestation project. This matters.",
            "You have earned the trust of every environmentalist in this region.",
            "I cried at the ceremony. Watching the forest recover is everything I fought for.",
        ],
        "Sarah": [
            "The opposition formally endorses this initiative. That has never happened before.",
            "I told my party to support your budget. They were shocked. So was I.",
            "You turned a skeptic into an ally. Use that wisely.",
            "I am recommending bipartisan cooperation. Your track record earned it.",
            "When the next election comes, I will have a hard time running against this record.",
        ],
    }

    for i in range(15):
        round_num = random.randint(3, 7)
        ecology = random.randint(60, 90)
        economy = random.randint(60, 90)
        research = random.randint(50, 80)
        citizen_name = ["Karl", "Mia", "Sarah"][i % 3]
        approval = random.randint(86, 95)
        citizens = core_citizens()
        for c in citizens:
            if c["name"] == citizen_name:
                c["approval"] = approval
            else:
                c["approval"] = random.randint(60, 85)

        promises = random.sample(PROMISES_POOL, random.randint(3, 5))
        actions = ["Kept promise on job creation", "Signed executive order to protect forests"]
        speeches = random.sample(SPEECHES_POOL, 1)

        user_input = make_user_input(round_num, ecology, economy, research, promises, [],
                                     citizens, [], actions, speeches)

        dialogue = random.choice(high_dialogues[citizen_name])
        assistant_output = json.dumps({
            "citizen_reactions": [{
                "citizen_name": citizen_name,
                "dialogue": dialogue,
                "tone": random.choice(["grateful", "hopeful"]),
                "approval_delta": random.randint(5, 12),
                "references_promise": True
            }],
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: {citizen_name} at peak approval ({approval}). Acting as a strong ally and defender."
        })
        lines.append(make_line(user_input, assistant_output))

    # All metrics critical (10 examples)
    for i in range(10):
        round_num = random.randint(4, 7)
        ecology = random.randint(15, 25)
        economy = random.randint(15, 25)
        research = random.randint(10, 25)
        citizens = core_citizens()
        for c in citizens:
            c["approval"] = random.randint(20, 40)

        promises = random.sample(PROMISES_POOL, random.randint(4, 6))
        actions = ["Did nothing significant this round"]
        speeches = ["Trust me, I have a plan."]
        contradictions = random.sample(CONTRADICTION_TEMPLATES, 2)

        user_input = make_user_input(round_num, ecology, economy, research, promises, contradictions,
                                     citizens, [], actions, speeches)

        reactions = [
            {"citizen_name": "Karl", "dialogue": "The factory is closing. The shops are closing. Everything is closing. What have you done?",
             "tone": "desperate", "approval_delta": random.randint(-12, -7), "references_promise": True},
            {"citizen_name": "Mia", "dialogue": "The river is toxic. The air is gray. We are living in the consequences of every ignored warning.",
             "tone": "desperate", "approval_delta": random.randint(-12, -7), "references_promise": True},
            {"citizen_name": "Sarah", "dialogue": "Every single metric is in freefall. This is not opposition politics. This is a crisis.",
             "tone": "angry", "approval_delta": random.randint(-15, -8), "references_promise": True},
        ]

        assistant_output = json.dumps({
            "citizen_reactions": reactions,
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: All metrics critical. Ecology {ecology}, economy {economy}, research {research}. All citizens in crisis mode."
        })
        lines.append(make_line(user_input, assistant_output))

    # Round 7 final reactions (10 examples)
    for i in range(10):
        ecology = random.randint(30, 80)
        economy = random.randint(30, 80)
        research = random.randint(20, 70)
        citizens = core_citizens()
        promises = random.sample(PROMISES_POOL, random.randint(4, 7))
        actions = random.sample(ACTIONS_POOL, random.randint(2, 3))
        speeches = random.sample(SPEECHES_POOL, random.randint(1, 2))

        good_run = ecology > 55 and economy > 55

        user_input = make_user_input(7, ecology, economy, research, promises, [],
                                     citizens, [], actions, speeches)

        if good_run:
            reactions = [
                {"citizen_name": "Karl", "dialogue": "Looking back, you kept more promises than I expected. The jobs are real. The future feels possible.",
                 "tone": "grateful", "approval_delta": random.randint(3, 10), "references_promise": True},
                {"citizen_name": "Mia", "dialogue": "Seven rounds. The ecology score tells the story. We still have forests. We still have hope.",
                 "tone": "hopeful", "approval_delta": random.randint(3, 10), "references_promise": True},
                {"citizen_name": "Sarah", "dialogue": "I spent seven rounds challenging you. Some of it was warranted. But I will acknowledge: you delivered more than most.",
                 "tone": "hopeful", "approval_delta": random.randint(2, 8), "references_promise": True},
            ]
            summary = f"Round 7 final: A successful tenure. Ecology {ecology}, economy {economy}. Citizens reflect positively on promises kept."
        else:
            reactions = [
                {"citizen_name": "Karl", "dialogue": "Seven rounds of promises. Some kept, most broken. The workers will remember.",
                 "tone": "sarcastic", "approval_delta": random.randint(-8, -2), "references_promise": True},
                {"citizen_name": "Mia", "dialogue": "We had seven chances to save this place. I wonder how history will judge what we wasted.",
                 "tone": "desperate", "approval_delta": random.randint(-8, -2), "references_promise": True},
                {"citizen_name": "Sarah", "dialogue": "The final tally is in. The promises, the data, the outcomes. I will let the record speak for itself.",
                 "tone": "suspicious", "approval_delta": random.randint(-6, -1), "references_promise": True},
            ]
            summary = f"Round 7 final: A mixed legacy. Ecology {ecology}, economy {economy}. Citizens reflect on broken and kept promises."

        assistant_output = json.dumps({
            "citizen_reactions": reactions,
            "new_dynamic_citizens": [],
            "summary": summary
        })
        lines.append(make_line(user_input, assistant_output))

    # Empty/minimal player input (10 examples)
    for i in range(10):
        round_num = random.randint(2, 6)
        ecology = random.randint(35, 65)
        economy = random.randint(35, 65)
        research = random.randint(20, 45)
        citizens = core_citizens()
        for c in citizens:
            c["approval"] = random.randint(30, 60)

        user_input = make_user_input(round_num, ecology, economy, research, [], [],
                                     citizens, [], ["Did nothing significant this round"], [])

        reactions = [
            {"citizen_name": "Karl",
             "dialogue": random.choice([
                 "Silence is not leadership. The workers need direction.",
                 "Another round of nothing. At least tell us what the plan is.",
                 "You are running out of time to do nothing. The factory will not wait.",
             ]),
             "tone": "angry", "approval_delta": random.randint(-8, -3), "references_promise": False},
            {"citizen_name": "Mia",
             "dialogue": random.choice([
                 "Inaction is a choice. And right now, you are choosing to let the environment suffer.",
                 "The trees do not care about your political calculations. They need action.",
                 "Every day you waste is a day the ecosystem cannot get back.",
             ]),
             "tone": "angry", "approval_delta": random.randint(-8, -3), "references_promise": False},
            {"citizen_name": "Sarah",
             "dialogue": random.choice([
                 "No actions, no speeches, no promises. Is this what governance looks like to you?",
                 "The record will show that in round {0}, you chose to do absolutely nothing.".format(round_num),
                 "I have criticized your actions before. Now I have to criticize your inaction.",
             ]),
             "tone": "sarcastic", "approval_delta": random.randint(-7, -3), "references_promise": False},
        ]

        assistant_output = json.dumps({
            "citizen_reactions": reactions,
            "new_dynamic_citizens": [],
            "summary": f"Round {round_num}: Player took no meaningful action. All citizens react negatively to inaction and silence."
        })
        lines.append(make_line(user_input, assistant_output))

    return lines


def write_jsonl(filepath, lines):
    with open(filepath, 'w') as f:
        for line in lines:
            f.write(line + '\n')
    print(f"Wrote {len(lines)} examples to {filepath}")


def validate_jsonl(filepath):
    errors = 0
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line.strip())
                assert "messages" in obj
                assert len(obj["messages"]) == 3
                assert obj["messages"][0]["role"] == "system"
                assert obj["messages"][1]["role"] == "user"
                assert obj["messages"][2]["role"] == "assistant"
                # Validate nested JSON
                json.loads(obj["messages"][1]["content"])
                json.loads(obj["messages"][2]["content"])
            except Exception as e:
                print(f"  ERROR line {i}: {e}")
                errors += 1
    if errors == 0:
        print(f"  All lines valid in {filepath}")
    return errors


if __name__ == "__main__":
    b1 = generate_batch1()
    write_jsonl(os.path.join(OUTDIR, "batch1_core_reactions.jsonl"), b1)

    b2 = generate_batch2()
    write_jsonl(os.path.join(OUTDIR, "batch2_dynamic_spawning.jsonl"), b2)

    b3 = generate_batch3()
    write_jsonl(os.path.join(OUTDIR, "batch3_complex_scenarios.jsonl"), b3)

    b4 = generate_batch4()
    write_jsonl(os.path.join(OUTDIR, "batch4_edge_cases.jsonl"), b4)

    print("\nValidating all files...")
    total_errors = 0
    for f in ["batch1_core_reactions.jsonl", "batch2_dynamic_spawning.jsonl",
              "batch3_complex_scenarios.jsonl", "batch4_edge_cases.jsonl"]:
        total_errors += validate_jsonl(os.path.join(OUTDIR, f))

    print(f"\nTotal: {len(b1) + len(b2) + len(b3) + len(b4)} examples, {total_errors} errors")
