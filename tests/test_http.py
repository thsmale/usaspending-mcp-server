# Unit tests to test HttpClient

import json
from unittest.mock import patch

import pytest
from httpx import Request, Response, TimeoutException
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
)
from validation import Validation

from utils.http import HttpClient


class TestHttpClientInit:
    def test_requires_endpoint_and_method(self):
        """Test required parameters"""
        with pytest.raises(TypeError) as err:
            HttpClient()
        assert "missing 2 required positional arguments: 'endpoint' and 'method'" in str(err.value)

    def test_requires_endpoint(self):
        with pytest.raises(TypeError) as err:
            HttpClient(endpoint="x")
        assert "missing 1 required positional argument: 'method'" in str(err.value)

    def test_requires_method(self):
        with pytest.raises(TypeError) as err:
            HttpClient(method="x")
        assert "missing 1 required positional argument: 'endpoint'" in str(err.value)

    def test_endpoint_is_str(self):
        with pytest.raises(TypeError) as err:
            HttpClient(endpoint=69, method="")
        assert "Expected str for endpoint" in str(err.value)

    def test_method_is_str(self):
        with pytest.raises(TypeError) as err:
            HttpClient(endpoint="", method=69)
        assert "Expected str for method" in str(err.value)

    def test_successful_init(self):
        http_client = HttpClient(endpoint="/", method="GET")
        assert isinstance(http_client, HttpClient)
        assert http_client.endpoint == "/"
        assert http_client.method == "GET"

    def test_validate_instance_variables(self):
        """
        Help detect if the functionality of HttpClient has changed.
        If this breaks, the unit test non_mandatory_instance_vars_resolve_to_none
        must be updated.
        """
        http_client = HttpClient(endpoint="", method="")
        instance_vars = vars(http_client)
        expected_vars = ["endpoint", "method", "params", "payload", "response_schema"]
        assert len(instance_vars) == len(expected_vars)
        assert sorted(instance_vars) == sorted(expected_vars)

    def test_optional_instance_vars_resolve_to_none(self):
        http_client = HttpClient(endpoint="", method="")
        mandatory_vars = ["endpoint", "method"]
        http_client_vars = vars(http_client)
        for var in http_client_vars:
            if var not in mandatory_vars:
                assert http_client_vars[var] is None


class TestValidateResponse:
    def test_no_response_schema(self):
        http_client = HttpClient(endpoint="", method="")
        result = http_client.validate_response(Response(status_code=200))
        assert result is None

    def test_non_response_type_passed(self):
        http_client = HttpClient(endpoint="", method="", response_schema={})
        result = http_client.validate_response(2)
        assert result is False

    def test_missing_required_property(self):
        response = Response(status_code=200, json={"y": "string"})
        http_client = HttpClient(
            endpoint="",
            method="",
            response_schema={
                "type": "object",
                "required": ["x"],
                "properties": {"x": {"type": "number"}},
            },
        )
        result = http_client.validate_response(response)
        assert result is False

    def test_invalid_response_type(self):
        response = Response(status_code=200, json={"x": 69})
        http_client = HttpClient(
            endpoint="",
            method="",
            response_schema={
                "type": "object",
                "required": ["x"],
                "properties": {"x": {"type": "string"}},
            },
        )
        result = http_client.validate_response(response)
        assert result is False

    def test_valid_response_schema(self):
        response = Response(status_code=200, json={"x": 69})
        http_client = HttpClient(
            endpoint="",
            method="",
            response_schema={
                "type": "object",
                "required": ["x"],
                "properties": {"x": {"type": "number"}},
            },
        )
        result = http_client.validate_response(response)
        assert result is True

    def test_response_with_text(self):
        response = Response(status_code=200, text="hello world")
        http_client = HttpClient(endpoint="", method="", response_schema={})
        result = http_client.validate_response(response)
        assert result is False


class TestHandleResponse(Validation):
    def test_2xx_status_code_response(self):
        http_client = HttpClient(endpoint="", method="")
        response = http_client.handle_response(Response(status_code=200))
        self.validate_text_content(response)

    def test_2xx_response_schema_err(self):
        http_client = HttpClient(endpoint="", method="", response_schema={})
        response = http_client.handle_response(Response(status_code=200, text=""))
        self.validate_text_content(response)

    def test_3xx_status_code_response(self):
        http_client = HttpClient(endpoint="", method="")
        with pytest.raises(McpError) as err:
            response = Response(status_code=300, request=Request(method="", url=""))
            http_client.handle_response(response)
        assert "Received non 2xx response status code 300" in str(err.value)

    def test_4xx_status_code_response(self):
        http_client = HttpClient(endpoint="", method="")
        with pytest.raises(McpError) as err:
            response = Response(status_code=400, request=Request(method="", url=""))
            http_client.handle_response(response)
        assert "Received non 2xx response status code 400" in str(err.value)

    def test_5xx_response_schema_err(self):
        http_client = HttpClient(endpoint="", method="")
        with pytest.raises(McpError) as err:
            response = Response(status_code=500, request=Request(method="", url=""))
            http_client.handle_response(response)
        assert "Received non 2xx response status code 500" in str(err.value)


class TestSuccessfulSends(Validation):
    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_200_text_response(self, mock_send):
        mock_send.return_value = Response(status_code=200, text="ok")
        get_client = HttpClient(method="GET", endpoint="/")
        res = await get_client.send()
        mock_send.assert_called_once()
        self.validate_text_content(res, text="ok")

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_200_json_response(self, mock_send):
        json_response = {"yo": "whatup"}
        mock_send.return_value = Response(status_code=200, json=json_response)
        get_client = HttpClient(method="GET", endpoint="/")
        res = await get_client.send()
        mock_send.assert_called_once()
        self.validate_text_content(res, validate_text=False)
        mock_response = json.loads(res[0].text)
        assert len(mock_response) == 1
        assert "yo" in mock_response
        assert mock_response["yo"] == json_response["yo"]

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_200_json_response_schema_err(self, mock_send):
        expected_json_schema = {
            "type": "object",
            "properties": {
                "yo": {"type": "string"},
            },
        }
        json_response = {"yo": None}
        mock_send.return_value = Response(
            status_code=200,
            json=json_response,
        )
        get_client = HttpClient(method="GET", endpoint="/", response_schema=expected_json_schema)
        res = await get_client.send()
        mock_send.assert_called_once()
        self.validate_text_content(res, validate_text=False)
        mock_response_text = json.loads(res[0].text)
        assert len(mock_response_text) == 1
        assert "yo" in mock_response_text
        assert mock_response_text["yo"] == json_response["yo"]


class TestUnsuccessfulSends:
    async def invalid_method_provided(self):
        assert "implement this test" in ""

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_400_response(self, mock_send):
        mock_send.return_value = Response(
            status_code=400, text="Bad Request", request=Request(method="", url="")
        )
        get_client = HttpClient(method="GET", endpoint="/")
        with pytest.raises(McpError) as err:
            await get_client.send()
        mock_send.assert_called_once()
        assert err.value.error.code == INTERNAL_ERROR

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_500_response(self, mock_send):
        mock_send.return_value = Response(
            status_code=500, text="Internal Server Error", request=Request(method="", url="")
        )
        get_client = HttpClient(method="GET", endpoint="/")
        with pytest.raises(McpError) as err:
            await get_client.send()
        mock_send.assert_called_once()
        assert err.value.error.code == INTERNAL_ERROR

    @pytest.mark.asyncio
    @patch(
        "utils.http.client.send",
    )
    async def test_timeout_exception(self, mock_send):
        mock_send.side_effect = TimeoutException(message="Timeout")
        get_client = HttpClient(method="GET", endpoint="/")
        with pytest.raises(McpError) as err:
            await get_client.send()
        mock_send.assert_called_once()
        assert err.value.error.code == INTERNAL_ERROR
