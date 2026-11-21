# Feature: overview

Status: EXPERIMENTAL. Version: 0.4.0.

## What does this feature do?

It makes one page you open in your browser. The page shows what waits for you, the rules in force, your knowledge files and the health of your workspace. It changes nothing in the workspace.

## Why would someone need it?

Not everyone likes reading a terminal. A page with clear sections and big numbers is easier to scan, easier to come back to, and works on a phone.

## What problem does it solve?

- You see the whole workspace at a glance, without opening folders.
- You can check your rules without an agent and without a command line open.
- Knowledge that is due for a re-check stands out.

## What does it require?

A Living System workspace, Python 3.10 or newer, and any web browser. No internet connection.

## How do you install or enable it?

Nothing to install. Run it from the Living System folder and choose a file name outside the workspace:

```sh
python3 tools/living.py overview ~/my-workspace --out ~/living-overview.html
```

Then open that file in your browser. Or ask your agent "Make me an overview page of my workspace".

## How do you use it?

Make the page whenever you want a fresh look; the same command replaces the earlier page. The page has these parts:

| Part | Where it comes from |
| --- | --- |
| Numbers at the top | counts of what waits, rules in force, knowledge files, parked ideas and health findings |
| Waiting for you | the same list as [status](status.md), with the command to copy once you have decided |
| Rules in force | each current decision with its title, date and who approved it |
| Where you stopped | the "next step" line of the handover note |
| Knowledge | each knowledge file with how long ago it was checked |
| Repeated work | the Third-Run counts, if you count any |
| Health | the findings from [doctor](doctor.md) |

## Example scenarios

- Monday morning: you make the page, read "Waiting for you", and review the two proposals listed there.
- You want to show a colleague how your rules look. You make the page, read it first, and share your screen.
- You are on your phone. You open the saved page and check which rule applies before you answer a client.

## What changes inside the system when it runs?

Nothing in the workspace. One `.html` file is written where you say, outside the workspace. The page is plain text and styling: it has no scripts, loads nothing from the internet, and follows your device's light or dark setting.

## Where does the human keep control?

- It is read-only, and the page is a copy: the files in your workspace are what counts.
- It is never saved inside the workspace (or a linked company workspace), so no agent mistakes it for the rules.
- It only replaces a page it made earlier, never another file.
- Parked ideas are private, so the page shows how many there are and not what they say.

## What can go wrong, and how do you undo it?

- **"already exists and was not made as the overview":** that file name is taken by something else. Choose a new name.
- **"must end in .html":** add `.html` to the file name.
- **The page looks out of date:** it is a snapshot. Run the command again.
- **Limits:** the page holds your rule titles and file names. Read it before you share it, and store it like any other private file. To remove it, delete the file.
