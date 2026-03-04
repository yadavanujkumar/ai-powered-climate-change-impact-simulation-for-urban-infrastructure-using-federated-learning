import pytest
from unittest.mock import patch, MagicMock
from workflow import Workflow, WorkflowError, Branch, Task

# Constants for test data
VALID_INPUT_DATA = {
    "temperature": 25,
    "humidity": 60,
    "infrastructure_type": "road",
}

INVALID_INPUT_DATA = {
    "temperature": -100,  # Invalid temperature
    "humidity": 150,      # Invalid humidity
    "infrastructure_type": "unknown",  # Invalid type
}

@pytest.fixture
def workflow_instance():
    """Fixture to create a Workflow instance for testing."""
    return Workflow()

@pytest.fixture
def mock_external_service():
    """Fixture to mock external service calls."""
    with patch('workflow.ExternalService') as mock_service:
        yield mock_service

@pytest.mark.parametrize("input_data, expected_result", [
    (VALID_INPUT_DATA, "success"),
    ({"temperature": 30, "humidity": 70, "infrastructure_type": "bridge"}, "success"),
])
def test_workflow_happy_path(workflow_instance, input_data, expected_result):
    """Test happy path scenarios with valid input data."""
    result = workflow_instance.run(input_data)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

def test_workflow_invalid_input(workflow_instance):
    """Test error handling for invalid input data."""
    with pytest.raises(WorkflowError) as exc_info:
        workflow_instance.run(INVALID_INPUT_DATA)
    assert "Invalid input data" in str(exc_info.value), "Expected WorkflowError for invalid input data"

@pytest.mark.parametrize("input_data", [
    {"temperature": 0, "humidity": 0, "infrastructure_type": "road"},  # Boundary condition
    {"temperature": 100, "humidity": 100, "infrastructure_type": "bridge"},  # Boundary condition
])
def test_workflow_boundary_conditions(workflow_instance, input_data):
    """Test boundary conditions for input data."""
    result = workflow_instance.run(input_data)
    assert result == "success", f"Expected success for boundary input, but got {result}"

def test_workflow_branch_logic(workflow_instance):
    """Test branching logic in the workflow."""
    input_data = {"temperature": 20, "humidity": 50, "infrastructure_type": "park"}
    result = workflow_instance.run(input_data)
    assert result == "branch_success", "Expected branch success for park infrastructure"

def test_workflow_failure_scenario(workflow_instance, mock_external_service):
    """Test failure scenario when external service fails."""
    mock_external_service.return_value.perform_task.side_effect = Exception("Service failure")
    
    with pytest.raises(WorkflowError) as exc_info:
        workflow_instance.run(VALID_INPUT_DATA)
    assert "Service failure" in str(exc_info.value), "Expected WorkflowError for external service failure"

def test_workflow_performance(workflow_instance):
    """Test performance of the workflow under load."""
    import time
    start_time = time.time()
    
    for _ in range(1000):  # Simulate load
        workflow_instance.run(VALID_INPUT_DATA)
    
    duration = time.time() - start_time
    assert duration < 2, "Performance test failed: took too long to process"

def test_workflow_integration(mock_external_service):
    """Integration test for the workflow with external service."""
    mock_external_service.return_value.perform_task.return_value = "task_completed"
    workflow = Workflow()
    
    result = workflow.run(VALID_INPUT_DATA)
    assert result == "success", "Expected success from integration test"

def test_workflow_task_execution(workflow_instance):
    """Test individual task execution within the workflow."""
    task = Task(name="Test Task")
    result = task.execute(VALID_INPUT_DATA)
    assert result == "task_completed", "Expected task to complete successfully"

def test_workflow_task_failure(workflow_instance):
    """Test task failure scenario."""
    task = Task(name="Failing Task")
    with pytest.raises(Exception) as exc_info:
        task.execute({"invalid": "data"})
    assert "Task execution failed" in str(exc_info.value), "Expected task execution failure"

@pytest.mark.parametrize("input_data", [
    {"temperature": 25, "humidity": 60, "infrastructure_type": "road"},
    {"temperature": 30, "humidity": 70, "infrastructure_type": "bridge"},
])
def test_workflow_multiple_scenarios(workflow_instance, input_data):
    """Test multiple scenarios with valid input data."""
    result = workflow_instance.run(input_data)
    assert result == "success", f"Expected success for input {input_data}, but got {result}"