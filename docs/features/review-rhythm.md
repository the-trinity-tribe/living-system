# Feature: the review loop and review rhythm

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It answers "how does the yes work day to day?".

An agent only proposes. You decide with a review. This feature adds two things around that:

- **A mode:** you choose **batch** (the default) or **ask-now**.
  - **Batch:** the agent writes a proposal, tells you in one line, and carries on. Proposals wait. You go through them in a short pass (the `tend` skill), one at a time.
  - **Ask-now:** the agent asks you right away: approve, reject or later?
- **A rhythm:** you choose how often a review is due: `daily`, `weekly` (the default), `monthly`, a number of days, or `off`. When something is waiting and your rhythm has passed, `status` says so, and `living.py nudge` says it once a day at the start of a session. Nothing runs in the background.

It also lets you name **who else may approve**, in which area (see "How do you use it?").

## Why would someone need it?

Without a rhythm, proposals pile up until you remember them, or they never get reviewed. A reminder that fires all day is worse: it breaks your focus. This is a middle way: a quiet day is silent, a waiting queue gets one calm line, and the yes is always yours.

## What problem does it solve?

- "Do I get asked every time, or do I look it over later?" You choose, and the docs say which.
- Reviews are left to memory. Now the workspace tells you, once, when it has been long enough.
- Nobody knows who may approve what. Now it is written as an approved decision.

## What does it require?

A Living System workspace and Python 3.10 or newer. The reminder line works with any agent that reads `AGENTS.md`. The `tend` pass needs Claude Code or Codex.

## How do you install or enable it?

New workspaces get **weekly** and **batch** at setup. You can change both when `init` asks, or later:

```sh
python3 tools/living.py review-rhythm ~/my-workspace                       # show
python3 tools/living.py review-rhythm ~/my-workspace --every weekly --mode batch
python3 tools/living.py review-rhythm ~/my-workspace --every off           # no reminders
python3 tools/living.py init ~/my-workspace --profile professional --language en --review-every monthly --review-mode ask-now
```

An older workspace has no rhythm and stays silent until you set one. `upgrade` does not change your settings; it does add the new rules for your agent.

**Optional timer (opt-in, not installed by Living System).** The timer only prints a reminder. It never reviews anything. `nudge` speaks at most once a day, so if the timer says it, your agent will not repeat it that day.

- **Linux** (tested here with a stand-in for the notifier). Run `crontab -e` and add (weekdays at 09:00):

  ```sh
  0 9 * * 1-5 line=$(python3 /path/to/living-system/tools/living.py nudge /path/to/workspace); [ -n "$line" ] && notify-send "Living System" "$line"
  ```

- **macOS** (not tested by us). A launchd job that runs, at the time you choose: `line=$(python3 ... nudge ...); [ -n "$line" ] && osascript -e "display notification \"$line\" with title \"Living System\""`.
- **Windows** (not tested by us). A Task Scheduler task that runs a PowerShell line such as `$l = py C:\path\living-system\tools\living.py nudge C:\path\workspace; if ($l) { msg $env:USERNAME $l }` (`msg` is missing on Windows Home; use any notifier you have).

## How do you use it?

**Every day:** nothing to do. If a review is due you will see one line, for example: *Review is due: 3 item(s) waiting, last looked over 2026-10-12 (your rhythm: weekly).*

**When you have ten minutes:** say "let's tend" (or run `status`). Take the waiting items one at a time. For a proposal, tell your agent the outcome for that named proposal ("approve the first one"), or run the review command yourself. At the end of the pass the agent runs `living.py reviewed .`, which records that you looked.

**Quick yes, in the moment:** if you chose ask-now, or a proposal blocks what you are doing, the agent shows it and asks. Same rule: only your stated outcome for that named proposal counts.

**Who else may approve.** At setup you are asked: "Besides you, is there anyone who may approve decisions, and for which area?" If yes, your agent writes it as a proposal (`living.py propose --kind new`) whose rule starts with `Approvers:`, for example *Approvers: Alex may approve decisions about client updates. Everything else is approved by the owner.* You approve it yourself. Until then only you approve. To change it, write a proposal like for any rule.

## Example scenarios

- **Quiet week.** Nothing is waiting. No line, no message.
- **A busy week.** Three proposals wait. On Monday your agent says once: "Review is due: 3 items waiting". You say "later". It says nothing more that day. Tomorrow it mentions it once more, because the review is still due. On Friday you tend for ten minutes. The clock restarts.
- **A blocking proposal.** In batch mode the agent normally does not interrupt, but a proposal that blocks the task in hand may be asked about once.
- **A second approver.** Maya's workspace has an approved decision "Approvers: Alex may approve decisions about client updates." `status` and `agency` show it. If Alex says "I approve", the agent checks with Maya, who confirms it matches the decision.

(Names are made up for this page.)

## What changes inside the system when it runs?

- `review-rhythm`, `reviewed` and `nudge` write only `.living/profile.json`: the settings `review_every`, `review_mode`, the day the rhythm was set (`review_set_on`), the day of your last look (`last_review`) and the day `nudge` last spoke (`nudged_on`). Dates only; nothing about what you did.
- **"Due"** means: something waits **and** your rhythm has passed since the newest of: your last `reviewed`, any review in `decisions/review-record.jsonl`, or the day you set the rhythm. Waiting means a proposal to review, shared role knowledge, a parked item whose date came, a knowledge or lesson suggestion, or a delegation to look at again.
- `status` adds the due line only when it is due, and lists approvers from approved decisions.
- `agency` shows mode, rhythm and approvers, each marked **[instruction]**.

## Where does the human keep control?

- Only `review.py review` creates or changes a rule, in both modes. This is enforced by the tool.
- `nudge` only prints text. It never reviews, approves or edits anything. `reviewed` only records a date.
- **Instructions, not tool rules:** batch or ask-now behaviour, saying the reminder once, and who else may approve. Names are labels: the tool does not check who types. A job title gives no approval right; only an approved `Approvers:` decision does.
- In a team workspace the tool already refuses an approval by whoever proposed the change.

## What can go wrong, and how do you undo it?

- **Reminders annoy you:** `review-rhythm . --every monthly` or `--every off`.
- **A reminder you do not expect:** the rhythm was set (or defaulted) at `init`. Run `review-rhythm .` to see it.
- **The agent asks every time though you chose batch, or never reminds you:** these are instructions for the agent, not enforced. Say "batch mode, please", and check `.claude/` or `AGENTS.md` is loaded. `status` always shows the due line regardless.
- **The clock restarts after a single review:** by design, one look counts for everything waiting. Waiting items are still listed by `status`.
- **Someone approves who is not an approver:** the tool cannot stop it, because it cannot know who is typing. Keep the workspace in Git if you need to see who changed what.
- **Limits:** no timer is installed for you, nothing is sent anywhere, and nothing is measured about how you work.
