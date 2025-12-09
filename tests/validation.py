from mcp.types import TextContent


class Utils:
    def validate_text_content(self, response, text="", validate_text=True):
        """
        At this stage, all API routes only return one TextContent
        Should evaluate populating the array with more than one TextContent
        """
        assert isinstance(response, list)
        assert len(response) == 1
        assert isinstance(response[0], TextContent)
        assert response[0].type == "text"
        if validate_text:
            assert response[0].text == text
