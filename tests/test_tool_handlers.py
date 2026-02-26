import importlib
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from httpx import Response
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS
from validation import Validation

from tools.config import (
    call_tool_federal_accounts,
    call_tool_list_budget_functions,
    call_tool_major_object_class,
    call_tool_recipient,
    call_tool_spending,
    call_tool_spending_by_award,
    call_tool_spending_over_time,
    call_tool_subawards,
    call_tool_toptier_agencies,
    call_tool_total_budgetary_resources,
)


class TestBudgetFunctions(Validation):
    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_list_budget_functions()
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestFederalAccounts(Validation):
    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_federal_accounts({})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestMajorObjectClass(Validation):
    @pytest.mark.asyncio
    async def test_no_fiscal_year_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_major_object_class({})
        assert err.value.error.code == INVALID_PARAMS
        assert "fiscal_year must be provided" in err.value.error.message
        assert "fiscal year that you are querying data for" in err.value.error.data

    @pytest.mark.asyncio
    async def test_no_funding_agency_id_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_major_object_class({"fiscal_year": 420})
        assert err.value.error.code == INVALID_PARAMS
        assert "funding_agency_id must be provided" in err.value.error.message
        assert "unique USAspending.gov agency identifier" in err.value.error.data
        assert "agency_id returned in the toptier_agencies tool" in err.value.error.data

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_major_object_class(
            {
                "fiscal_year": 420,
                "funding_agency_id": 69,
            }
        )
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestRecipient(Validation):
    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_recipient({})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestTopTierAgencies(Validation):
    import tools.v2.references.toptier_agencies.toptier_agencies as toptier_agencies_module

    @pytest.mark.asyncio
    @patch(
        "tools.v2.references.toptier_agencies.toptier_agencies_custom.read_cached_file",
    )
    @patch(
        "tools.v2.references.toptier_agencies.toptier_agencies_custom.get_fresh_toptier_agencies",
    )
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call_to_api(
        self, mock_send, mock_get_fresh_toptier_agencies, mock_read_cached_file
    ):
        mock_read_cached_file.return_value = [], False
        mock_get_fresh_toptier_agencies.return_value = [], False
        mock_send.return_value = Response(status_code=200, json={})
        importlib.reload(self.toptier_agencies_module)
        res = await call_tool_toptier_agencies({})
        mock_read_cached_file.assert_called_once()
        mock_get_fresh_toptier_agencies.assert_called_once()
        mock_read_cached_file.assert_called_once()
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch(
        "tools.v2.references.toptier_agencies.toptier_agencies_custom.read_cached_file",
    )
    async def test_successful_tool_call_to_cached_file(self, mock_read_cached_file):
        mock_read_cached_file.return_value = [], True
        importlib.reload(self.toptier_agencies_module)
        res = await call_tool_toptier_agencies({})
        expected_text = '{"results":[],"page":1,"count":0,'
        expected_text += '"next":null,"previous":null,"hasNext":false,"hasPrevious":false}'
        self.validate_text_content(res, text=expected_text)
        mock_read_cached_file.assert_called_once()


class TestTotalBudgetaryResources(Validation):
    @pytest.mark.asyncio
    async def test_year_less_than_2017(self):
        with pytest.raises(McpError) as err:
            await call_tool_total_budgetary_resources({"fiscal_year": 2016})
        assert err.value.error.code == INVALID_PARAMS
        assert "fiscal_year must be 2017 or later" in err.value.error.message

    @pytest.mark.asyncio
    async def test_fiscal_period_provided_with_no_fiscal_year(self):
        with pytest.raises(McpError) as err:
            await call_tool_total_budgetary_resources({"fiscal_period": "P6"})
        assert err.value.error.code == INVALID_PARAMS
        assert "fiscal_period is provided then fiscal_year must be" in err.value.error.message

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_total_budgetary_resources({})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestSpendingByAward(Validation):
    @pytest.mark.asyncio
    async def test_no_filters_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_by_award({})
        assert err.value.error.code == INVALID_PARAMS
        assert "filters must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_no_fields_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_by_award({"filters": {"prop": "val"}})
        assert err.value.error.code == INVALID_PARAMS
        assert "fields must be provided" in err.value.error.message

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending_by_award({"filters": {"prop": "val"}, "fields": []})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestSpendingOverTime(Validation):
    @pytest.mark.asyncio
    async def test_no_group_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_over_time({})
        assert err.value.error.code == INVALID_PARAMS
        assert "group must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_no_filters_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_over_time({"group": "test"})
        assert err.value.error.code == INVALID_PARAMS
        assert "filters must be provided" in err.value.error.message

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending_over_time({"group": "test", "filters": {"prop": "val"}})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestSpending(Validation):
    @pytest.mark.asyncio
    async def test_no_type_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending({})
        assert err.value.error.code == INVALID_PARAMS
        assert "type must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_invalid_date_range_less_than(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending({"type": "test", "filters": {"fy": "2017", "quarter": "1"}})
        assert err.value.error.code == INVALID_PARAMS
        assert "Data is not available prior to FY 2017 Q2" in err.value.error.message

    @pytest.mark.asyncio
    async def test_invalid_date_range_less_than_period(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending({"type": "test", "filters": {"fy": "2017", "period": "1"}})
        assert err.value.error.code == INVALID_PARAMS
        assert "Data is not available prior to FY 2017 Q2" in err.value.error.message

    @pytest.mark.asyncio
    @freeze_time("2026-01-30")
    async def test_invalid_date_range_greater_than(self):
        # Invalid date range because data is not reported til 45 days after the previous fq closes
        with pytest.raises(McpError) as err:
            await call_tool_spending({"type": "test", "filters": {"fy": "2026", "quarter": "1"}})
        assert err.value.error.code == INVALID_PARAMS
        assert "Most recently available data is from FY 2025 Q4" in err.value.error.message

    @freeze_time("2026-01-30")
    @pytest.mark.asyncio
    async def test_invalid_date_range_greater_than_period(self):
        # Invalid date range because data is not reported til 45 days after the previous fq closes
        with pytest.raises(McpError) as err:
            await call_tool_spending({"type": "test", "filters": {"fy": "2026", "period": "1"}})
        assert err.value.error.code == INVALID_PARAMS
        assert "Most recently available data is from FY 2025 Q4" in err.value.error.message

    @pytest.mark.asyncio
    @freeze_time("2026-01-30")
    @patch(
        "utils.http.client.send",
    )
    async def test_valid_date_range(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending({"type": "test", "filters": {"fq": "2025", "quarter": "4"}})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending({"type": "test", "filters": {"prop": "val"}})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")


class TestSubawards(Validation):
    arguments = {}

    @pytest.mark.asyncio
    async def test_no_page_provided(self):
        with pytest.raises(McpError) as err:
            await call_tool_subawards(self.arguments)
        assert err.value.error.code == INVALID_PARAMS
        assert "page must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_no_sort_provided(self):
        self.arguments["page"] = 69
        with pytest.raises(McpError) as err:
            await call_tool_subawards(self.arguments)
        assert err.value.error.code == INVALID_PARAMS
        assert "sort must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_no_order_provided(self):
        self.arguments["sort"] = "test"
        with pytest.raises(McpError) as err:
            await call_tool_subawards(self.arguments)
        assert err.value.error.code == INVALID_PARAMS
        assert "order must be provided" in err.value.error.message

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_successful_tool_call(self, mock_send):
        self.arguments["order"] = "test"
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_subawards(self.arguments)
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")
