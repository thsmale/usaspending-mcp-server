import urllib.parse

from httpx import AsyncClient, Request, Response
from jsonschema import ValidationError, validate
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
    ErrorData,
    TextContent,
)

api_url = "https://api.usaspending.gov"
client = AsyncClient(timeout=None)


class HttpClient:
    def __init__(self, endpoint: str, method: str, params=None, payload=None, output_schema=None):
        # Meant to catch mistakes, request to api_url alone would return no real results
        if not isinstance(endpoint, str):
            raise TypeError(f"Expected str for endpoint but received {type(endpoint)=}.")

        # Required to create the httpx.Request
        if not isinstance(method, str):
            raise TypeError(f"Expected str for method but received {type(method)=}")

        self.endpoint = endpoint
        self.method = method
        self.params = params
        self.payload = payload
        self.output_schema = output_schema

    def validate_response(self, response: Response) -> bool | None:
        """
        Most requests in my experience fail with silly validation errors.
        See https://github.com/fedspendingtransparency/usaspending-api/issues/4513.
        So at this moment, there is a warning log and the JSON received
        from USA spending API is returned to the client.

        In the future, we may want to further customize validate_response.
        Such as requiring certain properties or types in the response payload.
        """
        if self.output_schema is None:
            return None

        try:
            payload = response.json()
            validate(instance=payload, schema=self.output_schema)
            return True
        except ValidationError as e:
            print(
                "A validation error occurred in validate_response. "
                f"{e.message} in path {e.relative_schema_path}."
            )
        except Exception as e:
            print(
                "Warning the response did not contain the expected information. "
                f"{e=} and {type(e)=}"
            )
            pass
        return False

    def handle_response(self, response: Response) -> list[TextContent]:
        if response.status_code >= 200 and response.status_code < 300:
            print(response.text)
            self.validate_response(response)
            return [
                TextContent(
                    type="text",
                    text=response.text,
                )
            ]
        else:
            print(
                f"Non 2xx status code received {response.status_code} "
                f"with response payload {response.text}"
            )
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=(
                        f"Received non 2xx response status code {response.status_code} "
                        "from the USASpending API."
                    ),
                    data=(
                        f"The {response.request.method} request to {str(response.request.url)} "
                        f"with response payload {self.payload} "
                        f"failed with HTTP status code {response.status_code} "
                        f"and response payload {response.text}",
                    ),
                )
            )

    async def send(self):
        url = f"{api_url}{self.endpoint}"
        if self.params is not None:
            url = url + urllib.parse.urlencode(self.params)

        try:
            request = Request(method=self.method, url=url, json=self.payload)
            response = await client.send(request)
            return self.handle_response(response)
        except Exception as e:
            print(f"Request to {url} failed due to {e=} with {type(e)=}")
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message="Unable to send the request to the USA Spending API.",
                    data=(f"The request to {url} failed due to exception {e=} with {type(e)=}"),
                )
            ) from e
