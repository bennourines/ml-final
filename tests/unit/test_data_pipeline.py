import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np


@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    X_train = pd.DataFrame({
        "Account length": np.random.randint(1, 100, 10),
        "Total day minutes": np.random.uniform(0, 300, 10),
        "International plan": np.random.choice(["yes", "no"], 10)
    })
    y_train = np.random.randint(0, 2, 10)
    X_test = pd.DataFrame({
        "Account length": np.random.randint(1, 100, 5),
        "Total day minutes": np.random.uniform(0, 300, 5),
        "International plan": np.random.choice(["yes", "no"], 5)
    })
    y_test = np.random.randint(0, 2, 5)
    
    return X_train, y_train, X_test, y_test


@patch('pipelines.data_pipeline.load_and_prepare_data')
def test_data_loading(mock_load_data, mock_data):
    """Test if data is loaded correctly."""
    # Setup mock
    mock_load_data.return_value = mock_data
    
    # Import after patching
    from pipelines.data_pipeline import load_and_prepare_data
    
    # Call the function
    X_train, y_train, X_test, y_test = load_and_prepare_data()

    # Check if data is not empty
    assert len(X_train) > 0, "Training data is empty"
    assert len(y_train) > 0, "Training labels are empty"
    assert len(X_test) > 0, "Test data is empty"
    assert len(y_test) > 0, "Test labels are empty"
    
    # Verify the function was called
    mock_load_data.assert_called_once()


@patch('pipelines.data_pipeline.load_and_prepare_data')
def test_feature_columns(mock_load_data, mock_data):
    """Test if feature columns are correct."""
    # Setup mock
    mock_load_data.return_value = mock_data
    
    # Import after patching
    from pipelines.data_pipeline import load_and_prepare_data
    
    # Call the function
    X_train, _, _, _ = load_and_prepare_data()

    # Use the exact column names from your dataset
    expected_columns = ["Account length", "Total day minutes", "International plan"]
    for col in expected_columns:
        assert col in X_train.columns, f"Missing column: {col}"
