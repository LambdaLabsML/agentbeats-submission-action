# AgentBeats Competition Submission Action

GitHub Action for submitting your solution to the AgentBeats Competition 2026.

**What this action does:**

1. **Validates your Python files**:
    Checks for syntax errors to prevent broken submissions
2. **Optionally tests your solution**:
    Runs your agent against a real scenario to catch runtime errors before submission. Requires `OPENAI_API_KEY` and `OPENAI_BASE_URL` secrets; disable with `run_tests: 'false'`
3. **Packages and uploads**:
    Creates a zip of your code and submits it to the competition backend

---

## Repository Structure

Your repository should contain your attacker and/or defender code:

```
your-repo/
├── .github/workflows/submit.yml
├── scenarios/security_arena/agents/
│   ├── attacker/
│   │   └── ... your attacker code ...
│   └── defender/
│       └── ... your defender code ...
```

---

## Setup

### 1. Add Your API Key

Go to your repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- Name: `COMPETITION_API_KEY`
- Value: Your team's API key from the competition website

### 2. Create the Workflow

Create `.github/workflows/submit.yml`:

```yaml
name: Submit Solution

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  submit-attacker:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[submit]') || contains(github.event.head_commit.message, '[submit-attacker]')

    steps:
      - uses: actions/checkout@v4

      - name: Submit Attacker
        uses: LambdaLabsML/agentbeats-submission-action@main
        with:
          api_key: ${{ secrets.COMPETITION_API_KEY }}
          submission_endpoint: ${{ secrets.SUBMISSION_ENDPOINT }}
          role: 'attacker'
          submission_path: './scenarios/security_arena/agents/attacker'

  submit-defender:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[submit]') || contains(github.event.head_commit.message, '[submit-defender]')

    steps:
      - uses: actions/checkout@v4

      - name: Submit Defender
        uses: LambdaLabsML/agentbeats-submission-action@main
        with:
          api_key: ${{ secrets.COMPETITION_API_KEY }}
          submission_endpoint: ${{ secrets.SUBMISSION_ENDPOINT }}
          role: 'defender'
          submission_path: './scenarios/security_arena/agents/defender'
```

### 3. Submit

```bash
git commit -m "[submit] my solution"          # submits both
git commit -m "[submit-attacker] new strategy" # submits attacker only
git commit -m "[submit-defender] fixed bug"    # submits defender only
git push
```

---

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `api_key` | ✅ | — | Your team's API key |
| `role` | ✅ | — | `'attacker'` or `'defender'` |
| `submission_endpoint` | ✅ | — | Competition endpoint URL |
| `submission_path` | ❌ | `'./src'` | Path to your agent code (see below) |
| `run_tests` | ❌ | `'true'` | Integration test mode (see below) |
| `openai_api_key` | ❌ | — | Your LLM API key (required unless `run_tests: 'off'`) |
| `openai_base_url` | ❌ | — | Your LLM server URL (required unless `run_tests: 'off'`) |
| `print_info` | ❌ | `'true'` | Print detailed submission output |
| `scenario` | ❌ | `'thingularity'` | Scenario to test against (see below) |

### About `run_tests`

Controls whether and how integration tests are run before submission:

| Value | Description |
|-------|-------------|
| `'off'` or `'false'` | Skip testing entirely |
| `'warn'` or `'true'` | **(Default)** Run tests; if they fail, show a warning but still submit |
| `'required'` or `'block'` | Run tests; if they fail, block the submission |

**Note:** The default changed from `'false'` to `'true'` (warn mode). This helps catch issues early while still allowing submissions when tests fail unexpectedly.

### About `submission_path`

This is the folder that gets uploaded and used for evaluation. Only the contents of this folder are submitted — you don't need to include the full repository structure.

Your agent code in this folder should be self-contained and follow the expected agent interface.

### About `scenario`

Choose which scenario to test against. Available options:

| Value | Description |
|-------|-------------|
| `thingularity` | (Default) IoT device management scenario |
| `portfolioiq` | Financial portfolio assistant scenario |
| `medical` | Medical records assistant scenario |
| `gymjailbreak` | Fitness coaching assistant scenario |
| `resume_downgrade` | Resume evaluation assistant scenario |
| `all` | Run all scenarios |

Example:
```yaml
- name: Submit with specific scenario
  uses: LambdaLabsML/agentbeats-submission-action@main
  with:
    api_key: ${{ secrets.COMPETITION_API_KEY }}
    submission_endpoint: ${{ secrets.SUBMISSION_ENDPOINT }}
    role: 'defender'
    submission_path: './scenarios/security_arena/agents/defender'
    run_tests: 'true'
    scenario: 'portfolioiq'  # or 'all' for all scenarios
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    openai_base_url: ${{ secrets.OPENAI_BASE_URL }}
```

### Integration Testing

By default (`run_tests: 'true'`), tests run before submission. If tests fail, a warning is shown but submission continues. Use `run_tests: 'required'` to block submissions when tests fail, or `run_tests: 'off'` to skip testing.

This requires an LLM backend. Add these secrets pointing to your own server (e.g., a Lambda Labs instance running vLLM):

- `OPENAI_API_KEY`: Your API key (or any string if your server doesn't require auth)
- `OPENAI_BASE_URL`: Your server URL (e.g., `http://your-server-ip:8000/v1`)

```yaml
- name: Submit Attacker (with required testing)
  uses: LambdaLabsML/agentbeats-submission-action@main
  with:
    api_key: ${{ secrets.COMPETITION_API_KEY }}
    submission_endpoint: ${{ secrets.SUBMISSION_ENDPOINT }}
    role: 'attacker'
    submission_path: './scenarios/security_arena/agents/attacker'
    run_tests: 'required'  # block submission if tests fail
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    openai_base_url: ${{ secrets.OPENAI_BASE_URL }}
```

---

## Trigger Options

**Commit message trigger** (default): Only runs when commit contains `[submit]`
```yaml
if: contains(github.event.head_commit.message, '[submit]')
```

**Manual trigger**: Run from GitHub UI via Actions → Run workflow
```yaml
on:
  workflow_dispatch:
```

**Every push**: Submit on every push to main (remove the `if:` line)

---

## Example Workflows

| Workflow | Description |
|----------|-------------|
| [simple-attacker.yml](example-workflows/simple-attacker.yml) | Attacker only, no testing |
| [simple-defender.yml](example-workflows/simple-defender.yml) | Defender only, no testing |
| [both-roles.yml](example-workflows/both-roles.yml) | Both roles, no testing |
| [with-testing.yml](example-workflows/with-testing.yml) | Single role with testing |
| [both-roles-with-testing.yml](example-workflows/both-roles-with-testing.yml) | Both roles with testing |
| [fork-agentbeats-lambda.yml](example-workflows/fork-agentbeats-lambda.yml) | For agentbeats-lambda structure |
| [manual-trigger-only.yml](example-workflows/manual-trigger-only.yml) | Manual trigger with role selection |

All workflows (except manual-trigger-only) support selective triggers: `[submit]`, `[submit-attacker]`, `[submit-defender]`.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No Python files found" | Check `submission_path` points to your code |
| "Syntax error" | Fix the Python error shown in logs |
| "Invalid API key" | Check your `COMPETITION_API_KEY` secret |
| "Integration test failed" | See error details in the GitHub Actions summary |

---

## Good Luck! 🏆

