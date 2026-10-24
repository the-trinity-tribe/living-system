# Credits

## Origin

Living System was created, designed and architected by **Adrianna Mamczarz** inside **The Trinity Tribe**. She combined the ideas below with her own methods (Living System Design, the Third-Run Rule, the proposal and review model, delegation levels, calm-by-design upkeep) and tested the result in her own daily work before it became this project. AI agents assisted with the implementation; design decisions, review and acceptance stayed with her.

The people and projects below inspired parts of it. **None of them built Living System**, and naming them does not mean they know of, endorse or are affiliated with it.

## Thinkers who shaped how it thinks

- **Jake Van Clief and David McDermott**, *Interpretable Context Methodology: Folder Structure as Agentic Architecture* ([arXiv 2603.16021](https://arxiv.org/abs/2603.16021), CC BY 4.0; repository under the MIT licence). Folders and plain files as the structure of AI work, one small, checkable step at a time, loading only the context each step needs. Inspired the staged workflows, the modules and the routing guide. Details below.
- **David Shapiro**: his heuristic imperatives (reduce suffering, increase prosperity, increase understanding) and his thinking on which work should stay human. Inspired the question of what time saved by AI is *for*, which every workspace's work agreement asks.
- **Jacque Fresco** ([The Venus Project](https://www.thevenusproject.com/)): designing whole systems around real human needs and the planet's limits, rather than around tools. Inspired the idea of a system that serves the person, not the other way round.

## Writing and research that informed the design

- **Erik Schluntz and Barry Zhang (Anthropic)**, [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) (December 2024): start with the simplest thing that works and add autonomy only where it pays off. Reflected in "draft" as the default delegation level and in autonomy granted one kind of work at a time.
- **Mem0**, [*State of AI Agent Memory 2026*](https://mem0.ai/blog/state-of-ai-agent-memory-2026): stale memory is one of the hardest open problems, so freshness matters more than volume. Reflected in `last_verified` dates, re-check reminders and a curated context instead of an ever-growing memory.
- **Microsoft Research**, [*SkillOpt*](https://www.microsoft.com/en-us/research/blog/skillopt/): improving an agent's instruction file through small, bounded edits, and remembering which edits were rejected. Reflected in the `tend` upkeep pass (one small change at a time, always approved by a person) and in lessons that become rules only through a reviewed proposal.
- **ai-boost**, [*awesome-harness-engineering*](https://github.com/ai-boost/awesome-harness-engineering): a curated collection of patterns for the scaffolding around AI agents, including memory, permissions and human-in-the-loop design. Informed the human approval step before anything an agent learns becomes a rule.
- Also read while designing: Redis on [AI agent architecture](https://redis.io/blog/ai-agent-architecture/) (keeping a trace of what agents did) and [MindStudio](https://www.mindstudio.ai/blog) on learning loops (instructions that improve from a person's feedback), which shaped the staged-learning module.

## Built on

- **The [AGENTS.md](https://agents.md/) open format**, now stewarded by the Agentic AI Foundation at the Linux Foundation. Living System's rules live in an `AGENTS.md` so any agent that reads the format can use a workspace.
- **Claude Code** (Anthropic) and **Codex** (OpenAI), whose hooks make the write guard possible.
- **Design**: The Trinity Tribe's Solaris design system, itself inspired by Stanisław Lem's novel *Solaris*. Fonts: Ubuntu (Ubuntu Font Licence) and Figtree (SIL Open Font Licence).

## Interpretable Context Methodology (ICM)

The staged-workflow example in `demo/moss-and-circuit/workflows/client-update/`, the workflow generator and most modules use ideas from ICM by **Jake Van Clief** and **David McDermott**.

- Repository: MIT licence.
- Paper: arXiv 2603.16021, CC BY 4.0.
- **Concepts were reimplemented by hand. No files were copied from the ICM repository.** The example is labelled as an example and is not endorsed by the ICM authors.

## Licence

Living System is under the Mozilla Public License 2.0. See [LICENSE](LICENSE).
