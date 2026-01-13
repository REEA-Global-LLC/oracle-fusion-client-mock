"""Pytest configuration and fixtures for tests."""

import pytest

from oracle_fusion_mock import OracleFusionMockClient
from oracle_fusion_mock.data_loader import MockDataLoader


@pytest.fixture(autouse=True)
def reset_data_loader():
    """Reset the data loader singleton before each test."""
    MockDataLoader.reset()
    yield
    MockDataLoader.reset()


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return OracleFusionMockClient()
