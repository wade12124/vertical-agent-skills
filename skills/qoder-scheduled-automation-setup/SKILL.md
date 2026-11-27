---
name: qoder-scheduled-automation-setup
description: Create, verify, migrate and clean up Qoder scheduled automations through the builtin qoder_cron tool. Use when the user asks for a recurring/future/timed task, a reminder, an automated weekly job, a cloud or local task, or wants to change, pause, run, or delete an existing automation, including moving a local task between Full Access and Auto Approval. A mere discussion of scheduling is not creation authorization.
---

# Qoder Scheduled Automation Setup

## Overview

`mcp__builtin__qoder_cron` is the only entry point for automations. Cloud tasks can be created but never managed afterwards; local tasks are fully managed and run unattended under the task's permission mode, which is set at creation and can be changed later (step 8). Follow the sequence below; each failure mode listed has been observed in practice.

## Hard boundaries (read before calling)

- **Cloud tasks are write-once.** `add location=cloud` returns only `{success, location, taskId}`. `update`, `remove`, `run`, `enable`, `disable` accept **local task IDs only**. Passing a cloud ID to `run` returns `自动化不存在或已删除` — that is a tool-boundary error, not evidence the task failed to save. Never conclude "the task didn't get created" from that message; pausing or deleting a cloud task must be done by the user in the Automations panel.
- **Execution location is immutable.** An automation's cwd/workspace binding cannot be changed after creation. "Change it to write to a local directory" means: create a new local task, and tell the user explicitly that the old cloud task is still scheduled and will fire on the same cadence (double-run the same day; the cloud copy produces only a conversation, no file).
- **A cloud task's removal cannot be read back.** `list` returns local tasks only, so it shows no cloud row whether or not the user deleted one. When the user says they deleted or paused a cloud task, record it as their statement; never cite an empty or cloud-free `list` as evidence that it happened.
- **Never infer location** from the current device, and never silently retry a failed creation in the other location. Ask local vs cloud when the user hasn't said.
- **Never claim a model for a cloud task.** Cloud creation returns no model field. For local tasks, report the saved `task.model` verbatim from the tool result.
- Do not invent task IDs. IDs come only from `list` or from a fresh `add` result.

## Procedure

### 1. Pre-flight (always, in parallel)

- `qoder_cron {action:"list"}` — dedupe against existing tasks and capture the only legitimate ID source.
- `Bash: date "+%Y-%m-%d %H:%M:%S %z %A"` — get current local time and offset. Never infer a timezone from the language of the request.

If `list` is non-empty and something already matches the described work, update that task instead of creating a duplicate.

### 2. Resolve the schedule

- Recurring wall-clock time → `{kind:"cron", expression:"0 16 * * 5", timeZone:"Asia/Shanghai"}`. Five-field cron plus an **explicit IANA timezone** whenever the user names a time.
- Fixed elapsed interval → `{kind:"every", everyMs:...}` (cloud requires at least 60 minutes).
- One-off → `{kind:"at", at:"<ISO-8601 with Z or numeric offset>"}`, computed from the real current time and strictly in the future; pair with `deleteAfterRun` only for local one-shots.
- `schedule` is mandatory inside `job`. Omitting it is rejected as `params/job must have required property 'schedule'` before anything is saved.

### 3. Write a self-contained prompt

The run happens in its own conversation and **does not inherit this transcript**. The instruction text must carry goal, required context, constraints and expected result, and must pin down the output path and filename pattern. For a recurring report, include the continuity rule (list the output directory, read the latest previous artifact, compare against it) and an explicit "write 未获取到数据 for anything not found, never fabricate numbers" clause. Do not instruct the future run to schedule itself again.

### 4. Create — cloud

`add` with `location:"cloud"`. **Omit** `model`, `cwd`, `workspaceId`, `executionAuthorization`, `deleteAfterRun`, `expiresAt` — the cloud API does not accept them. `outputMode` defaults to `independent`. Before calling, show the proposed location, schedule, prompt and output mode and get confirmation.

### 5. Create — local, and the permission decision

Omit `model` and execution-location overrides to inherit them, unless the user asked for a specific model (use its catalog selection key) or directory. Note that `cwd` without `workspaceId` yields `executionScope.kind:"directory"`; with `workspaceId` it yields `"workspace"`.

**The default is Full Access.** A local task saved with `executionPolicy.permissionMode:"bypassPermissions"` (`executionAuthorization:true`) will search the web and write files into its cwd with no prompt, forever, on schedule. Before creating, state this and offer `executionAuthorization:false` (Auto Approval). Report whichever mode the result actually shows.

### 6. Verify the created task

From the returned `task` object read back, at minimum: `id`, `name`, `trigger.schedule`, `executionScope.cwd`, `model`, `executionPolicy.permissionMode`, `outputMode`, `enabled`.

Then convert the epoch-ms fields instead of eyeballing them:

```bash
python -c "import datetime;print(datetime.datetime.fromtimestamp(<nextRunAt>/1000))"
```

Use it on `nextRunAt` (and `createdAt`) to confirm the first run lands on the instant the user asked for, including the weekday.

If the cwd sits inside a git repository, run `git -C <cwd> rev-parse --show-toplevel` and `git status`. An artifact directory that is wholly untracked in a host repo (e.g. `?? reports/`) will accumulate untracked files on every run — say so and offer an ignore rule rather than leaving it silent.

For a repo-local artifact directory use `.git/info/exclude`, not `.gitignore`: the rule stays out of other clones and leaves tracked repo config untouched. When editing it, `Read` it first, then anchor on its **last line** and append below it — do not anchor on the boilerplate comment lines it ships with, and do not re-emit them in `new_string`.

Verify the rule actually applies: `git check-ignore -v <dir>` must name it (the report carries the rule's file and line number), and `git ls-files <dir>` must be empty, proving nothing already tracked is now hidden. Re-check status scoped to the directory (`git status --porcelain -- <dir>`); an unscoped `git status` truncated to N lines can omit the directory whether or not the rule works.

### 7. Manual verification

`run` takes a local ID only and returns `{run:{id, status:"pending", trigger:"manual", fileChanges:[]}}`. **Accepted is not finished.** Poll `list` for `runningAt` / `lastRunAt` / `lastRunStatus` / `lastError`, and check the filesystem for the expected artifact. Report the result as one of: running / produced file / failed with error / still pending — never as "completed" on the strength of the run receipt.

### 8. Changing the permission mode after creation

`update` with `patch:{executionAuthorization:false}` saves `executionPolicy.permissionMode:"auto"`; `true` saves `"bypassPermissions"`. The returned `task` is the confirmation — `permissionMode` plus a bumped `revision` — so do not make another call just to re-read that one field.

State both consequences before tightening a task that is supposed to produce a file unattended:

- **Not retroactive.** A run already in flight keeps the mode it started under; which mode a given run used is only knowable by comparing its `runningAt` against the task's `updatedAt`.
- **Approval can stall an unattended run.** A run blocked waiting for approval and one that is merely still working are not separable from these fields. Raise it as a risk to the user, not as a diagnosed cause.

### 9. Post-creation duplicate sweep

Call `list` again after creating, and the chat-session list tool. Tasks created from another window or a still-running session with the same title will not be visible in the conversation you are in, and two matches mean two runs and two files. Present the collision and let the user keep one.

`list` re-emits every task's complete `instruction.text`, so each extra call pulls the same long prompt back into context. Step 1's dedupe and step 7's polling justify it; re-confirming a field on the task you just created or changed does not.

## Failure messages and what they actually mean

| Message | Real cause |
|---|---|
| `params must have required property 'action'` | Malformed call; `action` is required on every use |
| `params/job must have required property 'schedule'` | `add` without a schedule; nothing saved |
| `自动化不存在或已删除。` | A cloud ID (or stale ID) was passed to `run`/`update`/`remove`/`enable`/`disable` |

## Reporting discipline

Report only what the tool result supports. A saved task or an accepted run is not evidence that the scheduled work finished. When migrating cloud to local, the final message must state: new local ID, schedule and cwd, plus "the cloud task `<id>` is still active — delete or disable it in the Automations panel".
