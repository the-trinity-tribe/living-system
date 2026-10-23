---
name: idea-check
description: Help the human decide whether an idea is worth building or doing now, and what the smallest useful version is, before any work starts. Use when the human says "should we build this?", "is this worth it?", "check this idea", or picks a parked idea to look at.
---

The aim is to decide, not to build. Ask one question at a time and accept short answers; "don't know" is a valid answer.

1. **Problem.** How often does it happen, and how bad is it when it does? Who has it?
2. **What exists.** What do they do today? Is there already a tool, module or workflow for it (check `.living/catalog.md` and `workflows/`)?
3. **Benefit.** What gets better, for whom, and how would we notice?
4. **Cost.** Time to make it, upkeep afterwards, things it depends on, extra load for the people using it.
5. **Risk.** Privacy, safety, anything that cannot be undone.
6. **Smallest version.** What is the smallest thing that would show whether it helps? Often: doing it by hand three times (the Third-Run Rule).
7. **Evidence.** What result would make us keep it, and what would make us stop?

Then summarise in at most five lines and offer four choices: **build the smallest version**, **try it by hand first**, **park it** (`living.py park . "<idea>"`), or **drop it**. The human chooses. Never present guesses as facts, and never invent numbers for time or money saved.
