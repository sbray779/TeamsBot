"""
Test suite for the Teams Bot application.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from azure_openai_client import AzureOpenAIClient
from config import DefaultConfig
from auth import AuthManager, validate_bot_authentication


class TestAzureOpenAIClient:
    """Test cases for Azure OpenAI client."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock(spec=DefaultConfig)
        config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        config.AZURE_OPENAI_API_KEY = "test-key"
        config.AZURE_OPENAI_API_VERSION = "2024-02-01"
        config.AZURE_OPENAI_DEPLOYMENT_NAME = "test-deployment"
        return config

    @pytest.fixture
    def openai_client(self, mock_config):
        """Create OpenAI client for testing."""
        with patch('azure_openai_client.DefaultConfig', return_value=mock_config):
            with patch('azure_openai_client.AsyncAzureOpenAI'):
                client = AzureOpenAIClient()
                return client

    @pytest.mark.asyncio
    async def test_get_completion_success(self, openai_client):
        """Test successful completion request."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response from AI"
        
        openai_client.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await openai_client.get_completion("Test prompt")
        
        assert result == "Test response from AI"
        openai_client.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_completion_error_handling(self, openai_client):
        """Test error handling in completion request."""
        openai_client.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        result = await openai_client.get_completion("Test prompt")
        
        assert "I'm sorry, I'm having trouble" in result


class TestAuthManager:
    """Test cases for authentication manager."""

    @patch('auth.ClientSecretCredential')
    @patch('auth.DefaultAzureCredential')
    def test_service_principal_auth(self, mock_default_cred, mock_sp_cred):
        """Test service principal authentication setup."""
        with patch.object(DefaultConfig, 'AZURE_CLIENT_ID', 'test-client-id'):
            with patch.object(DefaultConfig, 'AZURE_CLIENT_SECRET', 'test-secret'):
                with patch.object(DefaultConfig, 'AZURE_TENANT_ID', 'test-tenant'):
                    auth_manager = AuthManager()
                    
                    mock_sp_cred.assert_called_once()
                    mock_default_cred.assert_not_called()

    @patch('auth.DefaultAzureCredential')
    def test_default_credential_fallback(self, mock_default_cred):
        """Test fallback to default credential."""
        with patch.object(DefaultConfig, 'AZURE_CLIENT_ID', ''):
            auth_manager = AuthManager()
            
            mock_default_cred.assert_called_once()

    def test_validate_bot_authentication_valid(self):
        """Test bot authentication validation with valid credentials."""
        result = validate_bot_authentication("valid-app-id", "valid-password")
        assert result is True

    def test_validate_bot_authentication_invalid(self):
        """Test bot authentication validation with invalid credentials."""
        result = validate_bot_authentication("", "")
        assert result is False

        result = validate_bot_authentication("app-id", "")
        assert result is False

        result = validate_bot_authentication("", "password")
        assert result is False


class TestConfiguration:
    """Test cases for configuration validation."""

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        with patch.object(DefaultConfig, 'APP_ID', 'test-app-id'):
            with patch.object(DefaultConfig, 'APP_PASSWORD', 'test-password'):
                with patch.object(DefaultConfig, 'AZURE_OPENAI_ENDPOINT', 'https://test.openai.azure.com/'):
                    with patch.object(DefaultConfig, 'AZURE_OPENAI_API_KEY', 'test-key'):
                        with patch.object(DefaultConfig, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'test-deployment'):
                            result = DefaultConfig.validate_config()
                            assert result is True

    def test_config_validation_failure(self):
        """Test configuration validation with missing values."""
        with patch.object(DefaultConfig, 'APP_ID', ''):
            result = DefaultConfig.validate_config()
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__])