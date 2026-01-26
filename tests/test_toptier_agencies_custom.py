from copy import deepcopy

import pytest
from httpx import Response
from mcp.shared.exceptions import McpError
from validation import Validation

from tools.v2.references.toptier_agencies import (
    filename,
    original_output_schema,
)
from tools.v2.references.toptier_agencies_custom import (
    create_mcp_response,
    filter_by_keyword,
    get_pagination,
    read_cached_file,
    sort_results,
)
from utils.http import HttpClient


class TestPagination:
    # Pagination tests
    # It is uncertain this will work with multiple clients
    def test_invalid_limit_page(self):
        results, _ = get_pagination([], 0, 0)
        assert len(results) == 0

    def test_out_of_bounds(self):
        results = list(range(5))
        results, _ = get_pagination(results, 10, 10)
        assert len(results) == 0

    def test_successful_pagination(self):
        results = list(range(101))
        page = 1
        results_len = len(results)
        for i in range(0, len(results), 5):
            paginated_results, metadata = get_pagination(results, 5, page)
            assert metadata["page"] == page
            assert metadata["count"] == results_len
            # Validate first page
            if page == 1:
                value = i
                for paginated_result in paginated_results:
                    assert paginated_result == value
                    assert metadata["next"] == page + 1
                    assert metadata["previous"] is None
                    assert metadata["hasNext"] is True
                    assert metadata["hasPrevious"] is False
                    value += 1
            # Validate last page
            elif page == 21:
                assert len(paginated_results) == 1
                assert paginated_results[0] == 100
                assert metadata["next"] is None
                assert metadata["previous"] == page - 1
                assert metadata["hasNext"] is False
                assert metadata["hasPrevious"] is True
            # Validate middle pages
            else:
                value = i
                for paginated_result in paginated_results:
                    assert paginated_result == value
                    assert metadata["next"] == page + 1
                    assert metadata["previous"] == page - 1
                    assert metadata["hasNext"] is True
                    assert metadata["hasPrevious"] is True
                    value += 1
            page += 1


class TestFilterByKeyword:
    # toptier_agencies should not be changed
    def test_keyword_is_none(self):
        results = filter_by_keyword([], None)
        assert len(results) == 0

    # expecting toptier_agencies to not be changed
    def test_keyword_is_empty(self):
        results = filter_by_keyword([{"x": "y"}], "")
        assert len(results) == 1

    # To make sure there are no exceptions thrown
    def test_no_abbrevation_or_agency_name(self):
        mock_agencies = [{"x": 0, "y": 1}]
        results = filter_by_keyword(mock_agencies, "test-search")
        assert len(results) == 0

    # Safely handle unexpected input
    # May not cover everything
    def test_non_array_passed(self):
        invalid_agencies = [{}, "", 0, None]
        for invalid_agency in invalid_agencies:
            results = filter_by_keyword(invalid_agency, "test-search")
            assert len(results) == 0

    def test_no_matches_found(self):
        name = "ABC"
        mock_agencies = [
            {
                "abbreviation": name,
                "agency_name": name,
            },
            {
                "abbreviation": name,
                "agency_name": name,
            },
        ]
        og_mock_agencies = deepcopy(mock_agencies)
        results = filter_by_keyword(mock_agencies, "XYZ")
        assert len(results) == 0
        assert mock_agencies == og_mock_agencies

    # Expecting it to search regardless of case
    def test_successful_search(self):
        mock_agencies = [
            {
                "abbreviation": "AAA",
                "agency_name": "AAA",
            },
            {
                "abbreviation": "",
                "agency_name": "AAA",
            },
            {
                "abbreviation": "AAA",
                "agency_name": "",
            },
            {
                "abbreviation": "--",
                "agency_name": "",
            },
            {
                "abbreviation": "",
                "agency_name": "--",
            },
            {
                "abbreviation": "--",
                "agency_name": "",
            },
        ]
        og_mock_agencies = deepcopy(mock_agencies)
        results = filter_by_keyword(mock_agencies, "a")
        assert len(results) == 3
        assert mock_agencies == og_mock_agencies


class TestSortResults:
    def test_empty_results(self):
        results = []
        sort_results(results, "asc", "test")
        assert len(results) == 0

    def test_unexpected_results_values(self):
        invalid_results = [{}, "", 0]
        for invalid_result in invalid_results:
            results = deepcopy(invalid_result)
            sort_results(results, "sort", "asc")
            assert results == invalid_result

    # i.e a property that does not exist in results
    # test that it can handle the exception
    def test_non_existent_sort(self):
        results = [{"x": 0} for _ in range(5)]
        og_results = deepcopy(results)
        sort_results(results, "y", "asc")
        assert results == og_results

    def test_string_sort(self):
        results = [{"key": "a"}, {"key": "A"}, {"key": "b"}]
        sort_results(results, "key", "asc")
        assert results[0]["key"] == "A"
        assert results[1]["key"] == "a"
        assert results[2]["key"] == "b"

    # Should throw an exception that is handled.
    def test_mixed_values_sort(self):
        results = [{"key": "a"}, {"key": None}, {"key": 0}]
        og_results = deepcopy(results)
        sort_results(results, "key", "asc")
        assert results == og_results

    # Expected values are asc or desc
    def test_invalid_order(self):
        results = []
        sort_results(results, "", "invalid_order")
        assert len(results) == 0

    def test_asc_order(self):
        results = [{"x": i} for i in range(5)]
        og_results = deepcopy(results)
        sort_results(results, "x", "asc")
        assert results == og_results

    def test_desc_order(self):
        results = [{"x": i} for i in range(5)]
        sort_results(results, "x", "desc")
        x = 4
        for obj in results:
            assert obj["x"] == x
            x -= 1

    # Should sort by desc and percentage_of_total_budget_authority
    def test_default_order_sort_arguments(self):
        results = [{"percentage_of_total_budget_authority": i} for i in range(5)]
        sort_results(results)
        x = 4
        for obj in results:
            assert obj["percentage_of_total_budget_authority"] == x
            x -= 1


# TODO: handle when cached file is expired
class TestReadCachedFile:
    # Safely fails if cached file not read.
    def test_invalid_filename(self):
        _, use_cached_file = read_cached_file("file.no.exist")
        assert use_cached_file is False

    # Print warning or something if file is outdated
    def test_successfully_read_file(self):
        toptier_agencies, use_cached_file = read_cached_file(filename)
        assert len(toptier_agencies) == 111
        assert use_cached_file is True

    # Validate file is valid schema.
    def test_valid_schema(self):
        mock_client = HttpClient(
            endpoint="", method="GET", output_schema=original_output_schema["properties"]["results"]
        )
        toptier_agencies, _ = read_cached_file(filename)
        mock_response = Response(status_code=200, json=toptier_agencies)
        valid_schema = mock_client.validate_response(mock_response)
        assert valid_schema is True


class TestCreateMcpResponse(Validation):
    def test_handles_invalid_schema(self):
        output_schema = {"type": "object", "properties": {"x": "string"}}
        mock_client = HttpClient(method="GET", endpoint="", output_schema=output_schema)
        response = create_mcp_response([], {}, mock_client)
        self.validate_text_content(response, '{"results":[]}')

    def test_handle_json_dumps_failure(self):
        class InvalidObj:
            def __init__(self):
                self.name = "json.dumps cannot serialize this"

        invalid_obj = InvalidObj()
        mock_client = HttpClient(method="GET", endpoint="", output_schema={})
        with pytest.raises(McpError) as err:
            create_mcp_response(invalid_obj, invalid_obj, mock_client)
        assert "Internal MCP server error" in str(err.value)

    def test_returns_mcp_text_content(self):
        output_schema = {"type": "object", "properties": {"x": "string"}}
        mock_client = HttpClient(method="GET", endpoint="", output_schema=output_schema)
        response = create_mcp_response([{"x": "y"}], {"a": "b"}, mock_client)
        self.validate_text_content(response, '{"results":[{"x":"y"}],"a":"b"}')
