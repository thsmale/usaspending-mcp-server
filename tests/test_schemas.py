from jsonschema import Draft202012Validator


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


class TestSpendingByAwardClassSchema:
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

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)


class TestSubawardsSchema:
    from tools.v2.subawards import input_schema, output_schema

    def test_input_schema(self):
        Draft202012Validator.check_schema(self.input_schema)

    def test_output_schema(self):
        Draft202012Validator.check_schema(self.output_schema)
