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
    from tools.v2.references.toptier_agencies import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


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
