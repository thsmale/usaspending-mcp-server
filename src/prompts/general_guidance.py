from mcp.types import Prompt, PromptMessage, TextContent

prompt_general_guidance = Prompt(
    name="general_guidance",
    title="General Guidance",
    description="General guidance on how to effectively use this MCP server.",
)


def prompt_message_general_guidance() -> list[PromptMessage]:
    messages: list[PromptMessage] = []

    prompt = """The following provides instructions on using this MCP server.
    This MCP server interacts with the USASpending.gov API.
    The objective is to use the available tools and resources
    to answer questions about USA federal government spending.

    All of the provided input schemas do not accept additional properties.
    So before using a tool, ensure the arguments exist in the input schema.
    Do not try to add properties that do not exist in the input schema.

    Sometimes, a request will return no data or not what the user is looking for.
    If it is likely that the data exists, the problem is likely the tool arguments.
    So modify the tool arguments or try again with a different tool.
    """

    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=prompt)))

    return messages
