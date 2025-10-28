# TeamsBot

A lightweight Teams bot project that integrates with Azure OpenAI services.

This repository contains the bot application, authentication helpers, an Azure OpenAI client wrapper, deployment scripts, and Azure Bicep infrastructure definitions to deploy the service.

## Contents

- `app.py` — main bot application entrypoint
- `auth.py` — authentication helper(s)
- `azure_openai_client.py` — wrapper/client for Azure OpenAI interactions
- `config.py` — configuration (environment variables / settings)
- `test_bot.py` — simple tests for the bot
- `requirements.txt` — Python runtime dependencies
- `requirements-dev.txt` — development/test dependencies
- `infrastructure/` — Bicep templates for Azure deployment
  - `main.bicep`, `main.parameters.json`, `service-principal.bicep`
- `scripts/` — convenience scripts
  - `deploy.ps1` — PowerShell deploy helper
  - `deploy.sh` — Bash deploy helper


## Quick start (Windows / PowerShell)

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure environment variables

Open `config.py` to see which environment variables the app expects. Typical variables you might need to set (replace names/values according to `config.py` and your Azure resources):

- `AZURE_OPENAI_ENDPOINT` — your Azure OpenAI endpoint (if applicable)
- `AZURE_OPENAI_API_KEY` — API key for Azure OpenAI or other name used in `config.py`
- `TEAMS_APP_ID` and `TEAMS_APP_PASSWORD` — if the bot uses Teams app credentials
- Any other variables referenced in `config.py`

Set them in PowerShell (example):

```powershell
$env:AZURE_OPENAI_API_KEY = "your_key_here"
$env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
# etc.
```

4. Run the app

```powershell
python app.py
```

Watch the console logs for startup messages and port information.


## Running tests

This repo includes a basic test file, `test_bot.py`. Run tests with pytest.

```powershell
pip install -r requirements-dev.txt
pytest -q
```


## Deploying to Azure (high-level)

This repo includes Bicep templates under `infrastructure/` and convenience scripts in `scripts/`.

Common steps (you may already have scripts that wrap these):

1. Login to Azure CLI

```powershell
az login
```

2. (Optional) Select subscription

```powershell
az account set --subscription "<SUBSCRIPTION_ID_OR_NAME>"
```

3. Run the PowerShell deploy script (uses the Bicep templates)

```powershell
.\scripts\deploy.ps1
```

Or with Bash (Linux/macOS)

```bash
./scripts/deploy.sh
```

Notes:
- Inspect `infrastructure/main.bicep` and `infrastructure/main.parameters.json` to understand resources created and parameters required.
- The deploy scripts may require certain environment variables or inputs (service principal credentials, resource group name, location, etc.). Open them to see required parameters.


## Configuration details

The project reads configuration from environment variables via `config.py`. The file defines the following keys (name = environment variable, default if provided):

- PORT = `PORT` (default: 3978)
- APP_ID = `MicrosoftAppId` (no default — required)
- APP_PASSWORD = `MicrosoftAppPassword` (no default — required)
- APP_TYPE = `MicrosoftAppType` (default: "MultiTenant")
- APP_TENANTID = `MicrosoftAppTenantId` (no default)

Azure OpenAI configuration:

- AZURE_OPENAI_ENDPOINT = `AZURE_OPENAI_ENDPOINT` (no default — required)
- AZURE_OPENAI_API_KEY = `AZURE_OPENAI_API_KEY` (no default — required)
- AZURE_OPENAI_API_VERSION = `AZURE_OPENAI_API_VERSION` (default: "2024-02-01")
- AZURE_OPENAI_DEPLOYMENT_NAME = `AZURE_OPENAI_DEPLOYMENT_NAME` (default: "gpt-4")

Azure authentication (optional depending on deployment):

- AZURE_CLIENT_ID = `AZURE_CLIENT_ID`
- AZURE_CLIENT_SECRET = `AZURE_CLIENT_SECRET`
- AZURE_TENANT_ID = `AZURE_TENANT_ID`

Notes:
- The code expects `MicrosoftAppId` and `MicrosoftAppPassword` (Teams app credentials) and the Azure OpenAI endpoint/key to be present for normal operation. The `DefaultConfig.validate_config()` helper checks for required settings.
- Set these variables in your environment or CI/CD secret store before running the app. Example PowerShell commands are shown in the Quick start section.


## Contributing

- Create a new branch for features or fixes.
- Keep changes small and focused.
- Add or update tests when touching logic.
- Open a PR with a clear description.


## Troubleshooting

- If dependency installation fails, ensure you are using a supported Python version (check `requirements.txt` for version pins) and that your virtual environment is activated.
- For Azure deployment issues, increase verbosity in the Azure CLI or inspect deployment logs in the portal.
- If `app.py` exits immediately, check required environment variables are present.


## License

If this repository does not include a LICENSE file, check with the repository owner before reusing code. Add a `LICENSE` file if you intend to make the project open source.


## Where to look next

- Inspect `config.py` for exact env var names and behavior.
- Inspect `scripts/deploy.ps1` and `scripts/deploy.sh` to understand deployment arguments and pre-reqs.
- Review `infrastructure/` Bicep files if you plan to customize resource deployment.


---

If you'd like, I can:
- make the README more specific by extracting exact env var names from `config.py` and adding them to the "Configuration" section, or
- add a short `README` section showing example request/response flows for the bot.

Tell me which one you'd prefer next and I'll update the README accordingly.