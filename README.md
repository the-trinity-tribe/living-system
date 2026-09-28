# Living System

**Status: experimental, v0.1, Slice 1 of 6.**

Living System tests one idea: a Human-AI work system can change what it knows over time without letting AI silently redefine what is true. Everything lives in plain files in this repository, owned by humans, readable without any particular AI tool.

This repository uses a small fictional organisation, Moss & Circuit, as a worked example.

## What Slice 1 demonstrates

A fresh agent with no memory of previous conversations can:

1. enter the repository and find where to start;
2. understand who and what has authority;
3. read only the smallest set of files a task needs;
4. prefer approved organisational decisions over plausible guesses.

Slice 1 does not yet include staging, approval or promotion of new knowledge. Those come in later slices.

## Cold-open test

1. Open a new session of any AI agent that can read files, with this folder as its working directory. Make sure it has no prior conversation history about this project.
2. Give it no hints. Ask questions about Moss & Circuit and its current work.
3. Observe which files it opens and whether its answers come from approved sources.

The expected answers are deliberately kept out of this repository so the test agent cannot read them.

## Where to start reading

Agents and humans both start at [AGENTS.md](AGENTS.md).
