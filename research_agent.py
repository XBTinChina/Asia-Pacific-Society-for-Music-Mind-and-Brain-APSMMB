"""
General-purpose research agent with expert knowledge in RL, Bayesian inference,
control theory, and value/reward.

Usage:
    python research_agent.py                        # interactive: prompts you for a task
    python research_agent.py "your task here"       # inline task via CLI arg
    echo "your task" | python research_agent.py     # pipe task via stdin

Default task (no input): deep research across all four core topics.
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

You have access to WebSearch and WebFetch to gather current information, and Write to save output.
Approach every task with rigour: cite researchers, include mathematical intuitions where relevant,
highlight open problems and controversies, and draw cross-domain connections when useful.
If asked to produce a report or document, save it as a markdown file.
"""

DEFAULT_TASK = """Research and synthesize expert-level analysis on:
  - Reinforcement Learning
  - Bayesian Inference
  - Control Theory
  - Value and Reward in AI

Cover: core concepts and math foundations, state of the art, open problems, and cross-topic
connections (e.g., control-as-inference, KL-regularized RL, Bayesian RL).
Save the full report to `research_report.md`."""


def get_task() -> str:
    """Resolve task from: CLI arg > stdin pipe > interactive prompt > default."""
    # 1. CLI argument
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])

    # 2. Piped stdin (non-interactive)
    if not sys.stdin.isatty():
        task = sys.stdin.read().strip()
        if task:
            return task

    # 3. Interactive prompt
    print("Research Agent — powered by Claude")
    print("Default task: deep research across RL, Bayesian inference, control theory, value/reward")
    print()
    task = input("Enter your task (or press Enter to use the default): ").strip()
    return task if task else DEFAULT_TASK


async def run_agent(task: str) -> None:
    print()
    print("Task:", task[:120] + ("..." if len(task) > 120 else ""))
    print("-" * 60)

    async for message in query(
        prompt=task,
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
            print("Done.")
            if message.result:
                print(message.result)


def main() -> None:
    task = get_task()
    asyncio.run(run_agent(task))


if __name__ == "__main__":
    main()
