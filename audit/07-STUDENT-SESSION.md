# A first session with real students

Everything this app knows about itself came from its author and from audits.
Nobody taking MA 266 has used it while someone watched. This is a 30-minute
script for doing that with two or three classmates, one at a time. Three
sessions will show more than another audit would.

Each task below tests a decision that was made without evidence. The
*watch for* lines say which one, so a finding turns straight into a change.

---

## Before

- **Who.** Classmates taking MA 266 now. Try to include one who is behind or
  finds the course hard; the app is for them more than for anyone fluent.
- **What they run.** The download, not your development setup: build it with
  `py -3.10 packaging/build.py` and give them
  `dist/odesuite-studio-<version>-windows-amd64.zip`, or a release link once
  CI runs again. Installing it is part of the test.
- **A clean start.** On their machine nothing is remembered yet. On yours,
  delete `%LOCALAPPDATA%\odesuite\progress.json` (export it first) so the app
  opens the way it does for a newcomer.
- **Pick the topic.** Use the lesson the class is on this week, so the
  mathematics is fresh and the app is the only new thing.

## During: the rules

- Ask them to think aloud. "What are you looking for? What do you expect
  this to do?"
- **Do not help.** When they get stuck, ask "what would you try?" and wait.
  A place where you had to step in is the most valuable thing you will see.
  Write down the minute it happened.
- Do not explain the design or defend it. Notes only.

## The tasks (about 25 minutes)

1. **Unzip it and open it. Find where you would start.** (3 min)
   - *Watch for:* do they launch it without help, or stall at the Windows
     "unrecognised app" warning? Does the Course Map read as the place to
     begin? Do they find **Continue**? Do they go to *Tools* instead?
   - *Decision under test:* a first launch opens the Course Map
     (`cli.opening_screen`), and the sidebar puts *Study* above *Tools*.

2. **Open this week's lesson and read until you could explain the method to
   someone.** (5 min)
   - *Watch for:* do they read the chapter or skim to the examples? Is the
     page too long? Do they click a glossary link? Does any equation fail to
     render or look wrong?
   - *Ask afterwards:* "Was anything said in a way your lecture didn't?"

3. **Do the first typed Practice question.** (5 min)
   - *Watch for:* how do they write the answer: `e^(2t)`, `exp(2*t)`,
     `e**2t`? Do they look at the *Read as:* preview under the box? Does it
     catch a typo before they press Check? Do they understand a message like
     "'(' was never closed"?
   - *Decision under test:* the live preview (`widgets/answerpreview.py`).
     If people type in a form the parser refuses, that is the next thing to
     fix.

4. **Get one wrong on purpose, then use Hint and Show me.** (4 min)
   - *Watch for:* do they understand why the answer was marked wrong? Is a
     hint a nudge or does it give the answer away? After **Show me**, do they
     try the next question themselves?

5. **Press Next lesson, then go back and take the unit check-up in Quiz &
   Exams.** (6 min)
   - *Watch for:* do they find the check-up on their own? Does a mixed set
     feel harder than the lesson's practice (it is meant to)? Does the timer
     cause stress, even though it only reports?

6. **One open question.** (2 min) "If this were on your laptop the night
   before the midterm, would you open it? What for?"

## After

Write up each session the same day, using the sheet below. Then, for each
finding, choose one of:

- **fix**: a concrete change, filed in `audit/03-BACKLOG.md` with the minute
  it was seen;
- **watch**: seen once, so check in the next session;
- **no**: deliberate, and the reason is recorded.

Two people stuck in the same place is a fix. One person is a watch.

### Notes sheet

```
Session __   date ________   year/section ______   behind / on track / ahead

Task  Minute  What happened                          Stuck?  Helped?
1
2
3
4
5
6

How they typed answers (copy them exactly):

Things they said, word for word:

Where I had to step in:

Would they use it before the midterm?  yes / maybe / no   — because:
```

## What is not being tested

Solver Studio, the numerical side, is left out on purpose. These sessions
are about whether a student can learn from the Learning Hub. The solvers are
the best-verified part of the project, and the people who would use the
Studio are not taking MA 266.
