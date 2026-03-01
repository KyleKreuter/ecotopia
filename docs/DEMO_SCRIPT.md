# Ecotopia Demo Script — 10 Rounds to GOLD

This demo runs entirely in the frontend (no backend needed). All citizen reactions are scripted for a smooth, impressive presentation.

## Setup

```bash
cd frontend
npm run dev
```

Open the browser. The game runs in **Mock API mode** automatically when no backend is detected.

---

## Round 1 — Research Foundation

**Actions:**
1. Click tile **J10** (Wasteland, bottom-right) → **Build Research Center**
2. Click tile **I10** (Wasteland) → **Build Research Center**

**Speech** (type into text field):
> We begin with science. Two research centers will unlock the green technologies we need to transform this city. Knowledge is our greatest resource.

**Expected reactions:** Karl skeptical, Mia supportive, Sarah analytical, Dr. Yuki enthusiastic.

Click **End Round**.

---

## Round 2 — Reforestation

**Actions:**
1. Click tile **A10** (Wasteland, bottom-left) → **Plant Forest**
2. Click tile **B10** (Wasteland) → **Plant Forest**

**Speech:**
> While our researchers work, we restore the land. Every tree we plant is an investment in clean air and a healthier future for all.

**Expected reactions:** Karl pragmatic, Mia delighted, Sarah unimpressed.

Click **End Round**.

---

## Round 3 — Fossil Farewell (Emotional Peak)

**Actions:**
1. Click tile **J1** (Oil Refinery, top-right) → **Replace with Solar**
2. Click tile **I2** (Coal Plant) → **Replace with Solar**

**Speech:**
> Today we say goodbye to fossil fuels. The refinery and coal plant served us once, but the future belongs to clean energy. We will not leave the workers behind.

**Expected reactions:** Karl angry about job losses, Mia celebrates, Oleg appears (bitter), Lena appears (enthusiastic). This is the dramatic high point.

Click **End Round**.

---

## Round 4 — Industrial Conversion

**Actions:**
1. Click tile **H1** (Factory) → **Replace with Solar**
2. Click tile **I1** (Factory) → **Replace with Solar**

**Speech:**
> The transition continues. Every old factory becomes a modern solar field — bringing new jobs and clean energy. The economy will recover, I promise.

**Expected reactions:** Karl worried but understanding, Mia thrilled, Sarah cautious, Oleg seeing hope.

Click **End Round**.

---

## Round 5 — Solar Expansion

**Actions:**
1. Click tile **H2** (Factory) → **Replace with Solar**
2. Click tile **H3** (Wasteland) → **Build Solar**

**Speech:**
> More solar means more jobs and cleaner air. The green economy is not a dream — it is happening right now, right here in our city.

**Expected reactions:** Karl cautiously optimistic (neighbor got hired), Mia encouraged, Sarah noting economic stability, Lena reappears.

Click **End Round**.

---

## Round 6 — Grid Expansion

**Actions:**
1. Click tile **J3** (Wasteland) → **Build Solar**
2. Click tile **A7** (Wasteland) → **Build Solar**

**Speech:**
> Our solar grid stretches across the city. Both ecology and economy are growing together — proof that green policy and prosperity go hand in hand.

**Expected reactions:** Karl impressed, Mia passionate, Sarah giving credit.

Click **End Round**.

---

## Round 7 — Momentum

**Actions:**
1. Click tile **A8** (Wasteland) → **Build Solar**
2. Click tile **A9** (Wasteland) → **Build Solar**

**Speech:**
> The momentum is unstoppable. Every district benefits from clean energy. And our research has unlocked something extraordinary — fusion technology.

**Expected reactions:** Karl enthusiastic, Mia excited, Sarah grudgingly respectful, Lena reappears.

Click **End Round**.

---

## Round 8 — Fusion! (Climax)

**Actions:**
1. Click tile **B9** (Wasteland) → **Build Fusion Reactor**
2. Click tile **F9** (Wasteland) → **Build Fusion Reactor**

**Speech:**
> This is the moment everything changes. Fusion reactors — limitless, clean energy. The economy will soar, and our planet will heal. This is our legacy.

**Expected reactions:** Karl excited, Mia passionate, Sarah amazed, Pavel appears.

Click **End Round**.

---

## Round 9 — Securing Victory

**Actions:**
1. Click tile **H9** (Wasteland) → **Build Fusion Reactor**
2. Click tile **I9** (Wasteland) → **Build Solar**

**Speech:**
> One more fusion reactor seals our energy future. Combined with solar, we have built the greenest, most prosperous city this world has ever seen.

**Expected reactions:** Karl delighted, Mia close to tears, Sarah admitting success, Pavel proud, Lena reappears.

Click **End Round**.

---

## Round 10 — The Final Act

**Actions:**
1. Click tile **C10** (Wasteland) → **Plant Forest**
2. Click tile **D10** (Wasteland) → **Plant Forest**

**Speech:**
> We end where we began — with nature. These forests will stand as a symbol of what we achieved together. From pollution to paradise. Thank you all.

**Expected reactions:** Karl grateful, Mia emotional, Sarah respectful.

Click **End Round** → **GOLD Victory Screen** appears!

---

## Expected Final Stats

| Metric | Target | Expected |
|--------|--------|----------|
| Ecology | >80 | ~91 |
| Economy | >80 | ~88 |
| Research | >75 | ~100 |
| Rank | GOLD | GOLD |

## Troubleshooting

- **Wrong tile type?** The map is fixed — coordinates always have the same tile type at game start.
- **Citizen not appearing?** Duplicate citizens are prevented. If a citizen (e.g., Lena) already exists, they won't spawn again.
- **No reactions?** Make sure to type and submit a speech before ending the round.
- **Economy too low?** Follow the action plan exactly — the order matters for resource calculations.
