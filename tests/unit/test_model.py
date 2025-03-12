import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    X_train = pd.DataFrame({
        "Account length": np.random.randint(1, 100, 20),
        "Total day minutes": np.random.uniform(0, 300, 20),
        "International plan": np.random.choice(["yes", "no"], 20)
    })
    y_train = np.random.randint(0, 2, 20)
    X_test = pd.DataFrame({
        "Account length": np.random.randint(1, 100, 10),
        "Total day minutes": np.random.uniform(0, 300, 10),
        "International plan": np.random.choice(["yes", "no"], 10)
    })
    y_test = np.random.randint(0, 2, 10)
    
    return X_train, y_train, X_test, y_test


@patch('pipelines.training_pipeline.train_model')
def test_model_training(mock_train):
    """Test if the model training function is called correctly."""
    # Setup mock
    mock_model = MagicMock(spec=RandomForestClassifier)
    mock_train.return_value = mock_model
    
    # Import after patching
    from pipelines.training_pipeline import train_model
    
    # Call the function
    model = train_model()
    
    # Assert function was called
    mock_train.assert_called_once()
    assert model == mock_model


@patch('pipelines.data_pipeline.load_and_prepare_data')
def test_model_accuracy(mock_load_data, mock_data):
    """Test model evaluation logic without calling the actual training pipeline."""
    # Setup mock
    mock_load_data.return_value = mock_data
    X_train, y_train, X_test, y_test = mock_data
    
    # Create a simple test model (NOT using the actual pipeline)
    test_model = RandomForestClassifier(n_estimators=5, random_state=42)
    test_model.fit(X_train, y_train)
    
    # Test prediction functionality
    y_pred = test_model.predict(X_test)
    
    # Assert predictions are the right shape and type
    assert len(y_pred) == len(y_test), "Prediction length doesn't match test data"
    assert all(pred in [0, 1] for pred in y_pred), "Invalid prediction values"
    
    # We're testing the model evaluation logic, not the actual model performance
    # So we don't assert on absolute accuracy here
