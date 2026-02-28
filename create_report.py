"""Create a W&B Report for Ecotopia hackathon submission."""
import wandb
import wandb.apis.reports as wr

report = wr.Report(
    project="hackathon-london-nolan-2026",
    entity="nolancacheux",
    title="Ecotopia: Fine-Tuning Mistral for Political Simulation",
    description="Hackathon submission - Mistral Worldwide Hackathon London 2026",
)

report.blocks = [
    wr.H1("Ecotopia: Fine-Tuning Mistral for Political Simulation"),
    wr.P("Can you save a city on the edge of ecological collapse? Ecotopia is a political simulation game where you play as mayor, making speeches and promises to AI-powered citizens over 7 rounds."),

    wr.H2("Project Overview"),
    wr.P("We fine-tuned 2 specialized LoRA adapters on Ministral 8B using TRL SFT + QLoRA:"),
    wr.UnorderedList(items=[
        "FT-Extract: Promise extraction + contradiction detection from free-text speeches",
        "FT-Citizens: Dynamic citizen dialogue generation + NPC spawning",
    ]),
    wr.P("Total: 540 training examples, trained on HuggingFace Jobs (A10G GPU) for ~$2 total."),

    wr.H2("Training Results"),
    wr.P("Both models trained for 3 epochs with cosine LR schedule and 10% warmup:"),

    wr.PanelGrid(
        panels=[
            wr.LinePlot(x="train/global_step", y=["train/loss"], title="Training Loss"),
            wr.LinePlot(x="train/global_step", y=["train/mean_token_accuracy"], title="Token Accuracy"),
        ],
        runsets=[
            wr.Runset(project="hackathon-london-nolan-2026", entity="nolancacheux"),
        ],
    ),

    wr.H2("Base vs Fine-Tuned Evaluation"),
    wr.P("We evaluated both models on 40 held-out validation examples:"),

    wr.PanelGrid(
        panels=[
            wr.WeavePanelSummaryTable(table_name="eval_results"),
        ],
        runsets=[
            wr.Runset(project="hackathon-london-nolan-2026", entity="nolancacheux"),
        ],
    ),

    wr.H2("Key Findings"),
    wr.OrderedList(items=[
        "Fine-tuning dramatically improves schema conformance: type precision jumps from 10% to 100%",
        "Base model gets the gist right (87.5% promise count) but uses wrong labels",
        "Contradiction detection improves from 82.5% to 100% with fine-tuning",
        "QLoRA (4-bit) + LoRA keeps training cost under $2 total",
        "Specialized small models beat large base models on domain-specific tasks",
    ]),

    wr.H2("Architecture"),
    wr.P("Player Speech → FT-Extract (promise extraction) → FT-Citizens (dialogue generation) → Game State Update → Next Round"),

    wr.H2("Resources"),
    wr.UnorderedList(items=[
        "Extraction Model: https://huggingface.co/mistral-hackaton-2026/ecotopia-extract-ministral-8b",
        "Citizens Model: https://huggingface.co/mistral-hackaton-2026/ecotopia-citizens-ministral-8b",
        "GitHub: https://github.com/KyleKreuter/ecotopia",
    ]),

    wr.H2("Team"),
    wr.P("Nolan Cacheux (Fine-tuning, W&B, Frontend) + Kyle Kreuter (Backend, Spring Boot)"),
]

report.save()
print(f"Report URL: {report.url}")
