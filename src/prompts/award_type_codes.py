from mcp.types import Prompt, PromptMessage, TextContent

from resources.award_type_codes import award_type_groups, resource_name
from tools.v2.search.config import object_award_types

prompt_award_type_codes_guide = Prompt(
    name="award_type_codes_guide",
    title="Guide for award_type_codes",
    description="Explains how to use the award_type_codes property.",
)


def prompt_message_award_type_codes_guide() -> list[PromptMessage]:
    messages: list[PromptMessage] = []

    prompt = f"""# Guide

    ## What is award_type_codes?
    award_type_codes are short identifiers
    used to filter or categorize federal spending into specific buckets.
    award_type_codes is an array of award_types.
    The allowed award types are {object_award_types}.

    ## Usage
    One should use award_type_codes to specify which kind of spending data they are looking for.
    award_type_codes is used in the spending_by_award and spending_over_time tools.
    More specifically, it is used in the filters input schema.
    award_type_codes is required in tool spending_by_award but optional in tool spending_over_time.
    award_type_codes must only contain types from one group.
    The only groups are {award_type_groups.keys()}.
    award_type_codes are grouped according to this JSON {award_type_groups}.
    This means that you cannot include award_type_codes from different groups in the array.
    Select one or more unique values per group.

    ## Common Errors
    A common error is the message award_type_codes must only contain types from one group.
    One cannot include award_type_codes from different groups as they are mutually exclusive.
    So only use award_type_codes from one group in the final array.

    ## Resources
    Refer to the resource {resource_name} for award_type_codes sorted by group.
    """

    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=prompt)))

    return messages
