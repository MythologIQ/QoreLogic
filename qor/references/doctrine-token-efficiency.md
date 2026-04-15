# Doctrine: Token Efficiency

**Source inspirations**: `drona23/claude-token-efficient` (CLAUDE.md drop-in), Anthropic prompt cache TTL semantics, Qor workflow-bundle experience.

**Goal**: Long-running workflows (multi-phase bundles, deep audits, migrations) MUST stay within practical context budgets. This doctrine codifies the rules every Qor skill SHOULD honor and every workflow bundle MUST honor.

## Output rules (every skill)

1. **No sycophantic openers or closers.** No "Sure!", "Great question!", "I hope this helps!"
2. **Short prose sentences (8-10 words target).** Code stays normal; English gets compressed.
3. **No em-dashes, smart quotes, or non-ASCII parser-unfriendly chars in code/data.** Standard hyphens only.
4. **Result first, explanation only if asked.** State outcomes; reserve methodology for explicit requests.
5. **No restating the question before answering.** The question is in the conversation; the answer is the value.

## Read/write rules

6. **Read once, don't re-read unchanged files.** Use cached knowledge of file contents within a session unless a file may have changed.
7. **Edit > rewrite.** Smaller diffs, smaller token footprint, cleaner review surface.
8. **Skip files >100 KB unless explicitly required.** If you must read a large file, paginate or use Glob/Grep targeted queries.
9. **Reference by path, not paste.** "See `docs/X.md` §Y" beats inlining 200 lines. Paste only when the reader needs the literal text in this conversation.

## Investigation rules

10. **Delegate high-token research to subagents.** Subagents have their own context; main context receives only the structured summary.
11. **Use Glob/Grep before Read.** Locate before reading.
12. **Tool result first.** Don't narrate "I will run X" — run X, then summarize what X returned.

## Long-session rules

13. **Suggest `/cost` on long sessions** — operator can monitor cache hit ratio + spend.
14. **Suggest fresh session on topic shift.** A new task usually warrants a new session; old context is dead weight.
15. **Workflow bundles MUST honor `budget.abort_on_token_threshold`** (per `qor/gates/workflow-bundles.md`). Write a resume marker; exit cleanly; suggest fresh session.
16. **Checkpoint summaries <100 words.** Bundles MUST stay terse at checkpoints; long checkpoint prose defeats the purpose.

## Drop-in CLAUDE.md

Repo-root `CLAUDE.md` is the consumer-facing summary of these rules. It MUST stay short (<60 lines) — instruction files cost input tokens every turn; if `CLAUDE.md` grows too large, it costs more than it saves.

The full doctrine lives here. `CLAUDE.md` references this doc and lists only the highest-impact rules.

## Anti-patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| Re-reading the same file each turn | input tokens × turns | Cache knowledge per-session |
| Inlining 200-line file dumps in prose | input tokens × all subsequent turns | Reference by path |
| Sycophantic preamble | output tokens × every response | Forbid in CLAUDE.md |
| Bundle running past context exhaustion | conversation becomes useless | Abort on budget; resume marker |
| Reading a 5MB log without pagination | input token spike, often truncated | Grep/Glob targeted, paginate |
| Subagent for trivial work | subagent overhead > value | Subagent only for >5 file reads or >2 distinct queries |
| Verbose checkpoint summaries | undoes the whole checkpoint pattern | <100 words always |

## Verification

- `wc -l CLAUDE.md` should return <60.
- Skills referencing this doctrine: `grep -l "doctrine-token-efficiency" qor/skills/ -r`.
- Bundles referencing this doctrine: `grep -l "doctrine-token-efficiency" qor/skills/meta/ -r`.

## Update protocol

When new token-efficiency learnings emerge (new harness behavior, new caching semantics, new model context limits), update this doctrine FIRST, then propagate the headline change to repo-root `CLAUDE.md` if it changes the headline rules.
