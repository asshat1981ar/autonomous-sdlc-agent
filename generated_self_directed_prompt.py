# This script generates a self-directed prompting template based on project context for use in autonomous loops.

TASK_CONTEXT = "You are an autonomous software development orchestrator managing multiple AI agents collaborating on software projects."

TONE_CONTEXT = "Maintain a collaborative, analytical, and iterative tone."

TASK_DESCRIPTION = """
Generate a self-directed prompt that guides AI agents to:
- Analyze the current project context and state
- Identify next logical development or improvement steps
- Formulate clear, actionable tasks for autonomous execution
- Continuously monitor progress and adapt plans dynamically
- Communicate findings and decisions effectively within the agent swarm
"""

IMMEDIATE_TASK = "Create a detailed, structured prompt that can be used to initiate and sustain autonomous development loops."

PRECOGNITION = "Think step-by-step about the components needed in the prompt to ensure clarity, adaptability, and effectiveness."

OUTPUT_FORMATTING = "Format the prompt as a multi-line string with sections for context, objectives, instructions, and expected outcomes."

PREFILL = ""

PROMPT = ""

if TASK_CONTEXT:
    PROMPT += f"""{TASK_CONTEXT}"""

if TONE_CONTEXT:
    PROMPT += f"""\n\n{TONE_CONTEXT}"""

if TASK_DESCRIPTION:
    PROMPT += f"""\n\n{TASK_DESCRIPTION}"""

if IMMEDIATE_TASK:
    PROMPT += f"""\n\n{IMMEDIATE_TASK}"""

if PRECOGNITION:
    PROMPT += f"""\n\n{PRECOGNITION}"""

if OUTPUT_FORMATTING:
    PROMPT += f"""\n\n{OUTPUT_FORMATTING}"""

logger.info("--------------------------- Full prompt with variable substitutions ---------------------------")
logger.info("USER TURN")
logger.info(PROMPT)
logger.info("\nASSISTANT TURN")
logger.info(PREFILL)
