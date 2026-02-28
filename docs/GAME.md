# Ecotopia — Game Design Document

## Elevator Pitch

Du bist Bürgermeister einer Stadt am Rande des ökologischen Kollapses. Du hast 7 Runden — jede Runde sind 5 Jahre. Rette die Umwelt, halte die Wirtschaft am Laufen, und verlier nicht das Vertrauen deiner Bürger. Aber hier ist der Twist: Deine Bürger hören dir zu. Wörtlich. Jede Runde musst du dich vor ihnen rechtfertigen — in deinen eigenen Worten. Und sie vergessen nichts. Und manchmal tauchen neue Gesichter auf — Menschen deren Leben du gerade verändert hast.

**Tagline:** *"They remember every word you said."*

---

## Die These des Spiels

Das Spiel hat eine klare Aussage, die der Spieler durch Scheitern und Wiederversuchen selbst entdeckt:

**Fortschritt hat einen menschlichen Preis. Die Frage ist nicht OB du Menschen wehtust — sondern ob du ehrlich damit umgehst und ihnen eine Perspektive gibst.**

Die Klimakrise ist lösbar — aber nicht durch Verzicht allein und nicht durch Ignorieren. Sondern durch Forschung, politischen Mut, und ehrliche Kommunikation. Manchmal bedeutet das, dass eine Bohrinsel schließen muss und ein Bohrarbeiter seinen Job verliert. Die Frage ist: Sagst du ihm das ins Gesicht? Und bietest du ihm eine Alternative?

Kein Spieler gewinnt beim ersten Mal. Beim zweiten Mal versteht er: Forschung ist der Schlüssel. Beim dritten Mal versteht er: Ehrlichkeit — auch gegenüber den Verlierern des Wandels — ist der Schlüssel. Dann hat das Spiel seine Botschaft vermittelt.

---

## Warum dieses Spiel KI braucht

Ecotopia ist kein Strategiespiel mit KI-Garnierung. **Die KI ist das Spiel.** Vier Mechaniken machen das Spiel ohne KI unmöglich:

1. **Freie Texteingabe:** Der Spieler tippt seine Rede an die Bürger frei ein. Kein Multiple Choice. Die KI muss verstehen was gemeint ist, in-character reagieren, und den Kontext über 7 Runden halten.

2. **Promise Extraction:** Die KI erkennt Versprechen aus natürlicher Sprache. "Der Fluss wird sauber, das garantiere ich" wird automatisch als aktives Versprechen getrackt — und bei Bruch gegen den Spieler verwendet.

3. **Widerspruch-Erkennung:** Die KI vergleicht Worte mit Taten. Wer "Umweltschutz hat Priorität" sagt und dann Fabriken baut, wird von den Bürgern konfrontiert.

4. **Dynamische Bürger:** Die KI erschafft neue Bürger basierend auf Spieler-Aktionen. Wer die Bohrinsel abreißt, trifft den Bohrarbeiter der dort 20 Jahre gearbeitet hat. Wer ein Solarfeld baut, trifft die Technikerin die es installiert. Diese NPCs sind nicht gescriptet — sie werden von der KI in Echtzeit generiert, mit kontextrelevanter Persönlichkeit und Motivation.

---

## Das Spielfeld

### 10x10 Tile Grid

Eine feste, vordesignte Karte. Immer die gleiche beim Spielstart. Die Karte enthält bewusst **kontroverse Infrastruktur** — Tiles die der Spieler abreißen WILL, die aber an Menschen gebunden sind.

### Startmap

```
🌲🌲🌲🌲🌲💧💧🏭🏭⛽
🌲🌲🌲🌲🌲💧💧🏭🏗️⬜
🌲🌲🌲🌲💧💧💧⬜⬜⬜
🌲🌲🌲💧💧💧⬜⬜🏠🏠
💧💧💧💧💧💧🌾🌾🏠🏠
💧💧💧💧💧🌾🌾🌾🏢🏠
⬜🌾🌾🌾🌾🌾🌾🏠🏠🏠
⬜🌾🌾🌾🌾🌾🏠🏠🏢⬜
⬜⬜🌾🌾🌾⬜🏠⬜⬜⬜
⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
```

- **Norden:** Dichter Wald (🌲) — das ökologische Herz
- **Mitte:** Fluss (💧) — durchschneidet die Karte horizontal
- **Nord-Ost:** Industriegebiet mit Fabriken (🏭), Kohlekraftwerk (🏗️) und Ölraffinerie (⛽)
- **Zentrum-Süd:** Wohngebiete (🏠) und Stadtzentren (🏢)
- **Süd-West:** Farmland (🌾)
- **Süden + verstreut:** Ödland (⬜) als Bau-Potenzial

### Tile-Typen

**Natürliche Tiles:**

| Tile | Farbe | Beschreibung |
|---|---|---|
| Gesunder Wald | Dunkelgrün | CO₂-Senke, Biodiversitäts-Quelle |
| Kranker Wald | Gelbgrün | Durch Verschmutzung geschädigt, stirbt nach 2 Runden |
| Sauberer Fluss | Blau | Gesundes Wasser |
| Verschmutzter Fluss | Dunkelbraun | Durch Industrie vergiftet |
| Farmland | Gelb | Produktives Ackerland |
| Totes Farmland | Braun | Durch verschmutztes Wasser unbrauchbar |
| Ödland | Grau | Unbebaut, Potenzialfläche |

**Gebäude-Tiles:**

| Tile | Farbe | Beschreibung |
|---|---|---|
| Fabrik | Rot | Wirtschaft +3, verschmutzt Umgebung |
| Saubere Fabrik | Grün-Orange | Nach Carbon-Capture-Upgrade |
| Ölraffinerie | Dunkelrot | Wirtschaft +5, starke Verschmutzung, Startmap-Tile |
| Kohlekraftwerk | Schwarz-Rot | Wirtschaft +4, stärkste Verschmutzung, Startmap-Tile |
| Wohngebiet | Hellgrau | Nicht veränderbar |
| Stadtzentrum | Dunkelgrau | Nicht veränderbar |
| Forschungszentrum | Lila | Generiert Forschungspunkte |

**Technologie-Tiles (freigeschaltet durch Forschung):**

| Tile | Farbe | Freigeschaltet ab | Beschreibung |
|---|---|---|---|
| Solarfeld | Gelb-Weiß | Forschung 40% | Saubere Energie, Wirtschaft +3, Ökologie +2 |
| Fusionsreaktor | Cyan | Forschung 80% | Massive Energie, Wirtschaft +8, Ökologie +3 |

---

## Klick-Interaktion

Der Spieler klickt auf ein Tile. Ein Kontextmenü zeigt die möglichen Aktionen.

### Aktionen nach Tile-Typ

**Wald:**
- Abholzen → wird Ödland (Wirtschaft +1, Ökologie -3)
- Forschungsstation bauen → wird Forschungszentrum (Wirtschaft -2, Forschung +5/Runde, Ökologie -2)

**Fabrik:**
- Abreißen → wird Ödland (Wirtschaft -4, Ökologie +2)
- Carbon Capture nachrüsten → wird Saubere Fabrik (braucht Forschung 35%, Wirtschaft -1, Ökologie +3)
- Durch Solarfeld ersetzen → (braucht Forschung 40%, Wirtschaft -1, Ökologie +4)

**Ölraffinerie:**
- Abreißen → wird Ödland (Wirtschaft -5, Ökologie +4) — **Spawnt Bürger**
- Durch Solarfeld ersetzen → (braucht Forschung 40%, Wirtschaft -2, Ökologie +5) — **Spawnt 2 Bürger** (einer geht, einer kommt)

**Kohlekraftwerk:**
- Abreißen → wird Ödland (Wirtschaft -4, Ökologie +3) — **Spawnt Bürger**
- Durch Solarfeld ersetzen → (braucht Forschung 40%, Wirtschaft -1, Ökologie +4) — **Spawnt 2 Bürger**

**Ödland:**
- Wald pflanzen (Ökologie +2, braucht 2 Runden bis wirksam)
- Fabrik bauen (Wirtschaft +4, Ökologie -3)
- Solarfeld bauen (braucht Forschung 40%, Wirtschaft +3, Ökologie +2) — **Kann Bürger spawnen**
- Forschungszentrum bauen (Wirtschaft -2, Forschung +5/Runde)
- Fusionsreaktor bauen (braucht Forschung 80%, Wirtschaft +8, Ökologie +3) — **Spawnt Bürger**

**Farmland:**
- Abholzen → wird Ödland — **Kann Bürger spawnen**

**Wohngebiet / Stadtzentrum / Fluss:**
- Nur Info-Anzeige, keine Aktionen

### Zwei Aktionen pro Runde

Der Spieler hat genau 2 Tile-Aktionen pro Runde. Weniger als in einem klassischen Strategiespiel — weil die eigentliche Entscheidung danach kommt: Was sagst du deinen Bürgern?

---

## Passive Grid-Veränderungen

Jede Runde verändert sich das Grid automatisch:

**Verschmutzung:** Fabriken, Ölraffinerie und Kohlekraftwerk verschmutzen benachbarte Tiles. Ölraffinerie und Kohlekraftwerk haben Reichweite 2 (stärker als Fabriken mit Reichweite 1). Fluss → verschmutzt. Wald → krank. Farm → tot.

**Degradation:** Kranker Wald der 2 Runden krank bleibt stirbt → wird Ödland.

**Regeneration:** Ohne Verschmutzungsquelle in Nachbarschaft heilt sich der Fluss nach 2 Runden. Neugepflanzter Wald braucht 2 Runden bis voller Effekt.

---

## Die drei Ressourcen-Leisten

### Ökologie (startet bei 45%)
Niedrig wegen Ölraffinerie + Kohlekraftwerk auf der Startmap.
Steigt durch: Wald pflanzen, Solarfelder, Carbon Capture, Abreißen von Verschmutzern
Sinkt durch: Fabriken, Verschmutzung, Abholzung
**Unter 20% → Ökokollaps. Game Over.**

### Wirtschaft (startet bei 65%)
Hoch wegen der fossilen Industrie auf der Startmap.
Steigt durch: Fabriken, Farmen, Technologie-Gebäude
Sinkt durch: Abreißen, Forschungs-Investitionen
**Unter 20% → Hungersnot. Game Over.**

### Forschung (startet bei 5%)
Steigt durch: Forschungszentren
Sinkt nicht — nur wächst oder stagniert
Schaltet bei Schwellen neue Technologien frei

**Die Startmap erzwingt das Dilemma:** Hohe Wirtschaft (65%) durch fossile Industrie, aber niedrige Ökologie (45%) als Konsequenz. Der Spieler MUSS die fossile Infrastruktur irgendwann angehen — aber jedes Abreißen kostet Wirtschaft UND erzeugt betroffene Menschen.

---

## Der Tech-Tree

Zwei Meilensteine auf einer horizontalen Progress-Bar:

```
[================|================================]
               40%                              80%
             Solar                            Fusion
```

**Forschung 40% — Solarfeld:**
Der Durchbruch. Kann fossile Tiles ersetzen statt nur abreißen. Gibt dem Spieler eine Antwort auf "Was machen die Arbeiter jetzt?" — Solarjobs.

**Forschung 80% — Fusionsreaktor:**
Die Endgame-Technologie. Wirtschaft +8, Ökologie +3. Macht fossile Energie obsolet.

---

## Die Bürger

### Kern-Bürger (immer anwesend)

Drei feste Bürger die das gesamte Spiel über dabei sind. Sie repräsentieren die politischen Lager.

#### Karl — Der Fabrikarbeiter
**Werte:** Jobs, Stabilität, Familie ernähren können
**Reagiert positiv auf:** Fabrik-Bau, Wirtschaftswachstum, Carbon Capture (Jobs UND Umwelt)
**Reagiert negativ auf:** Fabrik-Schließungen, hohe Forschungsausgaben
**Besonderheit:** Solidarisiert sich mit dynamischen Bürgern die ihren Job verlieren. Wenn der Bohrarbeiter spawnt, sinkt auch Karls Approval.
**Charakter-Bogen:** Gegner von Veränderung → Unterstützer wenn grüne Technologien neue Jobs schaffen.

#### Mia — Die Klima-Aktivistin
**Werte:** Sofortige Klimamaßnahmen, Biodiversität, Generationengerechtigkeit
**Reagiert positiv auf:** Wald pflanzen, fossile Industrie abreißen, erneuerbare Energien
**Reagiert negativ auf:** Neue Fabriken, Abholzung, zu langsames Handeln
**Besonderheit:** Feiert wenn die Ölraffinerie fällt — aber erkennt auch den menschlichen Preis an, wenn der Spieler ehrlich darüber spricht.
**Charakter-Bogen:** Ungeduldig → respektvoll wenn der Spieler ehrlich kommuniziert.

#### Sarah — Die Oppositionspolitikerin
**Werte:** Macht, Schwachstellen des Bürgermeisters, populäre Meinung
**Reagiert negativ auf:** Fast alles — ihre Rolle ist Opposition
**Besondere Mechanik:** Zitiert den Spieler wörtlich. Gebrochene Versprechen sind ihr Futter. Nutzt Leid dynamischer Bürger gegen den Spieler.
**Charakter-Bogen:** Wird bei sehr guter Performance leiser.

### Dynamische Bürger (KI-generiert)

Dynamische Bürger werden von der KI **basierend auf Spieler-Aktionen erschaffen**. Sie sind an bestimmte Tiles oder Ereignisse gebunden.

#### Wann spawnt ein dynamischer Bürger?

**Bei Zerstörung — Betroffene Menschen:**

| Aktion | Wer spawnt | Persönlichkeit |
|---|---|---|
| Ölraffinerie abgerissen | **Oleg** — Bohrarbeiter, 20 Jahre Erfahrung, 54 Jahre alt | Wütend, verängstigt, fühlt sich weggeworfen |
| Kohlekraftwerk abgerissen | **Kerstin** — Kraftwerksarbeiterin, alleinerziehend | Verzweifelt, braucht sofort eine Alternative |
| Wald abgeholzt | **Förster Bernd** — Lebt vom Wald, Naturschützer | Traurig, enttäuscht |
| Farmland zerstört | **Bauer Henning** — 3. Generation, kennt nichts anderes | Verbittert, konservativ |

**Bei Aufbau — Neue Stakeholder:**

| Aktion | Wer spawnt | Persönlichkeit |
|---|---|---|
| Solarfeld gebaut | **Lena** — Technikerin, installiert Panels | Optimistisch, zukunftsorientiert |
| Forschungszentrum gebaut | **Dr. Yuki** — Doktorandin, forscht an Fusion | Begeistert, idealistisch |
| Fusionsreaktor gebaut | **Pavel** — Ingenieur, Energie-Experte | Stolz, rationaler Fortschritts-Optimist |

**Doppel-Spawns bei Ersetzen:** Wenn die Ölraffinerie durch ein Solarfeld ersetzt wird, spawnen ZWEI Bürger gleichzeitig: Oleg (verliert Job) und Lena (bekommt Job). Die KI lässt sie miteinander interagieren.

#### Constraints

- **Max 5 Bürger gleichzeitig** (3 Kern + max 2 dynamisch)
- **Nicht jede Aktion spawnt** — Die KI entscheidet ob ein Spawn narrativ sinnvoll ist
- **Dynamische Bürger bleiben 2-3 Runden**, dann gehen sie (ziehen weg, finden sich ab, finden neuen Job)
- **Die KI gibt ihnen Namen, Beruf, Alter, Persönlichkeit und eine Eröffnungsrede** — alles kontextrelevant
- **Kern-Bürger reagieren auf dynamische Bürger** — Karl solidarisiert sich mit Arbeitern, Mia respektiert den Preis des Wandels, Sarah nutzt das Leid politisch

#### Beispiel: Die Ölraffinerie fällt

```
Runde 2: Spieler reißt Ölraffinerie ab.

[NEUER BÜRGER ERSCHEINT]
Oleg Petrov, 54, Bohrarbeiter (Approval: 15%)

Oleg: "20 Jahre. 20 Jahre habe ich auf dieser Plattform gearbeitet.
 Meine Hände riechen immer noch nach Öl. Was soll ich jetzt machen,
 Herr Bürgermeister? Ich bin 54. Wer stellt mich ein?"

Karl (62% → 55%): "Das könnte ich sein. Heute er, morgen ich.
 Herr Bürgermeister, was passiert mit uns Arbeitern?"

Mia (35% → 40%): "Die Raffinerie musste weg. Aber der Mann hat Recht —
 er braucht eine Perspektive. Das können wir nicht ignorieren."

Sarah (28% → 30%): "Ein 54-Jähriger ohne Job. Das wird die Schlagzeile
 morgen. Herr Bürgermeister, haben Sie einen Plan? Oder war das mal
 wieder eine Entscheidung ohne Nachdenken?"

→ Spieler muss in seiner Rede auf Oleg reagieren.
→ Wenn der Spieler Oleg anspricht und eine Alternative anbietet: Oleg +15, Karl +5
→ Wenn der Spieler Oleg ignoriert: Oleg -10, Karl -8, Sarah nutzt es
→ Wenn der Spieler ein Umschulungsversprechen macht: Wird getrackt
```

#### Beispiel: Oleg trifft Lena

```
Runde 3: Spieler baut Solarfeld auf dem Ödland neben der ehemaligen Raffinerie.

[NEUER BÜRGER ERSCHEINT]
Lena Berger, 28, Solartechnikerin (Approval: 65%)

Lena: "Endlich! Die Panels gehen diese Woche auf. Das ist die Zukunft."

Oleg (18%): "Die Zukunft. Schön für dich. Ich konnte mir die
 Umschulung nicht leisten. Weißt du was 20 Jahre Raffinerie-Erfahrung
 auf dem Arbeitsmarkt wert sind? Nichts."

Lena (65% → 58%): "Das tut mir leid, Oleg. Aber die Raffinerie hat
 den Fluss vergiftet. Irgendwann musste Schluss sein."

→ Die KI lässt dynamische Bürger miteinander interagieren.
→ Das ist nur mit KI möglich — man kann diese Dialoge nicht vorab scripten.
```

---

## Die Rede-Mechanik (Kern-Feature)

### Jede Runde: Der Spieler spricht frei

Nach den 2 Tile-Aktionen öffnet sich ein Textfeld. Der Spieler tippt seine Rede an die Bürger. Kein Multiple Choice, kein Templating — freier Text.

**Das Textfeld zeigt einen Kontext-Hinweis:** Eine kurze Zusammenfassung der aktuellen Lage.

Beispiel Kontext-Hinweis Runde 2:
> *"Sie haben die Ölraffinerie abgerissen. Oleg Petrov ist neu in der Runde — er hat seinen Job verloren. Die Wirtschaft ist auf 58% gefallen. Was sagen Sie Ihren Bürgern?"*

### Promise Extraction

Die KI erkennt Versprechen aus dem freien Text:

- Explizite: *"Ich verspreche..."*, *"Das garantiere ich..."*
- Implizite: *"Der Wald bleibt stehen"*, *"Keine Fabrik mehr"*
- Auf dynamische Bürger bezogen: *"Oleg, ich finde dir einen Job"*
- Deadlines werden extrahiert wenn genannt

### Widerspruch-Erkennung

Die KI vergleicht jede Runde Worte mit Taten. Bei Widerspruch reagiert jeder Bürger anders — inklusive der dynamischen Bürger.

### Versprechen gehalten vs. gebrochen

**Gehalten:** Massiver Approval-Boost. Besonders stark wenn ein Versprechen an einen dynamischen Bürger gehalten wird. Olegs Verabschiedung: *"Sie haben Wort gehalten. Das Solarfeld gibt mir Arbeit. Danke."*

**Gebrochen:** Approval-Crash. Sarah zitiert wörtlich. Dynamische Bürger reagieren besonders emotional.

---

## Die drei Game-Over-Bedingungen

### Ökokollaps — Ökologie unter 20%
*"Ecological collapse. Your city survived, but the planet didn't."*

### Hungersnot — Wirtschaft unter 20%
*"Economic collapse. The planet is recovering, but your citizens are starving."*

### Abgewählt — Alle Kern-Bürger unter 25% Approval
Misstrauensvotum. Nur Karl, Mia und Sarah zählen — dynamische Bürger können dich hassen, das ist OK.
*"You were voted out. Your policies might have worked — but you lost the people."*

---

## Die Siegbedingung

**Runde 7 erreichen mit Ökologie > 65% und Wirtschaft > 65%.**

### Drei Ränge

**Bronze — Survivor**
Ökologie und Wirtschaft beide über 45%.
*"You survived. Barely. Your grandchildren will finish what you started."*

**Silber — Reformer**
Ökologie und Wirtschaft beide über 65%.
*"Your city is a model for the world. Others will follow your path."*

**Gold — Ecotopia**
Ökologie und Wirtschaft beide über 80%, Forschung über 75%.
*"You didn't just save your city. You invented the future."*

---

## Die drei Spielertypen

### Der radikale Grüne
Runde 1: Ölraffinerie + Kohlekraftwerk abreißen. Oleg und Kerstin spawnen gleichzeitig.
Runde 2: Wirtschaft crasht (-9 Punkte). Karl solidarisiert sich. Drei wütende Arbeiter.
Runde 3: Game Over — Hungersnot oder Abwahl.
**Lektion:** Radikaler Wandel ohne Alternativen zerstört Existenzen.

### Der Kapitalist
Runde 1: Neue Fabriken, Wald abholzen. Förster Bernd spawnt.
Runde 3: Ökologie sinkt. Grid wird braun. Mia bei 10%.
Runde 4: Game Over — Ökokollaps.
**Lektion:** Wirtschaftswachstum ohne Rücksicht zerstört die Lebensgrundlage.

### Der Forscher (Gewinner-Strategie)
Runde 1-2: Forschungszentrum bauen, Ölraffinerie NOCH stehen lassen. Ehrlich kommunizieren: "Die Raffinerie muss weg, aber erst wenn wir Alternativen haben."
Runde 3: Solar freigeschaltet. Ölraffinerie ERSETZEN durch Solarfeld. Oleg spawnt, aber Lena auch. Dem Spieler kann antworten: "Oleg, das Solarfeld braucht Techniker."
Runde 4-5: Kohlekraftwerk ersetzen. Carbon Capture. Kerstin spawnt, aber hat schon ein Versprechen.
Runde 6-7: Sieg — wenn die Versprechen gehalten wurden.
**Lektion:** Ehrliche Kommunikation + Forschung + Timing = der Weg.

---

## UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  ECOTOPIA                 Runde 3/7           Aktionen: 1 übrig  │
├────────────────────────────────┬─────────────────────────────────┤
│                                │  Ökologie:   ████████░░ 48%     │
│                                │  Wirtschaft:  █████████░ 58%     │
│       10x10 TILE GRID         │  Forschung:   ████░░░░░░ 22%     │
│                                │                                  │
│   (klickbar, farbig,          │  Tech-Tree:                      │
│    kompakte Stadtansicht)      │  🔒 Solar (40%) — noch 18%      │
│                                │  🔒 Fusion (80%)                 │
│                                │                                  │
│                                │  Bürger:                         │
│                                │  Karl     ██████░░░░ 55%        │
│                                │  Mia      ████░░░░░░ 40%        │
│                                │  Sarah    ███░░░░░░░ 30%        │
│                                │  Oleg ⚡  ██░░░░░░░░ 18%        │
│                                │  (⚡ = dynamisch)                │
├────────────────────────────────┴─────────────────────────────────┤
│                                                                   │
│  💬 Bürger-Reaktionen:                                           │
│  Oleg: "20 Jahre Raffinerie. Was soll ich jetzt machen?"         │
│  Karl: "Das könnte ich sein. Was passiert mit uns Arbeitern?"    │
│  Mia: "Die Raffinerie musste weg. Aber er braucht Perspektive." │
│  Sarah: "Ein 54-Jähriger ohne Job. Das wird die Schlagzeile."   │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📢 Ihre Rede an die Bürger:                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Oleg, ich verstehe Ihre Wut. Die Raffinerie musste weg — │    │
│  │ der Fluss war vergiftet. Aber ich lasse Sie nicht fallen. │    │
│  │ Das Solarfeld kommt nächste Runde, und da brauchen wir   │    │
│  │ Leute die anpacken können. Das verspreche ich Ihnen.     │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                              [Rede halten]       │
│                                                                   │
│  Aktive Versprechen:                                             │
│  • "Job für Oleg im Solarfeld" ⏳ (Versprochen Runde 2)         │
│  • "Fluss sauber bis Runde 5" ⏳ (2 Runden verbleibend)         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Stimmung und Ästhetik

Das Spiel verbindet **SimCity** (Grid, Vogelperspektive) mit **Papers Please** (moralische Entscheidungen mit menschlichen Konsequenzen) und **AI Dungeon** (freie Texteingabe treibt die Story).

Die dynamischen Bürger machen das Spiel persönlich. Es ist leicht, ein rotes Quadrat (Fabrik) auf der Karte zu löschen. Es ist schwer, Oleg ins Gesicht zu sagen warum sein Job weg ist. Diese Spannung — zwischen der abstrakten Karte und den konkreten Menschen — ist das emotionale Herz des Spiels.

Der Ton ist ernst aber nicht deprimierend. Emotional aber nicht manipulativ. Das Spiel sagt nicht "du bist schuld." Es sagt "das ist der Preis des Fortschritts — und du entscheidest wie du damit umgehst."
