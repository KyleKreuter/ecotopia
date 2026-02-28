# Ecotopia - Speaker Notes

Total target: ~5 minutes. Keep it tight. Energy up. Let the demo do the heavy lifting.

## Slide 1: Title (~20s)

Open strong. Don't read the slide.

"Imagine you're the mayor of a city on the brink of ecological collapse. Every decision you make has consequences -- for the environment, the economy, and the people who elected you. That's Ecotopia."

Introduce the team briefly: "I'm Nolan, this is Kyle, and we built this in 24 hours."

## Slide 2: The Problem (~40s)

Set up the tension. Make it relatable.

"Climate policy is hard. Not because we don't know what to do, but because every solution creates tradeoffs. You invest in green energy, the economy takes a hit. You prioritize jobs, emissions go up. And the people you serve? They all react differently to the same policy."

"Politicians promise everything and deliver on nothing. We wanted to build something that forces you to feel those tradeoffs firsthand."

Key point: This is an education problem disguised as a game.

## Slide 3: Our Solution (~40s)

Explain the core mechanic clearly.

"Ecotopia is a political simulation game powered by Mistral AI. You play as the mayor over 7 rounds -- each round represents 5 years."

"The twist: there are no pre-written dialogue options. You write your own speeches in free text. The AI reads your speech, extracts the promises you made, and tracks whether you keep them. Meanwhile, AI-powered citizens react dynamically to your policies -- some love you, some hate you, and they remember what you said."

Pause. Let that sink in. "No two games are ever the same."

## Slide 4: Live Demo (~60s)

THIS IS THE MOST IMPORTANT SLIDE. Practice the demo flow beforehand.

1. Show the game interface briefly
2. Type a short speech (have one prepared, ~2 sentences)
3. Show the promise extraction happening in real-time
4. Point out the citizen reactions updating
5. If time permits, show a contradiction being detected (e.g., promise green energy AND lower taxes)

Tips:
- Have a fallback screenshot ready in case of network issues
- Keep the speech short and punchy for the demo
- Narrate what's happening: "So I just promised to invest in renewable energy. Watch -- the AI extracts that as a promise of type ECOLOGY, and now the environmentalist citizen approves while the business owner is worried about costs."

## Slide 5: Architecture (~30s)

Go fast here. Judges care about the tech but don't belabor it.

"Here's the pipeline. Your speech goes into a fine-tuned Ministral 8B model that extracts structured promises. Those promises feed into a second fine-tuned model that generates citizen reactions. The game state updates accordingly."

"Frontend is React and TypeScript. Backend is Spring Boot. And every single Mistral API call is traced with Weights & Biases Weave -- we can show you the full trace of any game session."

## Slide 6: Fine-Tuning Story (~40s)

This is the technical highlight. Make the numbers land.

"Why did we fine-tune? Because the base Ministral 8B model only gets 10% type precision on promise extraction. Our fine-tuned model gets 100%. That's not a marginal improvement -- that's the difference between a broken game and a working one."

"We hand-crafted 540 training examples, ran SFT with QLoRA at 4-bit quantization on HuggingFace Jobs, and the total training cost was two dollars. Two dollars to go from 10% to 100%."

Let that number breathe. "$2."

## Slide 7: Results (~30s)

Show the comparison table. Let the numbers speak.

"Here's the full comparison. Promise count accuracy: 87.5% base to 100% fine-tuned. Contradiction detection: 82.5% to 100%. Type precision: 10% to 100%."

Drive home the thesis: "Specialized small models beat large base models on domain-specific tasks. You don't need GPT-4 for everything -- you need the right model for the right job."

## Slide 8: W&B Integration (~20s)

Quick but important for the sponsors.

"We tracked everything with Weights & Biases. Training metrics in W&B Models, every inference call traced with Weave, and a full evaluation dashboard comparing base versus fine-tuned performance. We also published a W&B report with all our findings."

If W&B is a sponsor/partner, emphasize: "Weave was essential for debugging our fine-tuned models in production."

## Slide 9: What We Learned (~30s)

Genuine reflections. Be honest.

"Three takeaways. First: fine-tuning is about schema conformance, not intelligence. The base model understood the task -- it just couldn't format the output reliably. Fine-tuning fixed that."

"Second: QLoRA makes 8B models trainable on a single A10G GPU in minutes. The barrier to fine-tuning is gone."

"Third: we hit a wall with La Plateforme's fine-tuning API -- it was blocked during the hackathon. We pivoted to HuggingFace Jobs in 30 minutes and kept going. Hackathon survival skill: always have a Plan B."

## Slide 10: Thank You (~10s)

Short. Confident. Smile.

"Thank you. Links are on screen -- GitHub, HuggingFace, W&B. Come try the game. We'd love your feedback."

Then be ready for questions.

## General Tips

- Practice the demo 3 times before presenting
- Have a backup plan if the API is slow (screenshots, pre-recorded GIF)
- Speak to the audience, not the screen
- If presenting with Kyle, split it: one person does slides 1-5, the other does 6-10
- Keep water nearby
- If a judge asks a question you don't know, say "great question, we haven't explored that yet" -- not a fumbled guess
