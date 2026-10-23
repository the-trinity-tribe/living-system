# Feature: value check

Status: EXPERIMENTAL. Version: 0.2.0-dev.

## What does this feature do?

It is a small test you run yourself, to see whether Living System helps you. You ask an AI the same five questions about your own work twice: once before you use the system and once a few weeks later. You mark each answer. A tiny command then counts your marks.

## Why would someone need it?

A setup can feel helpful without being helpful. The check gives you something simple to look at instead of a feeling.

## What problem does it solve?

It makes one risk visible: an AI that sounds sure and is wrong. Your marks separate four cases: right, wrong, made up, and "I don't know". "Made up" is the one to watch. It means the AI invented an answer. Living System is meant to reduce that.

## What does it require?

- A workspace. `value-check/` is created by `init`.
- You: you write the questions and mark the answers. The agent does not.
- Python 3 for the counting command.

## How do you install or enable it?

Nothing to install. The files are already in your workspace:

- `value-check/README.md`: the steps.
- `value-check/questions.md`: the table you fill in.
- `value-check/log.md`: free notes.

## How do you use it?

1. **Before** you rely on the system, replace the five example questions in `value-check/questions.md` with questions about your own work whose real answers you already know. For example: "Who has to approve X?" Include one whose honest answer is "it is not written down".
2. Ask a **fresh** AI session each question. Do not help it.
3. In the **Before** column, write exactly one of: `right`, `wrong`, `made up`, `don't know`.
4. After a few weeks of use, ask the same questions in a fresh session in your workspace. Fill the **After** column.
5. Count:

   ```sh
   python3 <Living System folder>/tools/living.py value-score <your workspace>
   ```

6. Write what you noticed in `value-check/log.md`.

Example output:

```text
              right      wrong    made up don't know
before            1          1          2          1
after             3          0          0          1
after: 1 not scored yet
```

## Example scenarios

- A freelancer asks "Who approves what I send to a client?" Before: `made up`. After the rule is written and approved: `right`.
- A student asks "When is my thesis deadline?" There is no deadline in the files. The honest answer is "not recorded". After: `don't know`, which counts as a good result here.

## What changes inside the system when it runs?

Nothing. `value-score` only reads `value-check/questions.md` and prints a table. It writes no file.

How it reads the file:

- It looks for a table whose header has both a `Before` and an `After` column.
- Cell words are not case-sensitive. Backticks around the word are ignored.
- An **empty** cell counts as "not scored yet" and is listed under the table.
- Any other word makes it stop with `REFUSED` (exit code 2), so a typo is not counted as zero.
- No such table, or no `questions.md`, also gives `REFUSED`. Prose instead of a table is not scored.
- A `|` inside a question must be written `\|`.

## Where does the human keep control?

You write the questions, you ask them, you decide what counts as right. The command never asks an AI anything and never changes a file.

## What can go wrong, and how do you undo it?

**What the score does not measure.**

- It does not check your marks. If you call a wrong answer `right`, it counts as right.
- It does not judge whether your questions are good, or whether five is enough.
- It gives no pass or fail and no percentage. It does not compare Before with After for you.
- It does not show that the system caused a change. A different AI model, a different day, or a better question can change the result.
- It is an informal check, not a scientific measurement. This is stated in `value-check/README.md` too.

**Common problems.**

- `REFUSED: ... is not one of: right, wrong, made up, don't know`: fix the word in that cell.
- `no table with 'Before' and 'After' columns found`: restore the table header.
- Undo: edit the file. Nothing else is touched.
