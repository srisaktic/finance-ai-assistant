import json
import os
#from google import genai
from dotenv import load_dotenv
from src.agent.tools import TOOLS, TOOL_FUNCTIONS
from src.logger import logger
from src.llm_client import call_gemini, call_azure
from src.config import LLM_PROVIDER

load_dotenv()

#client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """You are a financial research assistant with access to tools for searching SEC filings, getting stock prices, doing calculations, and searching news.

Rules:
- Only answer using information actually returned by your tools. Do not add facts, events, executive/leadership changes, regulatory news, analyst opinions, or commentary from your own general knowledge, even if you believe it to be true or recall it from training.
- If part of the question asks about something no tool can provide (e.g. leadership changes, regulatory settlements, analyst price targets, market commentary), say so explicitly — state plainly that this information isn't available from your current tools, rather than answering from memory.
- When you do have tool data, give a direct, synthesized answer, citing which tool/source backs each claim.
- If you're not fully confident a specific claim is backed by actual tool output, leave it out rather than include it anyway."""



def _run_agent_gemini(
    question: str,
    previous_interaction_id: str | None = None,
    max_turns: int = 5,
) -> tuple[str, str]:
    logger.info(
        f"Agent started | question: '{question}'"
        + (" (continuing conversation)" if previous_interaction_id else "")
    )

    first_call_kwargs = dict(
        system_instruction=SYSTEM_INSTRUCTION,
        input=question,
        tools=TOOLS,
    )
    if previous_interaction_id:
        first_call_kwargs["previous_interaction_id"] = previous_interaction_id

    interaction = call_gemini(**first_call_kwargs)

    for turn in range(max_turns):
        function_call_steps = [s for s in interaction.steps if s.type == "function_call"]

        if not function_call_steps:
            logger.info(f"Agent finished after {turn + 1} turn(s)")
            return interaction.output_text.strip(), interaction.id

        logger.info(f"Turn {turn + 1}: {len(function_call_steps)} tool call(s) requested")

        function_results = []
        for step in function_call_steps:
            logger.info(f"  -> {step.name}({step.arguments})")
            tool_fn = TOOL_FUNCTIONS[step.name]
            result = tool_fn(**step.arguments)
            logger.info(f"  <- {step.name} returned {str(result)[:150]}")
            function_results.append({
                "type": "function_result",
                "name": step.name,
                "call_id": step.id,
                "result": [{"type": "text", "text": json.dumps(result)}],
            })

        interaction = call_gemini(
        system_instruction=SYSTEM_INSTRUCTION,
        input=function_results,
        tools=TOOLS,
        previous_interaction_id=interaction.id,
             )

    logger.warning(f"Agent hit max_turns ({max_turns}) without finishing")
    return (
        "I wasn't able to fully answer this within the allowed number of steps.",
        interaction.id,
    )


def _to_azure_tools(tools: list[dict]) -> list[dict]:
    """Our tool definitions already match Azure's format. We only turn off "strict" mode,
    because strict mode requires every parameter, and some of ours are optional."""
    return [{**t, "strict": False} for t in tools]


def _run_agent_azure(
    question: str,
    previous_interaction_id: str | None = None,
    max_turns: int = 5,
) -> tuple[str, str]:
    logger.info(
        f"Agent started (Azure) | question: '{question}'"
        + (" (continuing conversation)" if previous_interaction_id else "")
    )
    tools = _to_azure_tools(TOOLS)

    first_call_kwargs = dict(
        instructions=SYSTEM_INSTRUCTION,
        input=question,
        tools=tools,
    )
    if previous_interaction_id:
        first_call_kwargs["previous_response_id"] = previous_interaction_id

    response = call_azure(**first_call_kwargs)

    for turn in range(max_turns):
        function_calls = [item for item in response.output if item.type == "function_call"]

        if not function_calls:
            logger.info(f"Agent finished after {turn + 1} turn(s)")
            return response.output_text.strip(), response.id

        logger.info(f"Turn {turn + 1}: {len(function_calls)} tool call(s) requested")

        function_results = []
        for call in function_calls:
            args = json.loads(call.arguments)
            logger.info(f"  -> {call.name}({args})")
            tool_fn = TOOL_FUNCTIONS[call.name]
            result = tool_fn(**args)
            logger.info(f"  <- {call.name} returned {str(result)[:150]}")
            function_results.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })

        response = call_azure(
            instructions=SYSTEM_INSTRUCTION,
            input=function_results,
            tools=tools,
            previous_response_id=response.id,
        )

    logger.warning(f"Agent hit max_turns ({max_turns}) without finishing")
    return (
        "I wasn't able to fully answer this within the allowed number of steps.",
        response.id,
    )


def run_agent(
    question: str,
    previous_interaction_id: str | None = None,
    max_turns: int = 5,
) -> tuple[str, str]:
    """Run the agent loop for whichever provider is switched on."""
    if LLM_PROVIDER == "gemini":
        return _run_agent_gemini(question, previous_interaction_id, max_turns)

    if LLM_PROVIDER == "azure":
        return _run_agent_azure(question, previous_interaction_id, max_turns)

    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")




if __name__ == "__main__":
    test_question = "What is Nvidia's current stock price, and what employee-related risks do they disclose in their 10-K?"
    answer, _ = run_agent(test_question)
    print(answer)