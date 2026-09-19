# Atlas Workbench — Setup & Repository Guide

Companion to the 16-week roadmap. Everything to install on a Mac, every package and why
it's there, and how to build the repository properly — one commit at a time.

| | |
|---|---|
| **Platform** | macOS |
| **Stack** | FastAPI · React · PostgreSQL |
| **Setup time** | ~3 hours |
| **Phase** | Weeks 1–2 |

> **Before you start.** Install top to bottom — each section assumes the one above it.
> Homebrew needs the Xcode tools, everything else needs Homebrew. Don't skip ahead to the
> interesting packages; a half-built toolchain fails in confusing ways an hour later.

---

## 01 · Base toolchain

### 1 · Xcode Command Line Tools

Apple's compiler toolchain. Homebrew won't install without it, and several Python packages
compile C extensions during install.

```bash
xcode-select --install
```

### 2 · Homebrew

The package manager for macOS. Every other tool here comes through it.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon only — Homebrew installs to /opt/homebrew, not on PATH by default
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3 · Git — the real one

macOS ships an old Git bundled with Xcode. Install the current one and configure it once.

```bash
brew install git

git config --global user.name  "Sanchit Kumar"
git config --global user.email "sanchitkumar1402@gmail.com"
git config --global init.defaultBranch main
git config --global pull.rebase true        # linear history, no merge-commit noise
git config --global core.editor "code --wait"
git config --global push.autoSetupRemote true
```

That email must match the one on your GitHub account, or your commits won't be attributed to
you and your contribution graph stays empty.

### 4 · GitHub CLI

`gh` lets you create repos, open pull requests and read CI results without leaving the
terminal. It also handles authentication, saving you from generating access tokens by hand.

```bash
brew install gh
gh auth login          # GitHub.com → HTTPS → login with browser
```

### 5 · uv — Python versions and packages

One tool replacing `pyenv`, `virtualenv`, `pip` and `pip-tools`. Roughly 10–100× faster than
pip, and it resolves dependencies properly instead of installing whatever it finds first.

```bash
brew install uv
uv python install 3.12
```

**Why not the Python already on my Mac?** macOS ships a Python the operating system itself
depends on. Installing packages into it can break system tools, and Apple replaces it without
warning during OS updates. Rule: never `pip install` into a Python you didn't install yourself.

**Virtual environment** — an isolated folder holding one project's interpreter and its
packages. Without it every project shares one global package set, and the moment two projects
need different versions of the same library, one breaks. Every serious Python project gets its
own.

**What uv does underneath** — `uv venv` creates `.venv/`; `uv pip install` installs into it;
`uv pip compile` turns loose requirements into a fully-pinned lockfile. Same concepts as the
classic `python -m venv` / `pip` / `pip-tools` workflow, which you'll meet in every tutorial
you read — worth knowing the mapping.

### 6 · Node via fnm

Don't install Node directly. Different projects pin different versions; a version manager
switches per-directory automatically.

```bash
brew install fnm
echo 'eval "$(fnm env --use-on-cd)"' >> ~/.zshrc
exec zsh

fnm install --lts
fnm default lts-latest
```

### 7 · OrbStack (containers)

You need Docker to run Postgres and Redis. Docker Desktop works but is heavy on a laptop.
OrbStack is a drop-in replacement — same `docker` and `docker compose` commands, a fraction of
the battery and memory.

```bash
brew install --cask orbstack
```

---

## 02 · Postgres and Redis — in containers, not on your Mac

You could `brew install postgresql`. Don't.

**Dev/prod parity** — the principle that development should resemble production as closely as
possible. A Homebrew Postgres is a different version, differently configured, with different
extensions, than the managed Postgres you deploy against. Every gap is a bug that only appears
after you deploy. A container pins the exact image, version and extension set — and your CI
runner and your laptop get the identical thing.

**Container vs VM** — a VM emulates a whole computer including its own OS: heavy, slow to
start. A container shares the host kernel and isolates only filesystem and processes — starts
in under a second, costs almost nothing. That's why you can casually run four databases and
throw them all away.

`infra/docker-compose.yml`:

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: atlas
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: atlas
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atlas"]
      interval: 5s

  cache:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

```bash
docker compose -f infra/docker-compose.yml up -d     # start
docker compose -f infra/docker-compose.yml logs -f   # watch
docker compose -f infra/docker-compose.yml down      # stop (data survives)
docker compose -f infra/docker-compose.yml down -v   # stop AND wipe the volume
```

Enable the extension inside the database once:

```bash
docker compose -f infra/docker-compose.yml exec db \
  psql -U atlas -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Adding PostGIS later.** No public image ships pgvector *and* PostGIS together, so when you
reach the spatial work in Phase 3, build a four-line image of your own:

```dockerfile
# infra/postgres.Dockerfile
FROM pgvector/pgvector:pg16
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-16-postgis-3 \
 && rm -rf /var/lib/apt/lists/*
```

Then swap `image:` for `build: {context: ., dockerfile: postgres.Dockerfile}`.

> **Why `devpassword` is fine here and nowhere else.** This container is bound to your laptop
> and holds throwaway data. Committing that password is harmless. The moment a credential
> points at anything real it goes in `.env`, which is gitignored — and the rule is absolute,
> because Git history is permanent.

---

## 03 · Editor and utilities

### VS Code

```bash
brew install --cask visual-studio-code

for ext in \
  ms-python.python ms-python.vscode-pylance charliermarsh.ruff \
  dbaeumer.vscode-eslint esbenp.prettier-vscode \
  eamodio.gitlens github.vscode-github-actions \
  ms-azuretools.vscode-docker usernamehw.errorlens \
  ms-toolsai.jupyter tamasfe.even-better-toml \
  redhat.vscode-yaml
do code --install-extension "$ext"; done
```

| Extension | Why it's on the list |
|---|---|
| **Ruff** | Lints and formats Python as you type, with the same rules CI enforces. Catching a lint error in the editor rather than a failed CI run is the point. |
| **Pylance** | Type checking and autocomplete. Tells you a function returns `None` before you call `.strip()` on it. |
| **GitLens** | Shows who wrote each line and when, inline. Invaluable for understanding your own code from six weeks ago. |
| **Error Lens** | Puts errors on the line itself instead of hiding them in a panel you never open. |
| **GitHub Actions** | Validates workflow YAML before you push. CI files are famously easy to get subtly wrong. |

### Command-line utilities

```bash
brew install jq ripgrep tree httpie direnv pre-commit
```

| Tool | What it does | Where you'll use it |
|---|---|---|
| `jq` | Query and reshape JSON on the command line | Inspecting Wikidata SPARQL responses without writing a script |
| `ripgrep` (`rg`) | Search code, respects .gitignore, very fast | Finding every use of a function before renaming it |
| `httpie` | A humane `curl` | Hitting your own API: `http :8000/events year==1914` |
| `direnv` | Auto-loads `.env` when you `cd` into the project | Stops you running the app with the wrong database URL |
| `pre-commit` | Runs linters before a commit is created | Makes it impossible to commit unformatted code |
| `tree` | Prints directory structure | Pasting your repo layout into a README |

### Two GUI apps worth having

**TablePlus** (`brew install --cask tableplus`) — a database browser. Free tier allows two open
tabs, enough for this. Being able to *see* your tables while designing the schema in Phase 2
makes ER modelling far less abstract.

**Bruno** (`brew install --cask bruno`) — an API client like Postman, except it stores saved
requests as plain text files in the repo, so your API requests get version-controlled alongside
the code that serves them. FastAPI's `/docs` covers most needs, so this is a nice-to-have.

---

## 04 · Python packages

Don't install all of this in Week 2. Install group by group as each phase needs it — a
dependency you haven't used yet is one you can't explain, and unexplained dependencies rot.

Split into two files. `requirements.txt` is what production needs; `requirements-dev.txt` is
what only you need. Your deployed container installs the first and not the second, keeping the
image smaller and the attack surface narrower.

### Web layer

| Package | Phase | What it does and why this one |
|---|---|---|
| `fastapi` | P2 | The web framework. Validates requests from type hints and generates interactive API docs for free — Swagger UI at `/docs` without writing a line of documentation. |
| `uvicorn[standard]` | P2 | The ASGI server that runs FastAPI. ASGI is the async successor to WSGI — it can hold thousands of open connections while waiting on slow AI calls, which a thread-per-request server cannot. |
| `pydantic` | P2 | Data validation from type annotations. The load-bearing library of the whole stack — request bodies, config, and later your LLM's structured output all get validated by it. |
| `pydantic-settings` | P2 | Loads config from environment variables into a typed object. A missing `DATABASE_URL` fails loudly at startup instead of as a confusing `None` twenty minutes later. |

### Database

| Package | Phase | What it does |
|---|---|---|
| `sqlalchemy` | P2 | The ORM (Object-Relational Mapper). `session.get(Event, 42)` instead of raw SQL. Use 2.x — syntax changed substantially from 1.x, so check tutorial dates. |
| `alembic` | P2 | Migrations. Every schema change becomes a versioned, reviewable, reversible script instead of a `CREATE TABLE` you ran once and forgot. |
| `psycopg[binary]` | P2 | The Postgres driver, version 3. `[binary]` ships precompiled so you don't need Postgres headers locally. |
| `pgvector` | P5 | Python bindings for the vector column type, so SQLAlchemy understands `Vector(384)`. |
| `geoalchemy2` | P3 | Adds PostGIS geometry types to SQLAlchemy. |

### Cache and background work

| Package | Phase | What it does |
|---|---|---|
| `redis` | P2 | Redis client. Caching, rate limiting, session state. |
| `arq` | P6 | Async job queue on Redis. An AI call takes 10–30s; you can't hold an HTTP request open that long, so you enqueue a job and let the client poll. Celery is the industry standard but far heavier; `arq` is ~200 lines of concepts. |

### Data ingestion — Phase 3

| Package | What it does |
|---|---|
| `httpx` | HTTP client with async support. Doubles as FastAPI's test client, so one API for both. |
| `SPARQLWrapper` | Queries the Wikidata SPARQL endpoint — where your events and entities come from. |
| `pandas` | The ETL transform step and the data-quality report. |
| `dateparser` | Parses messy real-world dates: "c. 1347", "spring 1789", "14 July 1789 (Julian)". Saves a genuinely painful week. |
| `rapidfuzz` | Fast fuzzy matching for entity resolution — deciding "Constantinople", "Istanbul" and "Byzantium" are one place. |
| `tenacity` | Retry decorators with exponential backoff. Every external API fails intermittently. |
| `pillow` | Image resizing and format conversion for the media pipeline. |

### AI — Phases 5–7

| Package | What it does |
|---|---|
| `anthropic` / `openai` | Whichever provider you pick. Wrap it behind your own thin interface module so swapping providers touches one file. |
| `sentence-transformers` | Runs embedding models locally, free, on your Mac's GPU. `all-MiniLM-L6-v2` is 80MB and good enough to ship. How you avoid paying per embedding. |
| `tiktoken` | Counts tokens before you send them. Required for the per-session budgets from the roadmap's cost section. |
| `rank-bm25` | Classic keyword relevance scoring for the keyword half of hybrid search. Postgres full-text is the alternative — try both and measure. |
| `instructor` | Forces model output to match a Pydantic schema and retries when it doesn't. Turns "parse the JSON and hope" into a validated object. |

### Model training — do it in Colab

| Package | What it does |
|---|---|
| `scikit-learn` | TF-IDF, logistic regression, train/test splits, metrics, confusion matrices. Your baselines. |
| `transformers`, `datasets` | Hugging Face. Fine-tuning DistilBERT for the event and tone classifiers. |
| `torch` | The deep learning framework underneath. On Mac it uses Apple's Metal backend (`mps`); for real training runs use Colab's free GPU. |
| `peft` | LoRA and friends. Only if you reach parameter-efficient fine-tuning, which the roadmap says you probably shouldn't this semester. |

### Dev-only — requirements-dev.txt

| Package | What it does |
|---|---|
| `pytest`, `pytest-asyncio`, `pytest-cov` | Test runner, async support, coverage. Install in Week 2 before you have anything to test — having the harness ready removes the excuse. |
| `ruff` | Linter and formatter in one, written in Rust, effectively instant. Replaces black + flake8 + isort + pyupgrade. |
| `mypy` | Static type checking. Optional and worth turning on — catches a real class of bug before runtime. |
| `nbstripout` | Strips output from notebooks before committing. Without it one notebook produces a 4,000-line diff nobody can review. |
| `locust` | Load testing. Lets you say "120 concurrent users at 400ms p95" instead of "it feels fast". |
| `structlog`, `sentry-sdk` | Structured logging and error tracking. Structured means logs are JSON objects you query, not sentences you grep. |

### Setting it up

```bash
cd backend
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt

# freeze exact versions so CI and your laptop install the same thing
uv pip freeze > requirements.lock
```

**Pinning and lockfiles** — `fastapi` in a requirements file means "any version". Six weeks
later a new release changes a default and your project breaks with no change on your side. A
lockfile records the exact version of every package *and* every package they depend on, so an
install today and an install in March produce identical environments. This is what
"reproducible build" means, and it's the single most common cause of "but it works on my
machine".

---

## 05 · Node packages

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

> **Take the TypeScript template.** A few hours of friction in week one, paying back for the
> rest of the project: your editor knows the exact shape of every API response, renames are
> safe, and a whole category of "cannot read property of undefined" bugs stops existing. It's
> also what essentially every employer uses. You have a JavaScript background already — TS is
> that plus type annotations, not a new language.

| Package | Phase | What it does |
|---|---|---|
| `react-router-dom` | P4 | Client-side routing, so `/event/1914-sarajevo` is a real shareable URL rather than hidden app state. |
| `@tanstack/react-query` | P4 | Handles server data: fetching, caching, loading and error states, refetching, deduplication. Replaces a large amount of hand-written `useEffect` code that is always subtly wrong. Learn this one properly. |
| `maplibre-gl` + `react-map-gl` | P4 | The map. MapLibre is the open-source fork of Mapbox GL — no API key, no usage limits, no billing surprise. |
| `zustand` | P4 | Small global state store for what React Query doesn't own: selected year, active scenario, UI toggles. Far simpler than Redux and sufficient here. |
| `date-fns` | P4 | Date formatting and arithmetic. Assumes modern calendar dates — historical date handling stays server-side. |
| `tailwindcss` | P4 | Optional. Utility CSS; fast once learned, noisy in markup. CSS Modules are a fine alternative and teach you more CSS. |
| `vitest` + `@testing-library/react` | P8 | Frontend testing. Testing Library pushes you to test what the user sees rather than internal component state. |
| `eslint`, `prettier` | P1 | Lint and format — the JS equivalent of Ruff, in two tools instead of one. |

```bash
npm install react-router-dom @tanstack/react-query maplibre-gl react-map-gl zustand date-fns
npm install -D vitest @testing-library/react @testing-library/jest-dom prettier
```

---

## 06 · Accounts to create

All free. Create the first two today; the rest when the relevant phase arrives.

| Service | When | What you get and why |
|---|---|---|
| **GitHub** | Now | Public repos get unlimited Actions minutes — private repos have a monthly quota you can exhaust. |
| **GitHub Student Developer Pack** | Now | Free with a college email or ID at `education.github.com/pack`. Credits and free tiers across dozens of services — hosting, domains, monitoring, Copilot Pro. Apply on day one; verification takes a few days. |
| **Supabase** or **Neon** | P2 | Managed Postgres, free tier. Supabase fits better here — its Postgres ships with PostGIS *and* pgvector enabled, plus object storage in the same project. Neon is leaner with database branching, elegant for CI. You still develop against your local container. |
| **Cloudflare** | P3 | R2 for media storage — zero egress fees, which matters enormously when your product is thousands of large images. Pages for frontend hosting, free. |
| **Railway** / **Render** / **Fly.io** | P9 | Backend hosting. All three deploy a Dockerfile with near-zero config. Railway is smoothest to start; Fly.io gives more control and a region close to India. |
| **An LLM provider** | P5 | **Set a hard monthly spend limit the same hour you create the key.** A runaway loop in a background worker can spend a lot of money overnight, and the limit is the only thing between you and that. |
| **Hugging Face** | P5 | Embedding models, DistilBERT checkpoints, datasets. Free. |
| **Google Colab** | ML | Free GPU for fine-tuning your classifiers. A DistilBERT fine-tune on 3,000 examples takes minutes on a T4 and an unpleasant while on a laptop. |
| **Sentry** | P8 | Error tracking. Generous free tier, and how you find out about production errors from something other than a user complaining. |
| **Europeana API** | P3 | Free key for European cultural heritage media. Wikimedia Commons, the Met and the Smithsonian need no key — but Wikimedia requires a descriptive `User-Agent` header identifying your project and a contact, and will block you if you omit it. |

---

## 07 · How Git actually works

Almost everyone learns Git as four memorised commands and stays confused for years. Ten minutes
on the underlying model fixes that permanently.

Git maintains your project in **four places**. Every command moves changes between two of them.

```
Working tree  ──git add──▶  Staging area  ──git commit──▶  Local repo  ──git push──▶  Remote
(your files)                (next commit,                  (your commit                (GitHub)
                             being assembled)                history)
                                                                       ◀──git pull──
```

**Why a staging area exists at all** — it lets you commit *some* of your changes and not
others. You fixed a bug and also renamed a variable in a different file: two logical changes,
two commits. `git add -p` walks you through your changes hunk by hunk, asking what goes in this
commit. It's also the best code-review habit you can build, because you re-read every line as
you stage it.

**Commit** — a snapshot of the entire project at a moment, plus a message, plus a pointer to
its parent. Not a diff — a full snapshot, stored efficiently. Because each commit points at its
parent, history is a chain, and a branch is just a movable label pointing at one commit in it.

**Branch** — a named pointer to a commit. That's the whole implementation, which is why
creating one is instant regardless of project size.

**HEAD** — a pointer to where you currently are, normally the branch you're on. "Detached HEAD"
means it points at a commit directly rather than a branch, which happens when you check out an
old commit. Not dangerous; just means new commits won't belong to any branch until you make one.

**Merge vs rebase** — both integrate one branch into another. *Merge* creates a commit with two
parents, preserving exactly what happened. *Rebase* replays your commits on top of the other
branch, producing a straight line that reads more cleanly but rewrites commit IDs. Safe rule:
rebase your own unpushed work freely; never rebase anything you've pushed and someone else
might have pulled.

---

## 08 · Building the repository

In order. Each step is a commit.

### 1 · Decide three things first

**Name:** lowercase, hyphenated, no spaces — `counterfactual-atlas`. It becomes the URL and the
folder name.

**Visibility:** public. Unlimited free CI minutes, it forces the hygiene you're trying to learn,
and it's a portfolio piece from day one. The only rule is that nothing private ever goes in it.

**Shape:** one repository containing backend, frontend and ML — a monorepo. Three repos means
three CI setups and coordinated pull requests for a single feature. Not worth it at this size.

### 2 · Create it

```bash
mkdir counterfactual-atlas && cd counterfactual-atlas
git init -b main

gh repo create counterfactual-atlas \
  --public --source=. --remote=origin \
  --description "A virtual museum of world history with AI-driven counterfactual timelines"
```

`--source=.` links this folder to the new remote and names it `origin`, the conventional name
for "the repo I cloned from".

### 3 · Write .gitignore before anything else

This must be your first commit. Once a file is tracked, adding it to `.gitignore` does nothing
— Git only ignores files it isn't already following.

```gitignore
# --- secrets: never, under any circumstances ---
.env
.env.*
!.env.example
*.pem
*.key

# --- python ---
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage

# --- node ---
node_modules/
dist/
.vite/
*.local

# --- data & models: too big for git, belongs in object storage ---
data/raw/
data/staging/
*.csv
*.parquet
*.sqlite3
ml/checkpoints/
ml/runs/
*.pt
*.safetensors

# --- macOS & editors ---
.DS_Store
.idea/
.vscode/*
!.vscode/extensions.json
!.vscode/settings.json
```

Note the two `!` lines: ignore the whole `.vscode` folder *except* the two files that are
genuinely shared project config. Same trick keeps `.env.example` tracked while every other
`.env.*` is ignored.

```bash
git add .gitignore
git commit -m "chore: add gitignore"
```

### 4 · Create the skeleton

```bash
mkdir -p backend/app/{api,services,models,schemas,engine} \
         backend/tests backend/alembic \
         frontend ml/{notebooks,training,eval} \
         data/{ingest,raw} docs/adr infra .github/workflows

# git tracks files, not folders — an empty directory is invisible to it
find backend ml data docs -type d -empty -exec touch {}/.gitkeep \;
```

That last line is a real Git fact: Git has no concept of a directory, it tracks file paths. An
empty folder doesn't exist as far as Git is concerned, so the convention is a placeholder file.

### 5 · README — treat it as the front door

First thing a reviewer, a recruiter or future-you reads. Nine sections, in this order:

```markdown
# Counterfactual Atlas

One-sentence description. What it is, who it's for.

![screenshot](docs/screenshot.png)     <- add in week 8, it doubles engagement

## Why
The problem, in two or three sentences.

## Quickstart
The exact commands to get it running from a clean clone.
Test them by actually following them.

## Architecture
The five-tier diagram, or a link to docs/ARCHITECTURE.md

## Tech stack
Table: layer | choice | why

## Roadmap
Link to docs/ROADMAP.md, with current phase marked

## Development
How to run tests, lint, migrations, the seed script

## Licence
Code: MIT. Content: see DATA_LICENSES.md

## Acknowledgements
Data sources, with attribution
```

The Quickstart is what actually gets judged. If a stranger can't go from `git clone` to a
running app by following it exactly, the project reads as unfinished no matter how good the
code is.

### 6 · Two licences, not one

**Your code:** MIT. Permissive, one paragraph, universally understood. Add a `LICENSE` file from
GitHub's template picker.

**Your content:** different, and not yours to relicense. Wikipedia prose is CC BY-SA, a
*share-alike* licence — derived text must carry the same licence. Met and Smithsonian
open-access images are CC0, effectively public domain. Wikimedia Commons is a mix, file by
file. Keep a `DATA_LICENSES.md` recording what came from where under what terms, and store the
licence on every `media_asset` row as the roadmap's schema requires.

> **The mistake to avoid.** Slapping MIT on the repo and shipping CC BY-SA content inside it.
> You'd be claiming to license something you can't. Two files, two scopes, stated plainly — five
> minutes, and it distinguishes a considered project from a scraped one.

### 7 · .env.example

The committed template. Same keys as your real `.env`, with fake or empty values. Documents what
configuration exists without leaking any of it.

```bash
DATABASE_URL=postgresql+psycopg://atlas:devpassword@localhost:5432/atlas
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=sk-replace-me
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
S3_BUCKET=atlas-media
ENVIRONMENT=development
LOG_LEVEL=debug
SESSION_TOKEN_BUDGET=40000
```

Load it with `pydantic-settings` so a missing key crashes at startup with a clear message.

### 8 · pre-commit — the guard rail

Runs checks before a commit is created, so unformatted or broken code can't enter history in the
first place. Better than catching it in CI, because there's nothing to fix afterwards.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key

  - repo: https://github.com/kynan/nbstripout
    rev: 0.7.1
    hooks:
      - id: nbstripout
```

```bash
pre-commit install
pre-commit run --all-files
```

`check-added-large-files` and `detect-private-key` exist precisely to stop the two mistakes that
are unfixable after the fact.

### 9 · CI

The workflow from the roadmap goes in `.github/workflows/ci.yml`. Commit it in Week 2 with a
single trivial test, then watch it turn red when you deliberately break something. Seeing it
work once is what makes you trust it later.

### 10 · Push

```bash
git add .
git commit -m "chore: scaffold project structure and tooling"
git push -u origin main
```

`-u` sets the upstream once; after this, plain `git push` and `git pull` know where to go.

---

## 09 · Protecting main

Do this even though you're working alone. The point isn't to stop a colleague — it's to stop
*you*, at 1am, pushing something untested to the branch you deploy from. Constraints you set
while calm are how you survive being tired.

**Settings → Rules → Rulesets → New branch ruleset**, targeting `main`:

- **Require a pull request before merging.** Zero required approvals since you're solo — the
  value is the diff view, not the approval.
- **Require status checks to pass.** Select your CI job. This is the rule that does the work.
- **Require branches to be up to date before merging.** Stops you merging something that passed
  CI against an older main.
- **Block force pushes.** Makes history on main genuinely immutable.

Then set **Settings → General → Pull Requests** to allow squash merging only, and enable
automatic deletion of head branches.

> **The effect.** From now on, every change to main arrives through a pull request with a green
> CI badge. Six months from now your commit history is a readable record of what you built and
> in what order — and that history is, quite literally, your portfolio.

---

## 10 · Issues, labels and the board

### Labels

```bash
gh label create "area:backend"  --color 0E6B61
gh label create "area:frontend" --color 1D6FA5
gh label create "area:ml"       --color 8F6210
gh label create "area:data"     --color 6B4E9E
gh label create "type:bug"      --color A3392B
gh label create "type:feature"  --color 2D8A4E
gh label create "type:chore"    --color 6B7280
gh label create "priority:p1"   --color A3392B
gh label create "blocked"       --color 000000
```

### Milestones

One per roadmap phase — "Phase 2: Data model and API", due end of Week 4. Every issue gets a
milestone. The value shows up in Week 8, when you can see at a glance that Phase 3 has four open
issues and you're a week behind.

### The board

**Projects → New project → Board.** Columns: Backlog → In Progress → In Review → Done. One rule
matters more than the rest: **a work-in-progress limit of two.** Nothing new enters In Progress
until something leaves. More things half-done is not more progress.

### Issue and PR templates

`.github/ISSUE_TEMPLATE/bug.md` and `.github/pull_request_template.md`. The PR template is the
more useful because it prompts you to review your own work:

```markdown
## What changed

## Why

## How I tested it

## Checklist
- [ ] Tests added or updated
- [ ] No secrets, keys or large files in the diff
- [ ] Migration included if the schema changed
- [ ] I read my own diff line by line
```

That last checkbox is the one that catches bugs.

---

## 11 · Your first ten commits

If you do nothing else from this document, do this sequence — it establishes the habit of small,
labelled, reviewable changes before the project is big enough for the habit to be hard.

| # | Commit | What it contains |
|---|---|---|
| 1 | `chore: add gitignore` | Just `.gitignore`. Always first. |
| 2 | `docs: add README and licences` | README skeleton, LICENSE, DATA_LICENSES.md |
| 3 | `chore: scaffold directory structure` | Empty folders with .gitkeep |
| 4 | `chore: add python tooling` | requirements files, pyproject.toml with Ruff config, .pre-commit-config.yaml |
| 5 | `ci: lint and test on push` | .github/workflows/ci.yml plus one trivial passing test |
| 6 | `feat: add docker compose for postgres and redis` | infra/docker-compose.yml + README lines explaining how to start it |
| 7 | `feat: add fastapi app with health endpoint` | `GET /health` returning `{"status":"ok"}`, and a test asserting it |
| 8 | `feat: add settings from environment` | pydantic-settings config class, .env.example |
| 9 | `feat: scaffold react frontend` | Vite output, plus a page that fetches `/health` and displays it |
| 10 | `docs: add adr 0001 on stack selection` | Your first architecture decision record — why FastAPI, why Postgres, what you considered |

Commit 7 plus commit 9 together give you a **vertical slice**: a request travelling from the
browser, through your API, and back. It does almost nothing useful, and it's the most important
milestone of Week 2 — from here on every feature is a modification of a working system rather
than a leap towards an imagined one.

---

## 12 · When Git goes wrong

It will, and the panic is worse than the problem. Almost nothing in Git is unrecoverable if it
was ever committed.

| Situation | Fix |
|---|---|
| Staged the wrong file | `git restore --staged path/to/file` |
| Discard uncommitted edits to a file | `git restore path/to/file` — genuinely destructive, those changes are gone |
| Bad commit message, not pushed yet | `git commit --amend` |
| Forgot a file in the last commit | `git add forgotten.py && git commit --amend --no-edit` |
| Undo the last commit, keep the changes | `git reset --soft HEAD~1` |
| Undo a commit already pushed | `git revert <sha>` — new commit undoing it, never rewrites shared history |
| Committed to main by accident | `git branch feat/x && git reset --hard origin/main && git switch feat/x` |
| Stash work to switch branches | `git stash push -m "wip"` … `git stash pop` |
| Merge conflict | Open the file; `<<<<<<<` / `=======` / `>>>>>>>` markers show both versions. Edit to what you want, delete the markers, `git add` the file, `git rebase --continue` |
| "I've completely destroyed everything" | `git reflog`. Logs every position HEAD has held for 90 days, including commits you think you deleted. Find the sha, `git reset --hard <sha>`. This has saved more projects than any other command. |
| Committed a secret | Rotate the key *first*, immediately. Then clean history with `git filter-repo` if you must. Assume the key is compromised the moment it was pushed — scanners find public keys within minutes. |

**The one habit that prevents most of this:** run `git status` before every `add`, and
`git diff --staged` before every `commit`. Two seconds each. Almost every Git disaster starts
with committing something you hadn't looked at.

---

## 13 · Verify everything

Each line should print a version, not an error.

```bash
git --version
gh auth status
uv --version
node --version && npm --version
docker --version && docker compose version
code --version
jq --version
pre-commit --version
```

Then prove the services work:

```bash
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml exec db psql -U atlas -c "SELECT version();"
docker compose -f infra/docker-compose.yml exec cache redis-cli ping    # → PONG
```

### Setup checklist

- [ ] Homebrew on PATH, `brew doctor` is clean
- [ ] `git config --global user.email` matches your GitHub account
- [ ] `gh auth status` shows you logged in
- [ ] Repo created, public, first commit pushed
- [ ] `.gitignore` is commit number one
- [ ] `.env` exists locally and does *not* appear in `git status`
- [ ] `.env.example` is committed
- [ ] Postgres and Redis containers start and respond
- [ ] `vector` extension created in the database
- [ ] `pre-commit run --all-files` passes
- [ ] CI is green on main, and turns red when you break it on purpose
- [ ] Branch ruleset active on `main`
- [ ] Labels, milestones and board created
- [ ] GitHub Student Pack application submitted
- [ ] Spend limit set on your model provider account

> **One last thing.** This whole setup is Phase 1 of the roadmap — Week 2, two days of work. It
> will feel like you've built nothing, because you have built nothing yet. What you've actually
> done is make the next fourteen weeks cheaper: every lint error caught in the editor, every
> broken commit stopped by CI, every environment that matches production is time you don't spend
> debugging. That trade is the substance of software engineering, and it's the part you said you
> came here to learn.
