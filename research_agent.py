"""
Research agent that synthesizes expert-level analysis on:
  - Reinforcement Learning
  - Bayesian Inference
  - Control Theory
  - Value & Reward

Usage:
    python research_agent.py
    python research_agent.py "reinforcement learning"
"""

import asyncio
import sys
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock

SYSTEM_PROMPT = """You are a world-class researcher and theorist with deep expertise across:

- **Reinforcement Learning**: MDP formulations, policy gradients, Q-learning, model-based RL,
  offline RL, multi-agent systems, reward shaping, exploration strategies, and convergence theory.
- **Bayesian Inference**: Prior/posterior reasoning, MCMC, variational inference, Bayesian
  networks, hierarchical models, approximate inference, and probabilistic programming.
- **Control Theory**: Classical PID, LQR/LQG, Lyapunov stability, optimal control, model
  predictive control (MPC), robust control, and connections to RL via dynamic programming.
- **Value & Reward**: Utility theory, reward hypothesis, intrinsic motivation, reward hacking,
  value alignment, reward modeling, and the philosophy of objective specification.

When researching and writing:
1. Search broadly first, then dive deep into key papers, debates, and open problems.
2. Draw non-obvious cross-domain connections (e.g., Bayesian RL, control-as-inference,
   reward as a Lyapunov function, KL-regularized RL as variational inference).
3. Present expert-level arguments — include mathematical intuitions, cite key researchers,
   and highlight controversies or unsolved questions.
4. Structure your output as a rigorous but readable markdown document with sections,
   subsections, and a synthesis section that ties the topics together.
5. Save the final report to a file named `research_report.md`.
"""

DEFAULT_TOPICS = [
    "reinforcement learning",
    "bayesian inference",
    "control theory",
    "value and reward in AI",
]

def build_prompt(topics: list[str]) -> str:
    topic_list = "\n".join(f"  - {t}" for t in topics)
    return f"""Research and synthesize expert-level analysis on the following topics:

{topic_list}

Steps:
1. Use WebSearch to find key papers, tutorials, and expert discussions for each topic.
2. Use WebFetch to read and extract insights from the most relevant sources.
3. Synthesize your findings into a comprehensive markdown report covering:
   - Core concepts and mathematical foundations for each topic
   - Current state of the art and open problems
   - Cross-topic connections and unified perspectives
   - Expert arguments and debates in the field
4. Save the complete report to `research_report.md`.

Aim for depth over breadth — this is for a technical audience with strong ML/math backgrounds.
"""

async def run_agent(topics: list[str]) -> None:
    prompt = build_prompt(topics)

    print(f"Starting research agent on {len(topics)} topic(s)...")
    print("Topics:", ", ".join(topics))
    print("-" * 60)

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(Path(__file__).parent),
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="acceptEdits",
            system_prompt=SYSTEM_PROMPT,
            max_turns=40,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("Agent complete.")
            if message.result:
                print(message.result)

def main() -> None:
    topics = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_TOPICS
    asyncio.run(run_agent(topics))

if __name__ == "__main__":
    main()
