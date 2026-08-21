import json
import os
#from google import genai
from dotenv import load_dotenv
from src.agent.tools import TOOLS, TOOL_FUNCTIONS
from src.logger import logger
from src.llm_client import call_gemini

load_dotenv()

#client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """You are a financial research assistant with access to tools for searching SEC filings, getting stock prices, doing calculations, and searching news.

Rules:
- Only answer using information actually returned by your tools. Do not add facts, events, executive/leadership changes, regulatory news, analyst opinions, or commentary from your own general knowledge, even if you believe it to be true or recall it from training.
- If part of the question asks about something no tool can provide (e.g. leadership changes, regulatory settlements, analyst price targets, market commentary), say so explicitly — state plainly that this information isn't available from your current tools, rather than answering from memory.
- When you do have tool data, give a direct, synthesized answer, citing which tool/source backs each claim.
- If you're not fully confident a specific claim is backed by actual tool output, leave it out rather than include it anyway."""



def run_agent(question: str, max_turns: int = 5) -> str:
    logger.info(f"Agent started | question: '{question}'")
    interaction = call_gemini(
    system_instruction=SYSTEM_INSTRUCTION,
    input=question,
    tools=TOOLS,
)


    for turn in range(max_turns):
        function_call_steps = [s for s in interaction.steps if s.type == "function_call"]

        if not function_call_steps:
            logger.info(f"Agent finished after {turn + 1} turn(s)")
            return interaction.output_text.strip()

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
    return "I wasn't able to fully answer this within the allowed number of steps."


if __name__ == "__main__":
    test_question = "What is Nvidia's current stock price, and what employee-related risks do they disclose in their 10-K?"
    print(run_agent(test_question))