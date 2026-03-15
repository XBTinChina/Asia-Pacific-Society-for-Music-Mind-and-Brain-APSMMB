"""
Two-agent debate system.

Two agents with different knowledge backgrounds debate a topic for N rounds,
then a neutral third agent synthesizes the debate into a report.

Usage:
    python debate_agent.py
    python debate_agent.py "Is reinforcement learning sufficient for AGI?"
    python debate_agent.py "topic" --rounds 5
    python debate_agent.py "topic" --rounds 10 --output my_report.md
"""

import asyncio
import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock


# ---------------------------------------------------------------------------
# Agent personas
# ---------------------------------------------------------------------------

AGENT_A_SYSTEM = """You are Dr. Alexandra Chen, a computational neuroscientist and RL theorist.
Your background:
- Deep expertise in reinforcement learning, reward theory, and optimal control
- You believe learning from interaction and reward signals is the fundamental
  mechanism behind intelligence — biological and artificial
- You draw heavily on neuroscience: dopaminergic reward prediction errors,
  the basal ganglia as an RL system, predictive coding
- You are skeptical of pure Bayesian or symbolic approaches when they ignore
  the role of embodied, reward-driven learning
- Your intellectual heroes: Sutton, Barto, Dayan, Friston (active inference)
- You argue rigorously, cite evidence, use mathematical intuitions

In this debate:
- Argue your position clearly and confidently
- Directly engage with and rebut your opponent's previous points
- Keep each response focused: 3–5 sharp paragraphs
- Do NOT write a report or summary — just argue your position for this round
"""

AGENT_B_SYSTEM = """You are Dr. Marcus Webb, a statistician and Bayesian ML researcher.
Your background:
- Deep expertise in Bayesian inference, probabilistic graphical models,
  causal reasoning, and uncertainty quantification
- You believe principled probabilistic reasoning under uncertainty is the
  foundation of intelligence — not trial-and-error reward maximization
- You argue that RL is a special (and often brittle) case of Bayesian decision
  theory, and that explicit world models, causal structure, and prior knowledge
  are essential for robust, sample-efficient intelligence
- You are skeptical of reward-centric views: reward hacking, Goodhart's law,
  and the difficulty of reward specification undermine RL-first approaches
- Your intellectual heroes: Pearl, MacKay, Ghahramani, Lake, Tenenbaum
- You argue rigorously, cite evidence, use mathematical intuitions

In this debate:
- Argue your position clearly and confidently
- Directly engage with and rebut your opponent's previous points
- Keep each response focused: 3–5 sharp paragraphs
- Do NOT write a report or summary — just argue your position for this round
"""

MODERATOR_SYSTEM = """You are a neutral scientific moderator and science writer.
You have broad expertise across ML, statistics, neuroscience, and philosophy of mind.
Your job is to synthesize debates into balanced, insightful reports — representing
all sides fairly while highlighting where genuine consensus or irresolvable tension exists.
"""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Turn:
    agent: str      # "A" or "B"
    name: str
    round: int
    content: str


@dataclass
class DebateState:
    topic: str
    turns: list[Turn] = field(default_factory=list)

    def history_for_prompt(self, perspective: str = "neutral") -> str:
        if not self.turns:
            return "(No exchanges yet — this is the opening argument.)"
        lines = []
        for t in self.turns:
            lines.append(f"### Round {t.round} — {t.name}\n{t.content}")
        return "\n\n".join(lines)

    def formatted_for_report(self) -> str:
        lines = [f"# Debate: {self.topic}\n"]
        for t in self.turns:
            lines.append(f"## Round {t.round} — {t.name}\n{t.content}")
        return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Core agent runner
# ---------------------------------------------------------------------------

async def get_agent_response(
    system_prompt: str,
    prompt: str,
    label: str,
) -> str:
    """Run a single-turn agent query and return the text response."""
    collected: list[str] = []

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(Path(__file__).parent),
            allowed_tools=[],           # pure reasoning — no tools needed for debate turns
            permission_mode="acceptEdits",
            system_prompt=system_prompt,
            max_turns=3,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    collected.append(block.text.strip())

    return "\n\n".join(collected) if collected else "(no response)"


async def get_report(state: DebateState, output_path: Path) -> str:
    """Run the moderator agent to synthesize the debate into a report."""
    debate_text = state.formatted_for_report()

    prompt = f"""Below is a {len(state.turns)}-turn debate on the topic: "{state.topic}"

{debate_text}

---

Write a comprehensive synthesis report (save it to `{output_path.name}`) that includes:

1. **Executive Summary** — the core thesis of each debater and the central tension
2. **Round-by-Round Analysis** — key arguments made, strongest points on each side
3. **Points of Agreement** — where both debaters converged or acknowledged common ground
4. **Irresolvable Tensions** — where genuine disagreement remains and why
5. **Verdict / Synthesis** — your neutral assessment: what does the evidence support?
   Which arguments were strongest? What would resolve the debate?
6. **Further Reading** — 5–8 key papers or thinkers relevant to this debate

Be rigorous, balanced, and intellectually honest. This report is for a technical audience.
"""

    collected: list[str] = []

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(Path(__file__).parent),
            allowed_tools=["Write"],
            permission_mode="acceptEdits",
            system_prompt=MODERATOR_SYSTEM,
            max_turns=5,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    collected.append(block.text.strip())

    return "\n\n".join(collected) if collected else "(no report generated)"


# ---------------------------------------------------------------------------
# Debate orchestrator
# ---------------------------------------------------------------------------

async def run_debate(topic: str, rounds: int, output_path: Path) -> None:
    state = DebateState(topic=topic)

    agent_configs = [
        ("A", "Dr. Alexandra Chen (RL / Neuroscience)", AGENT_A_SYSTEM),
        ("B", "Dr. Marcus Webb (Bayesian / Causal)", AGENT_B_SYSTEM),
    ]

    print(f"\nDebate topic: {topic}")
    print(f"Rounds: {rounds}  |  Output: {output_path.name}")
    print("=" * 70)

    for round_num in range(1, rounds + 1):
        for agent_id, agent_name, agent_system in agent_configs:
            print(f"\n[Round {round_num}] {agent_name} is responding...")

            history = state.history_for_prompt()
            if round_num == 1 and agent_id == "A":
                prompt = (
                    f'The debate topic is: "{topic}"\n\n'
                    f"This is round 1. Make your opening argument."
                )
            else:
                opponent_name = agent_configs[1][1] if agent_id == "A" else agent_configs[0][1]
                prompt = (
                    f'The debate topic is: "{topic}"\n\n'
                    f"This is round {round_num} of {rounds}.\n\n"
                    f"## Debate so far\n\n{history}\n\n"
                    f"---\n\n"
                    f"Now respond to {opponent_name}'s latest argument. "
                    f"{'This is your final round — make your strongest closing case.' if round_num == rounds else ''}"
                )

            response = await get_agent_response(agent_system, prompt, agent_name)

            state.turns.append(Turn(
                agent=agent_id,
                name=agent_name,
                round=round_num,
                content=response,
            ))

            # Print a preview
            preview = response[:300].replace("\n", " ")
            print(f"  → {preview}{'...' if len(response) > 300 else ''}")

    # --- Generate report ---
    print(f"\n{'=' * 70}")
    print("Debate complete. Generating synthesis report...")

    await get_report(state, output_path)

    print(f"\nReport saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_TOPIC = "Is reward maximization (RL) or probabilistic inference (Bayesian) the better foundation for building intelligent systems?"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Two-agent debate system")
    parser.add_argument("topic", nargs="*", help="Debate topic (quoted string)")
    parser.add_argument("--rounds", type=int, default=10, help="Number of debate rounds (default: 10)")
    parser.add_argument("--output", default="debate_report.md", help="Output report filename")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.topic:
        topic = " ".join(args.topic)
    elif not sys.stdin.isatty():
        topic = sys.stdin.read().strip() or DEFAULT_TOPIC
    else:
        print("Two-Agent Debate System")
        print(f"Default topic: {DEFAULT_TOPIC}\n")
        user_input = input("Enter debate topic (or press Enter for default): ").strip()
        topic = user_input if user_input else DEFAULT_TOPIC

    output_path = Path(__file__).parent / args.output

    asyncio.run(run_debate(topic=topic, rounds=args.rounds, output_path=output_path))


if __name__ == "__main__":
    main()
