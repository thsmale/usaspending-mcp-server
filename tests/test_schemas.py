import importlib
from unittest.mock import patch

import pytest
from jsonschema import Draft202012Validator, ValidationError


class TestListBudgetFunctionSchemas:
    from tools.v2.budget_functions.list_budget_functions import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestMajorObjectClassSchema:
    from tools.v2.financial_spending.major_object_class import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestTopTierAgenciesSchema:
    """
    Used to refresh the module.
    So that the below tests can recall the module level function.
    Without it, caching would prevent the import from occurring again.
    """

    import tools.v2.references.toptier_agencies as toptier_agencies_module

    def test_original_input_schema(self):
        from tools.v2.references.toptier_agencies import original_input_schema

        Draft202012Validator.check_schema(original_input_schema)

    def test_original_output_schema(self):
        from tools.v2.references.toptier_agencies import original_output_schema

        Draft202012Validator.check_schema(original_output_schema)

    @patch(
        "tools.v2.references.toptier_agencies_custom.read_cached_file",
    )
    @patch(
        "tools.v2.references.toptier_agencies_custom.get_fresh_toptier_agencies",
    )
    def test_no_cache_input_schema(self, mock_get_fresh_toptier_agencies, mock_read_cached_file):
        mock_read_cached_file.return_value = [], False
        mock_get_fresh_toptier_agencies.return_value = [], False
        importlib.reload(self.toptier_agencies_module)
        from tools.v2.references.toptier_agencies import input_schema, original_input_schema

        mock_read_cached_file.assert_called_once()
        mock_get_fresh_toptier_agencies.assert_called_once()
        Draft202012Validator.check_schema(input_schema)
        assert input_schema == original_input_schema

    @patch(
        "tools.v2.references.toptier_agencies_custom.read_cached_file",
    )
    @patch(
        "tools.v2.references.toptier_agencies_custom.get_fresh_toptier_agencies",
    )
    def test_no_cache_output_schema(self, mock_get_fresh_toptier_agencies, mock_read_cached_file):
        mock_read_cached_file.return_value = [], False
        mock_get_fresh_toptier_agencies.return_value = [], False
        importlib.reload(self.toptier_agencies_module)
        from tools.v2.references.toptier_agencies import original_output_schema, output_schema

        mock_read_cached_file.assert_called_once()
        mock_get_fresh_toptier_agencies.assert_called_once()
        Draft202012Validator.check_schema(output_schema)
        assert output_schema == original_output_schema

    @patch(
        "tools.v2.references.toptier_agencies_custom.read_cached_file",
    )
    def test_cached_file_input_schema(self, mock_read_cached_file):
        mock_read_cached_file.return_value = [], True
        importlib.reload(self.toptier_agencies_module)
        from tools.v2.references.toptier_agencies import input_schema, original_input_schema

        mock_read_cached_file.assert_called_once()
        Draft202012Validator.check_schema(input_schema)
        assert input_schema != original_input_schema
        assert "keyword" in input_schema["properties"]
        assert "limit" in input_schema["properties"]
        assert "page" in input_schema["properties"]

    @patch(
        "tools.v2.references.toptier_agencies_custom.read_cached_file",
    )
    def test_cached_file_output_schema(self, mock_read_cached_file):
        mock_read_cached_file.return_value = [], True
        importlib.reload(self.toptier_agencies_module)
        from tools.v2.references.toptier_agencies import original_output_schema, output_schema

        mock_read_cached_file.assert_called_once()
        Draft202012Validator.check_schema(output_schema)
        assert output_schema != original_output_schema
        assert "previous" in output_schema["properties"]
        assert "count" in output_schema["properties"]
        assert "limit" in output_schema["properties"]
        assert "hasNext" in output_schema["properties"]
        assert "page" in output_schema["properties"]
        assert "hasPrevious" in output_schema["properties"]
        assert "next" in output_schema["properties"]


class TestTotalBudgetaryResources:
    from tools.v2.references.total_budgetary_resources import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestSpendingByAwardSchema:
    from tools.v2.search.spending_by_award import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestSpendingOverTimeSchema:
    from tools.v2.search.spending_over_time import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestFederalAccountsSchema:
    from tools.v2.federal_accounts import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestRecipientSchema:
    from tools.v2.recipient import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestSpendingSchema:
    from tools.v2.spending import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_input_schema_no_fy(self):
        with pytest.raises(ValidationError) as err:
            Draft202012Validator(self.input_schema).validate({"type": "award", "filters": {}})
        assert "is not valid under any of the given schemas" in err.value.message
        assert "anyOf" == err.value.validator

    def test_input_schema_short_fy(self):
        with pytest.raises(ValidationError) as err:
            Draft202012Validator(self.input_schema).validate(
                {"type": "award", "filters": {"fy": "17", "quarter": "1"}}
            )
        assert "'17' is too short" == err.value.message
        assert "minLength" == err.value.validator
        assert 4 == err.value.validator_value

    def test_input_schema_fy_no_quarter_or_period(self):
        with pytest.raises(ValidationError) as err:
            Draft202012Validator(self.input_schema).validate(
                {"type": "award", "filters": {"fy": "2017"}}
            )
        assert "is not valid under any of the given schemas" in err.value.message
        assert "anyOf" == err.value.validator

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestSubawardsSchema:
    from tools.v2.subawards import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)
