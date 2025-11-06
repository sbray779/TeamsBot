# TeamsBot

TeamsBot is a Python application designed to interact with Microsoft Teams using Azure OpenAI services. It includes infrastructure-as-code templates for Azure deployment and scripts for automated provisioning.

## Features
- Microsoft Teams bot integration
- Azure OpenAI client support
- Authentication and configuration modules
- Infrastructure deployment using Bicep
- Deployment scripts for PowerShell and Bash
- Unit tests for bot functionality

## Project Structure
```
app.py                   # Main application entry point
auth.py                  # Authentication logic
azure_openai_client.py   # Azure OpenAI client integration
config.py                # Configuration management
requirements.txt         # Python dependencies
requirements-dev.txt     # Development dependencies
test_bot.py              # Unit tests
infrastructure/          # Bicep templates and parameters
scripts/                 # Deployment scripts
```

## Getting Started
1. **Install dependencies**:
   ```pwsh
   pip install -r requirements.txt
   ```
2. **Configure environment**:
   - Update `config.py` with your Azure and Teams settings.
3. **Deploy infrastructure**:
   - Use the scripts in `scripts/` or deploy manually with Bicep files in `infrastructure/`.
4. **Run the bot**:
   ```pwsh
   python app.py
   ```

## Testing
Run unit tests with:
```pwsh
python test_bot.py
```

## Deployment
- Infrastructure is defined in Bicep (`infrastructure/`).
- Use `deploy.ps1` (PowerShell) or `deploy.sh` (Bash) for automated deployment.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
