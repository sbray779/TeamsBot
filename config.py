"""
Configuration settings for the Teams Bot application.
"""

import os
from typing import Optional


class DefaultConfig:
    """Bot Configuration"""

    PORT = int(os.environ.get("PORT", 3978))
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")

    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    # Azure Authentication
    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")

    # Use a managed identity instead of the MicrosoftAppPassword (optional)
    # If set to a truthy value ("1", "true", "yes"), the app will skip
    # requiring MicrosoftAppPassword and assume the hosting environment
    # (App Service) has a system/user-assigned managed identity configured.
    USE_MANAGED_IDENTITY = os.environ.get("USE_MANAGED_IDENTITY", "false").lower() in ["1", "true", "yes"]

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_settings = [
            "APP_ID",
            # APP_PASSWORD is required only when not using managed identity
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(cls, setting):
                missing_settings.append(setting)

        # Special-case: if managed identity is not enabled, require APP_PASSWORD
        if not cls.USE_MANAGED_IDENTITY and not cls.APP_PASSWORD:
            missing_settings.insert(0, "APP_PASSWORD")
        
        if missing_settings:
            print(f"Missing required configuration: {', '.join(missing_settings)}")
            return False
        
        return True