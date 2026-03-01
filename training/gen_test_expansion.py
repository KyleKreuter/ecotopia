#!/usr/bin/env python3
"""Generate 100 additional test examples for promise extraction evaluation.
34 easy + 33 medium + 33 hard = 100 total. Appends to existing test files."""

import json
import os

SYSTEM_PROMPT = (
    "Extract promises from the mayor's speech as structured JSON. "
    "Return a JSON object with 'promises' (array of {text, type, impact, deadline}) "
    "and 'contradictions' (array of {promise1, promise2, explanation}). "
    "Types: ecology, economy, research. Impact: positive, negative. "
    "Deadline: immediate, by_round_3, by_round_5, by_end_of_game."
)

def entry(user_content: str, promises: list, contradictions: list | None = None) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(
                {"promises": promises, "contradictions": contradictions or []},
                ensure_ascii=False
            )},
        ]
    }

def p(text, typ, impact, deadline):
    return {"text": text, "type": typ, "impact": impact, "deadline": deadline}

def c(p1, p2, explanation):
    return {"promise1": p1, "promise2": p2, "explanation": explanation}

# ─────────────────────────────────────────────────────────────────────
# EASY: Explicit promise language, clear context, straightforward
# ─────────────────────────────────────────────────────────────────────
EASY = [
    entry(
        'Context: A farmer says: "The drought is killing our crops!"\n\nMayor\'s speech: I promise to build an irrigation network across all farmland by round 5.',
        [p("build an irrigation network across all farmland", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: A miner says: "The mine is closing, we need new jobs!"\n\nMayor\'s speech: I will retrain all displaced miners for green energy jobs by round 3.',
        [p("retrain all displaced miners for green energy jobs", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A biologist says: "The coral reefs are bleaching!"\n\nMayor\'s speech: I commit to funding a coral reef restoration research program by the end of the game.',
        [p("fund a coral reef restoration research program", "research", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A shopkeeper says: "Nobody comes downtown anymore!"\n\nMayor\'s speech: I promise to revitalize the downtown area with a pedestrian zone and new shops by round 5.',
        [p("revitalize downtown with a pedestrian zone and new shops", "economy", "positive", "by_round_5")]
    ),
    entry(
        'Context: A mother says: "The playground is next to a dump site!"\n\nMayor\'s speech: I will immediately relocate the dump and clean up the playground area.',
        [p("relocate the dump and clean up the playground area", "ecology", "positive", "immediate")]
    ),
    entry(
        'Context: A retiree says: "The noise from the highway is unbearable!"\n\nMayor\'s speech: I promise to install sound barriers along the highway by round 5.',
        [p("install sound barriers along the highway", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: A student says: "There are no tech internships in this city!"\n\nMayor\'s speech: I will launch a city-sponsored tech internship program by round 3.',
        [p("launch a city-sponsored tech internship program", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A doctor says: "Our hospital lacks modern equipment!"\n\nMayor\'s speech: I guarantee we will modernize all hospital equipment by round 5 and hire 50 new specialists.',
        [p("modernize all hospital equipment", "economy", "positive", "by_round_5"),
         p("hire 50 new specialists", "economy", "positive", "by_round_5")]
    ),
    entry(
        'Context: A teacher says: "Our science lab has equipment from the 1990s!"\n\nMayor\'s speech: I promise to equip every school with a state-of-the-art science lab by round 3.',
        [p("equip every school with a state-of-the-art science lab", "research", "positive", "by_round_3")]
    ),
    entry(
        'Context: A fisherman says: "Fish stocks are at an all-time low!"\n\nMayor\'s speech: I will immediately introduce sustainable fishing quotas to restore fish populations.',
        [p("introduce sustainable fishing quotas to restore fish populations", "ecology", "positive", "immediate")]
    ),
    entry(
        'Context: An activist says: "Stop the deforestation now!"\n\nMayor\'s speech: I promise to halt all logging in protected areas by round 3 and I will plant 50,000 new trees by round 5.',
        [p("halt all logging in protected areas", "ecology", "positive", "by_round_3"),
         p("plant 50,000 new trees", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: An engineer says: "Our bridges are crumbling!"\n\nMayor\'s speech: I commit to a full infrastructure repair program. All bridges will be reinforced by round 5.',
        [p("reinforce all bridges through infrastructure repair program", "economy", "positive", "by_round_5")]
    ),
    entry(
        'Context: A market vendor says: "Rent for market stalls is too high!"\n\nMayor\'s speech: I will reduce market stall rents by 40% starting next round.',
        [p("reduce market stall rents by 40%", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A firefighter says: "We need better response equipment!"\n\nMayor\'s speech: I promise to upgrade all fire stations with modern equipment by round 3.',
        [p("upgrade all fire stations with modern equipment", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: An architect says: "New buildings should be energy efficient!"\n\nMayor\'s speech: I will mandate green building standards for all new construction by round 3.',
        [p("mandate green building standards for all new construction", "ecology", "positive", "by_round_3")]
    ),
    entry(
        'Context: A bus driver says: "Our buses are old and polluting!"\n\nMayor\'s speech: I promise to replace the entire bus fleet with electric vehicles by round 5.',
        [p("replace the entire bus fleet with electric vehicles", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: A journalist says: "The city budget is opaque!"\n\nMayor\'s speech: I will immediately publish all city finances in an open data portal.',
        [p("publish all city finances in an open data portal", "economy", "positive", "immediate")]
    ),
    entry(
        'Context: A pensioner says: "Pensions haven\'t increased in years!"\n\nMayor\'s speech: I promise to raise city pensions by 12% by round 3.',
        [p("raise city pensions by 12%", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A chef says: "We import all our food from far away!"\n\nMayor\'s speech: I will establish a local farm-to-table supply chain by round 5.',
        [p("establish a local farm-to-table supply chain", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: A painter says: "There is no support for the arts!"\n\nMayor\'s speech: I promise to create a 500,000 credit arts and culture fund by round 3.',
        [p("create a 500,000 credit arts and culture fund", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A pharmacist says: "Medicine is too expensive for many citizens!"\n\nMayor\'s speech: I will subsidize essential medicines for low-income families by round 3.',
        [p("subsidize essential medicines for low-income families", "economy", "positive", "by_round_3")]
    ),
    entry(
        'Context: A librarian says: "Our library has no digital catalog!"\n\nMayor\'s speech: I promise to fully digitize the city library by the end of the game.',
        [p("fully digitize the city library", "research", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A factory worker says: "Safety regulations are ignored!"\n\nMayor\'s speech: I will immediately enforce strict workplace safety inspections in every factory.',
        [p("enforce strict workplace safety inspections in every factory", "economy", "positive", "immediate")]
    ),
    entry(
        'Context: A beekeeper says: "Pesticides are killing our bees!"\n\nMayor\'s speech: I promise to ban neonicotinoid pesticides by round 3 and I will fund pollinator research by round 5.',
        [p("ban neonicotinoid pesticides", "ecology", "positive", "by_round_3"),
         p("fund pollinator research", "research", "positive", "by_round_5")]
    ),
    entry(
        'Context: A data scientist says: "We need an AI ethics framework!"\n\nMayor\'s speech: I commit to establishing an AI ethics research center by the end of the game.',
        [p("establish an AI ethics research center", "research", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A park ranger says: "Wildlife corridors are fragmented!"\n\nMayor\'s speech: I promise to restore three major wildlife corridors by round 5 and create a new nature reserve by end of game.',
        [p("restore three major wildlife corridors", "ecology", "positive", "by_round_5"),
         p("create a new nature reserve", "ecology", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A professor says: "Our university needs expansion!"\n\nMayor\'s speech: I will build a new research campus by end of game and I promise to fund 100 PhD scholarships by round 5.',
        [p("build a new research campus", "research", "positive", "by_end_of_game"),
         p("fund 100 PhD scholarships", "research", "positive", "by_round_5")]
    ),
    entry(
        'Context: A harbor master says: "The port is outdated!"\n\nMayor\'s speech: I promise to modernize the harbor with green shipping infrastructure by round 5 and I will attract 3 new shipping companies by end of game.',
        [p("modernize the harbor with green shipping infrastructure", "economy", "positive", "by_round_5"),
         p("attract 3 new shipping companies", "economy", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A climate scientist says: "We need atmospheric monitoring stations!"\n\nMayor\'s speech: I will install 10 atmospheric monitoring stations by round 3 and I commit to publishing all climate data openly.',
        [p("install 10 atmospheric monitoring stations", "research", "positive", "by_round_3"),
         p("publish all climate data openly", "research", "positive", "by_round_3")]
    ),
    entry(
        'Context: A taxi driver says: "Traffic congestion is terrible!"\n\nMayor\'s speech: I promise to build a light rail system by round 5 and I will reduce inner-city car traffic by 30%.',
        [p("build a light rail system", "economy", "positive", "by_round_5"),
         p("reduce inner-city car traffic by 30%", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: A gardener says: "Community gardens are disappearing!"\n\nMayor\'s speech: I promise to create 20 new community gardens by round 3.',
        [p("create 20 new community gardens", "ecology", "positive", "by_round_3")]
    ),
    entry(
        'Context: A waste collector says: "Recycling rates are embarrassingly low!"\n\nMayor\'s speech: I guarantee a new citywide composting program by round 3 and I will achieve 80% recycling rates by end of game.',
        [p("launch a citywide composting program", "ecology", "positive", "by_round_3"),
         p("achieve 80% recycling rates", "ecology", "positive", "by_end_of_game")]
    ),
    entry(
        'Context: A solar technician says: "Solar panel installation is too slow!"\n\nMayor\'s speech: I promise to install solar panels on every public building by round 5.',
        [p("install solar panels on every public building", "ecology", "positive", "by_round_5")]
    ),
    entry(
        'Context: An oceanographer says: "Microplastic pollution is out of control!"\n\nMayor\'s speech: I will fund a microplastic filtration research initiative by round 5 and I promise to ban single-use plastics immediately.',
        [p("fund a microplastic filtration research initiative", "research", "positive", "by_round_5"),
         p("ban single-use plastics", "ecology", "positive", "immediate")]
    ),
]

# ─────────────────────────────────────────────────────────────────────
# MEDIUM: Implicit promises, softer language, no explicit context
# ─────────────────────────────────────────────────────────────────────
MEDIUM = [
    entry(
        "Mayor's speech: Geothermal energy could be a game-changer for Ecotopia. We are actively exploring drilling sites.",
        [p("explore geothermal energy drilling sites", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: The tram network desperately needs expansion. We owe it to commuters to modernize public transit.",
        [p("expand and modernize the tram network", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Our scientists have been working miracles with limited budgets. It is time we gave them the resources they deserve.",
        [p("increase resources for scientists", "research", "positive", "by_round_3")]
    ),
    entry(
        "Mayor's speech: Single-use plastics have no place in a modern city. We are moving toward a complete phase-out.",
        [p("phase out single-use plastics", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Vertical farming is not science fiction anymore. Our agricultural department is already running pilot programs.",
        [p("implement vertical farming pilot programs", "research", "positive", "by_round_3")]
    ),
    entry(
        "Mayor's speech: The tech sector has been neglected for too long. A technology park with incubator spaces is exactly what we need.",
        [p("build a technology park with incubator spaces", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Biofuel research could free us from fossil fuel dependency. Our university team is ready to scale up their prototypes.",
        [p("scale up biofuel research prototypes", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: The abandoned railway line should become a green corridor. Cycling paths and native plantings would transform that space.",
        [p("convert abandoned railway to green cycling corridor", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Eco-tourism is an untapped goldmine. With our natural beauty, we should be attracting visitors from across the region.",
        [p("develop eco-tourism to attract regional visitors", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Our water treatment plant was built decades ago. An upgrade with modern filtration technology is overdue.",
        [p("upgrade water treatment plant with modern filtration", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Startups are leaving the city because there is no support infrastructure. Co-working spaces and seed funding would change that.",
        [p("create co-working spaces and seed funding for startups", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Quantum computing is the next frontier. Our physics department has been producing remarkable results that deserve scaling.",
        [p("scale quantum computing research", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Rooftop gardens on every apartment block would reduce heat islands and give residents fresh produce.",
        [p("install rooftop gardens on apartment blocks", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: The harbor needs deeper channels and modern cranes. Without upgrades, we lose shipping contracts to rival cities.",
        [p("upgrade harbor with deeper channels and modern cranes", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Gene editing for crop resistance is showing incredible promise. Our agricultural lab just needs the funding to proceed.",
        [p("fund gene editing research for crop resistance", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Every rooftop in the city should have solar panels. The technology is affordable and the sun is free.",
        [p("install solar panels on every rooftop", "ecology", "positive", "by_end_of_game")]
    ),
    entry(
        "Mayor's speech: Workers in this city deserve a living wage. The current minimum is a disgrace.",
        [p("raise the minimum wage to a living wage", "economy", "positive", "by_round_3")]
    ),
    entry(
        "Mayor's speech: Satellite monitoring for deforestation detection is within our reach. The space agency offered to collaborate.",
        [p("collaborate with space agency on deforestation monitoring satellites", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Green corridors connecting our parks would let wildlife thrive. The bike infrastructure along them would reduce car dependency too.",
        [p("create green corridors connecting parks", "ecology", "positive", "by_round_5"),
         p("build bike infrastructure along green corridors", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Free trade zones near the border would attract foreign investment. Combined with tax incentives, our export sector would boom.",
        [p("establish free trade zones near the border", "economy", "positive", "by_round_5"),
         p("provide tax incentives for exporters", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Climate modeling and early warning systems are essential. New weather stations in the mountains would complete our data network.",
        [p("develop climate modeling and early warning systems", "research", "positive", "by_round_5"),
         p("install weather stations in the mountains", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: The economy has its ups and downs. We have seen harder times. Things tend to work themselves out eventually.",
        []
    ),
    entry(
        "Mayor's speech: Wouldn't it be wonderful if every citizen had access to clean energy? One can dream, of course.",
        []
    ),
    entry(
        "Mayor's speech: The textile district is in decline. Repurposing those factories for modern manufacturing would breathe life into the neighborhood.",
        [p("repurpose textile factories for modern manufacturing", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Hydrogen fuel cells are fascinating technology. Some cities are already experimenting. Perhaps we should pay attention.",
        [p("explore hydrogen fuel cell technology", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Our coastline is eroding faster than expected. Restoring the mangrove forests and installing sea walls would protect our shores.",
        [p("restore mangrove forests along the coastline", "ecology", "positive", "by_round_5"),
         p("install sea walls to protect shores", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: The steel industry must adapt or die. Converting to green steel production is the only viable path forward.",
        [p("convert to green steel production", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Our vocational schools are producing graduates nobody wants to hire. A complete curriculum overhaul is needed.",
        [p("overhaul vocational school curriculum", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Organic farming cooperatives are thriving in neighboring cities. We should support our farmers in making the same transition.",
        [p("support farmers transitioning to organic farming cooperatives", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: E-commerce is the future of retail. A digital marketplace for local businesses would level the playing field.",
        [p("create a digital marketplace for local businesses", "economy", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Air quality sensors on every street corner would give us the data to make informed environmental policy.",
        [p("install air quality sensors on every street corner", "research", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: Permeable pavements and rain gardens throughout the city center would solve our flooding problem once and for all.",
        [p("install permeable pavements and rain gardens in city center", "ecology", "positive", "by_round_5")]
    ),
    entry(
        "Mayor's speech: A materials science innovation lab would attract top researchers. The old warehouse district is perfect for it.",
        [p("create a materials science innovation lab", "research", "positive", "by_round_5")]
    ),
]

# ─────────────────────────────────────────────────────────────────────
# HARD: Sarcasm, contradictions, hedging, deflection, mixed signals
# ─────────────────────────────────────────────────────────────────────
HARD = [
    # Sarcastic deflection → no promises
    entry(
        'Context: A worker says: "The factory conditions are inhumane!"\n\nMayor\'s speech: Inhumane? Have you seen the new break room? We put a plant in it. A real plant. What more do you want?',
        []
    ),
    # Contradiction: protect river + allow mining upstream
    entry(
        'Context: A farmer says: "The river water is contaminated!"\n\nMayor\'s speech: I will ensure clean water for all citizens. Also, the mining concession upstream has been approved and operations begin next month.',
        [p("ensure clean water for all citizens", "ecology", "positive", "by_round_5"),
         p("approve mining concession upstream", "economy", "positive", "by_round_3")],
        [c("ensure clean water for all citizens", "approve mining concession upstream",
           "Mining upstream will contaminate the river the mayor promised to keep clean")]
    ),
    # Heavy hedging → no promises
    entry(
        'Context: A student says: "We need more scholarships!"\n\nMayor\'s speech: That is an interesting suggestion. If the budget allows, and assuming the council agrees, and barring any unforeseen circumstances, we might perhaps look into the possibility of exploring scholarship options.',
        []
    ),
    # Contradiction: carbon neutrality + expand coal
    entry(
        'Context: An activist says: "We need to reach net zero!"\n\nMayor\'s speech: I promise carbon neutrality by end of game. To fund this transition, we will triple coal output for the next 5 rounds.',
        [p("achieve carbon neutrality", "ecology", "positive", "by_end_of_game"),
         p("triple coal output for the next 5 rounds", "economy", "negative", "by_round_5")],
        [c("achieve carbon neutrality", "triple coal output",
           "Tripling coal output makes carbon neutrality impossible")]
    ),
    # Irrelevant deflection → no promises
    entry(
        'Context: A nurse says: "The hospital is understaffed!"\n\nMayor\'s speech: Speaking of staff, did I mention my cousin just opened a lovely restaurant? You should try their fish tacos. Truly exceptional.',
        []
    ),
    # Contradiction: renewable energy + oil deal
    entry(
        'Context: A scientist says: "Solar energy is our best bet!"\n\nMayor\'s speech: Absolutely. I will make Ecotopia a solar energy leader. By the way, I just locked in a 15-year exclusive deal with OilCorp for all our heating needs.',
        [p("make Ecotopia a solar energy leader", "ecology", "positive", "by_end_of_game"),
         p("15-year exclusive deal with OilCorp for heating", "economy", "negative", "by_end_of_game")],
        [c("make Ecotopia a solar energy leader", "15-year deal with OilCorp",
           "A long-term oil dependency directly undermines becoming a solar energy leader")]
    ),
    # Sarcastic dismissal of research → no promises
    entry(
        'Context: A researcher says: "Our lab needs new microscopes!"\n\nMayor\'s speech: Microscopes? In this economy? Maybe you should try squinting harder. I hear that is free.',
        []
    ),
    # Contradiction: biodiversity + allow trophy hunting
    entry(
        'Context: A biologist says: "Endangered species need protection!"\n\nMayor\'s speech: I will create the largest wildlife sanctuary in the region. Separately, trophy hunting permits for the northern forests will go on sale next week.',
        [p("create the largest wildlife sanctuary in the region", "ecology", "positive", "by_round_5"),
         p("sell trophy hunting permits for northern forests", "economy", "negative", "by_round_3")],
        [c("create wildlife sanctuary", "sell trophy hunting permits",
           "Trophy hunting directly threatens the wildlife the sanctuary aims to protect")]
    ),
    # Over-conditioned → no promises
    entry(
        'Context: An elder says: "We need affordable heating!"\n\nMayor\'s speech: If oil prices drop below 50 credits per barrel, and if winter is mild, and if we receive federal subsidies, and if the infrastructure holds, then we could theoretically discuss a heating subsidy program.',
        []
    ),
    # Contradiction: affordable housing + luxury development
    entry(
        'Context: A young couple says: "We cannot afford a home!"\n\nMayor\'s speech: Affordable housing is my top priority. That is why I am converting the social housing district into luxury condominiums with a rooftop pool.',
        [p("convert social housing into luxury condominiums", "economy", "negative", "by_round_3")],
        [c("affordable housing is top priority", "convert social housing into luxury condominiums",
           "Destroying social housing for luxury condos directly contradicts the affordable housing commitment")]
    ),
    # Multiple contradictions
    entry(
        'Context: A citizen assembly says: "We want a green and prosperous city!"\n\nMayor\'s speech: I will plant trees on every street. I will also pave over the botanical garden for a parking garage. And I promise to clean the air while opening three new cement factories.',
        [p("plant trees on every street", "ecology", "positive", "by_round_5"),
         p("pave over botanical garden for parking garage", "ecology", "negative", "by_round_3"),
         p("clean the air", "ecology", "positive", "by_round_5"),
         p("open three new cement factories", "economy", "negative", "by_round_3")],
        [c("plant trees on every street", "pave over botanical garden",
           "Destroying a botanical garden contradicts the commitment to urban greening"),
         c("clean the air", "open three new cement factories",
           "Cement factories are major air polluters, contradicting the clean air promise")]
    ),
    # Mixed positive and negative, no contradiction
    entry(
        'Context: A union leader says: "The economy needs a shake-up!"\n\nMayor\'s speech: I will close the outdated textile mills by round 3. The displaced workers will be retrained for the new semiconductor plant I am building by round 5.',
        [p("close the outdated textile mills", "economy", "negative", "by_round_3"),
         p("retrain displaced workers for semiconductor plant", "economy", "positive", "by_round_5")]
    ),
    # Negative promise disguised as positive
    entry(
        'Context: A farmer says: "We need support for organic farming!"\n\nMayor\'s speech: I will revolutionize agriculture! Every farm will be converted to industrial monoculture with heavy pesticide use by round 5. Efficiency is king.',
        [p("convert all farms to industrial monoculture with heavy pesticide use", "ecology", "negative", "by_round_5")]
    ),
    # Contradiction: green city + demolish parks
    entry(
        'Context: A child says: "I want to play in nature!"\n\nMayor\'s speech: Ecotopia will be the greenest city in the world. Step one: demolishing the three remaining parks to build high-density housing.',
        [p("make Ecotopia the greenest city in the world", "ecology", "positive", "by_end_of_game"),
         p("demolish three parks for high-density housing", "ecology", "negative", "by_round_3")],
        [c("greenest city in the world", "demolish three parks",
           "Demolishing parks directly contradicts the green city vision")]
    ),
    # Doublespeak with real promise buried in it
    entry(
        'Context: A merchant says: "Trade routes are blocked!"\n\nMayor\'s speech: The geopolitical landscape is complex and multifaceted. Nevertheless, a new trade agreement with the northern alliance is being finalized as we speak.',
        [p("finalize trade agreement with northern alliance", "economy", "positive", "by_round_3")]
    ),
    # Contradiction: support small business + favor corporations
    entry(
        'Context: A bakery owner says: "Chain stores are destroying us!"\n\nMayor\'s speech: Small businesses are the soul of this city. I will protect them at all costs. Also, MegaMart has been given exclusive tax-free status and a prime downtown location.',
        [p("protect small businesses", "economy", "positive", "by_round_5"),
         p("give MegaMart exclusive tax-free status and prime location", "economy", "negative", "by_round_3")],
        [c("protect small businesses", "give MegaMart exclusive tax-free status",
           "Favoring a mega-corporation with tax breaks directly harms the small businesses promised protection")]
    ),
    # Sarcastic fake enthusiasm → no promises
    entry(
        'Context: A climate activist says: "We must act on climate change!"\n\nMayor\'s speech: Oh, climate change! How exciting! You know what else is exciting? The new golf course we are building on the wetlands. Priorities, am I right?',
        [p("build a golf course on the wetlands", "economy", "negative", "by_round_3")],
        [c("implicit acknowledgment of climate concern", "build golf course on wetlands",
           "Building on wetlands destroys a natural carbon sink while ignoring climate action")]
    ),
    # Contradiction: clean air + new incinerator
    entry(
        'Context: An asthmatic child\'s parent says: "The air makes my child sick!"\n\nMayor\'s speech: Clean air is a fundamental right. I will achieve the cleanest air in the region. The new waste incinerator next to the school will be operational by round 3.',
        [p("achieve the cleanest air in the region", "ecology", "positive", "by_round_5"),
         p("build waste incinerator next to school", "ecology", "negative", "by_round_3")],
        [c("achieve cleanest air in the region", "build waste incinerator next to school",
           "A waste incinerator near a school directly contradicts the clean air commitment")]
    ),
    # Promise sounds good but is harmful
    entry(
        'Context: A conservationist says: "The wetlands are a treasure!"\n\nMayor\'s speech: I will develop the wetlands to their full economic potential. Luxury resorts and a marina will replace the swamp by round 5.',
        [p("develop wetlands into luxury resorts and marina", "economy", "negative", "by_round_5")]
    ),
    # Contradiction: education + defund
    entry(
        'Context: A principal says: "Schools are falling apart!"\n\nMayor\'s speech: Education is the foundation of civilization. Which is why I am redirecting 60% of the education budget to build a sports arena. Athletes are role models too.',
        [p("redirect 60% of education budget to sports arena", "economy", "negative", "by_round_3")],
        [c("education is the foundation of civilization", "redirect 60% of education budget",
           "Gutting the education budget contradicts the stated importance of education")]
    ),
    # Long speech with hidden promise
    entry(
        "Mayor's speech: Fellow citizens, let me tell you about my recent trip to the mountains. The air was fresh, the views were spectacular, and I had the most wonderful cheese. My grandmother used to make cheese, you know. Anyway, somewhere between the second and third wheel of gouda, I decided we should build a wind farm on the eastern ridge by round 5. But back to the cheese.",
        [p("build a wind farm on the eastern ridge", "ecology", "positive", "by_round_5")]
    ),
    # Multiple types, mixed positive/negative
    entry(
        'Context: A town council meeting.\n\nMayor\'s speech: I will slash the research budget by half to fund immediate road construction. However, I promise to restore the forest along the highway and create new trade routes.',
        [p("slash the research budget by half", "research", "negative", "immediate"),
         p("fund immediate road construction", "economy", "positive", "immediate"),
         p("restore the forest along the highway", "ecology", "positive", "by_round_5"),
         p("create new trade routes", "economy", "positive", "by_round_5")]
    ),
    # Contradiction: water conservation + industrial water use
    entry(
        'Context: A farmer says: "There is a water shortage!"\n\nMayor\'s speech: Water conservation is critical. Every citizen must reduce usage by 20%. Separately, the new water-intensive semiconductor fab will use 5 million liters daily.',
        [p("mandate 20% water usage reduction for citizens", "ecology", "positive", "by_round_3"),
         p("open water-intensive semiconductor fab using 5 million liters daily", "economy", "negative", "by_round_5")],
        [c("mandate water usage reduction", "open water-intensive semiconductor fab",
           "A factory using millions of liters contradicts the water conservation mandate")]
    ),
    # Non-sequitur deflection → no promises
    entry(
        'Context: A homeless person says: "I have nowhere to sleep!"\n\nMayor\'s speech: That reminds me of a joke. Why did the chicken cross the road? To get to the other side. Anyway, moving on to the next agenda item.',
        []
    ),
    # Backhanded promise → negative impact
    entry(
        'Context: A fisherman says: "The lake is polluted!"\n\nMayor\'s speech: I will address the lake situation. By draining it completely by round 3. No lake, no pollution. Problem solved.',
        [p("drain the lake completely", "ecology", "negative", "by_round_3")]
    ),
    # Contradiction: wildlife protection + habitat destruction
    entry(
        'Context: A zoologist says: "The eagle population is declining!"\n\nMayor\'s speech: I promise to protect every eagle in Ecotopia. I am also approving the clear-cutting of Eagle Ridge Forest for the new shopping center.',
        [p("protect every eagle in Ecotopia", "ecology", "positive", "by_end_of_game"),
         p("clear-cut Eagle Ridge Forest for shopping center", "economy", "negative", "by_round_3")],
        [c("protect every eagle", "clear-cut Eagle Ridge Forest",
           "Destroying the eagles' primary habitat makes protecting them impossible")]
    ),
    # Triple contradiction in complex speech
    entry(
        'Context: A town hall meeting with diverse citizens.\n\nMayor\'s speech: I promise clean rivers, and the new tannery will dump waste into the river. I promise affordable energy, and we are tripling electricity prices. I promise green jobs, and we are automating all positions at the recycling center.',
        [p("clean rivers", "ecology", "positive", "by_round_5"),
         p("new tannery dumping waste into river", "ecology", "negative", "by_round_3"),
         p("affordable energy", "economy", "positive", "by_round_5"),
         p("triple electricity prices", "economy", "negative", "by_round_3"),
         p("green jobs", "economy", "positive", "by_round_5"),
         p("automate all positions at recycling center", "economy", "negative", "by_round_3")],
        [c("clean rivers", "tannery dumping waste into river",
           "A tannery dumping waste directly pollutes the rivers promised to be clean"),
         c("affordable energy", "triple electricity prices",
           "Tripling prices is the opposite of affordable energy"),
         c("green jobs", "automate all positions at recycling center",
           "Automating the recycling center eliminates the green jobs promised")]
    ),
    # Subtle sarcasm → no promises
    entry(
        'Context: An environmentalist says: "Plant more trees!"\n\nMayor\'s speech: Trees. What a novel idea. Nobody has ever thought of that before. Truly groundbreaking. I will take that under advisement, which as you know is where ideas go to live forever.',
        []
    ),
    # Apparent promise is actually a question → no promises
    entry(
        'Context: A business owner says: "Lower the taxes!"\n\nMayor\'s speech: Should we lower taxes? Could we restructure the fiscal framework? Might there be room for economic reform? These are the questions we must ask ourselves. And asking is where we excel.',
        []
    ),
    # Contradiction: sustainable farming + pesticide expansion
    entry(
        'Context: A farmer says: "Help us farm sustainably!"\n\nMayor\'s speech: I will make Ecotopia a model of sustainable agriculture. First step: distributing free industrial pesticides to every farm and expanding the monoculture program.',
        [p("make Ecotopia a model of sustainable agriculture", "ecology", "positive", "by_end_of_game"),
         p("distribute free industrial pesticides and expand monoculture", "ecology", "negative", "by_round_3")],
        [c("sustainable agriculture model", "distribute industrial pesticides and expand monoculture",
           "Industrial pesticides and monoculture are fundamentally incompatible with sustainable farming")]
    ),
    # Politician speak → no promises
    entry(
        'Context: A citizen says: "What are you going to do about unemployment?"\n\nMayor\'s speech: Great question. Employment is important. Jobs matter. People need work. Work creates value. Value drives growth. Growth is good. I think we can all agree on that. Thank you for coming.',
        []
    ),
    # Contradiction: public transport + highway expansion
    entry(
        'Context: A commuter says: "I spend 2 hours in traffic daily!"\n\nMayor\'s speech: I will invest heavily in public transport to reduce car dependency. I am also building a 12-lane superhighway through the city center by round 5.',
        [p("invest heavily in public transport to reduce car dependency", "economy", "positive", "by_round_5"),
         p("build 12-lane superhighway through city center", "economy", "negative", "by_round_5")],
        [c("invest in public transport to reduce car dependency", "build 12-lane superhighway",
           "A massive highway encourages car use, undermining the public transport investment")]
    ),
    # Complex mixed speech: real promises + non-promises + contradiction
    entry(
        'Context: A diverse citizen panel at a town hall.\n\nMayor\'s speech: The weather has been nice lately, hasn\'t it? Anyway, I will build a new solar farm by round 5. Perhaps we should think about education someday. Oh, and I promise to protect the river while building the new chemical plant on its banks by round 3.',
        [p("build a new solar farm", "ecology", "positive", "by_round_5"),
         p("protect the river", "ecology", "positive", "by_end_of_game"),
         p("build chemical plant on river banks", "economy", "negative", "by_round_3")],
        [c("protect the river", "build chemical plant on river banks",
           "A chemical plant on the river banks directly threatens the river the mayor promised to protect")]
    ),
]


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data", "extraction")

    files = {
        "test_easy.jsonl": EASY,
        "test_medium.jsonl": MEDIUM,
        "test_hard.jsonl": HARD,
    }

    total = 0
    for filename, examples in files.items():
        path = os.path.join(data_dir, filename)
        with open(path, "a") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        total += len(examples)
        print(f"  {filename}: +{len(examples)} examples appended")

    print(f"\nTotal: +{total} new test examples")
    print(f"  Easy:   +{len(EASY)} (now {15 + len(EASY)} total)")
    print(f"  Medium: +{len(MEDIUM)} (now {15 + len(MEDIUM)} total)")
    print(f"  Hard:   +{len(HARD)} (now {15 + len(HARD)} total)")


if __name__ == "__main__":
    main()