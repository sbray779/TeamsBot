"""
Utilities for handling authentication and security.
"""

import logging
from typing import Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from config import DefaultConfig

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication for Azure services."""

    def __init__(self):
        """Initialize the authentication manager."""
        self.config = DefaultConfig()
        self.credential = None
        self._setup_credential()

    def _setup_credential(self):
        """Setup Azure credential based on available configuration."""
        try:
            if (self.config.AZURE_CLIENT_ID and 
                self.config.AZURE_CLIENT_SECRET and 
                self.config.AZURE_TENANT_ID):
                # Use service principal authentication
                self.credential = ClientSecretCredential(
                    tenant_id=self.config.AZURE_TENANT_ID,
                    client_id=self.config.AZURE_CLIENT_ID,
                    client_secret=self.config.AZURE_CLIENT_SECRET
                )
                logger.info("Using service principal authentication")
            else:
                # Use default credential chain (managed identity, CLI, etc.)
                self.credential = DefaultAzureCredential()
                logger.info("Using default Azure credential")
        except Exception as e:
            logger.error(f"Failed to setup Azure credential: {str(e)}")
            raise

    def get_credential(self):
        """Get the Azure credential."""
        return self.credential

    def get_secret_from_keyvault(self, vault_url: str, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret from Azure Key Vault.
        
        Args:
            vault_url: The URL of the Key Vault
            secret_name: The name of the secret to retrieve
            
        Returns:
            The secret value or None if not found
        """
        try:
            client = SecretClient(vault_url=vault_url, credential=self.credential)
            secret = client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from Key Vault: {str(e)}")
            return None


def validate_bot_authentication(app_id: str, app_password: str) -> bool:
    """
    Validate bot authentication credentials.
    
    Args:
        app_id: Microsoft App ID
        app_password: Microsoft App Password
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if not app_id or not app_password:
        logger.error("Bot authentication credentials are missing")
        return False
    
    # Additional validation logic can be added here
    return True