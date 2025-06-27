import pandas as pd
import pytest

from app.errors import InvalidInstructionError
from app.services.instruction_executor import InstructionExecutor

executor = InstructionExecutor()


@pytest.fixture
def df_sample():
    return pd.DataFrame({
        "Client_Region": ["USA", "USA", "Canada"],
        "Earnings_USD": [100, 200, 150],
        "Experience_Level": ["Expert", "Beginner", "Expert"],
        "Job_Completed": [50, 120, 80],
        "Freelancer_ID": [1, 2, 3]
    })


def test_filter_then_aggregate_percentage(df_sample):
    instruction = {
        "operation": "filter_then_aggregate",
        "filters": {
            "Experience_Level": "Expert",
            "Job_Completed": "<100"
        },
        "groupby": None,
        "metric": "percentage_of_total",
        "target_column": "Freelancer_ID"
    }
    result = executor.execute(df_sample, instruction)
    assert result == "66.67% строк удовлетворяют условию."


def test_groupby_extreme_max(df_sample):
    instruction = {
        "operation": "groupby_extreme",
        "filters": {},
        "groupby": "Client_Region",
        "metric": "sum",
        "target_column": "Earnings_USD",
        "extreme": "max"
    }
    result = executor.execute(df_sample, instruction)
    assert "имеет max значение" in result or "имеет максимальное значение" in result


def test_invalid_missing_field(df_sample):
    instruction = {
        "operation": "filter_then_aggregate",
        "filters": {},
        "groupby": None,
        "metric": "sum"
    }
    with pytest.raises(InvalidInstructionError):
        executor.execute(df_sample, instruction)


def test_groupby_stat_mean(df_sample):
    instruction = {
        "operation": "groupby_stat",
        "filters": {},
        "groupby": "Client_Region",
        "metric": "mean",
        "target_column": "Earnings_USD"
    }
    result = executor.execute(df_sample, instruction)
    assert isinstance(result, pd.Series)
    assert "USA" in result.index


def test_groupby_compare(df_sample):
    instruction = {
        "operation": "groupby_compare",
        "filters": {},
        "groupby": "Client_Region",
        "metric": "mean",
        "target_column": "Earnings_USD"
    }
    result = executor.execute(df_sample, instruction)
    assert isinstance(result, str)
    assert "имеет на" in result
