"""
conftest.py
Shared fixtures and configuration for pytest tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('openai.OpenAI') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Test response"
    response.choices[0].message.role = "assistant"
    response.choices[0].finish_reason = "stop"
    response.id = "test-id"
    response.created = 1234567890
    response.model = "gpt-4"
    response.usage = Mock()
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30
    return response


@pytest.fixture
def sample_chat_history():
    """Sample chat history for testing"""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]


@pytest.fixture
def sample_memory_entries():
    """Sample memory entries for testing"""
    return [
        {"timestamp": "2024-01-01T00:00:00.000Z", "action": "test1", "result": "success"},
        {"timestamp": "2024-01-01T00:01:00.000Z", "action": "test2", "result": "completed"},
        {"timestamp": "2024-01-01T00:02:00.000Z", "action": "test3", "result": "failed"}
    ]


@pytest.fixture
def mock_file_operations():
    """Mock file system operations"""
    with patch('builtins.open', create=True) as mock_open:
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                with patch('pathlib.Path.write_text') as mock_write:
                    with patch('pathlib.Path.read_text') as mock_read:
                        yield {
                            'open': mock_open,
                            'exists': mock_exists,
                            'mkdir': mock_mkdir,
                            'write_text': mock_write,
                            'read_text': mock_read
                        }


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    original_env = os.environ.copy()
    os.environ['OPENAI_API_KEY'] = 'test-api-key'
    os.environ['MODEL_NAME'] = 'gpt-4'
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'model': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 1000,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0
    }
