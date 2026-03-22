#!/usr/bin/env python
import sys
import warnings

import asyncio
from datetime import datetime

from ai_hal.crew import AiHal
from crewai import Crew

import json

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import re

def safe_json_parse(text):
    """Extract JSON from text that may contain explanatory text"""
    try:
        return json.loads(text)
    except:
        cleaned = re.sub(r"```json\s*|\s*```", "", text).strip()
        try:
            return json.loads(cleaned)
        except:
            pass
    
        json_pattern = r'\{[^{}]*"sources"[^{}]*\[.*?\][^{}]*"content"[^{}]*\[.*?\][^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[-1]) 
            except:
                pass
        
        last_brace = text.rfind('{')
        if last_brace != -1:
            potential_json = text[last_brace:]
            try:
                return json.loads(potential_json)
            except:
                pass
        
        print("⚠️ Could not parse JSON, returning raw")
        return {"raw": text, "sources": [], "content": []}

async def run_crew(crew_instance, inputs=None):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: crew_instance.kickoff(inputs=inputs)
    )

    output_text = result.raw if hasattr(result, "raw") else str(result)
    try:
        return safe_json_parse(output_text)
    except:
        print("⚠️ JSON parse failed:\n", output_text)
        return {"raw": output_text}
    
async def run_single(agent_fn, task_fn, inputs):
    """Run a single agent with its task"""
    ai = AiHal()

    # Get the agent and task
    agent = agent_fn()
    task = task_fn()
    task.agent = agent

    # Create the crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )

    # Pass inputs to kickoff
    result = await run_crew(crew, inputs)
    
    # If result is already a dict with sources, return it
    if isinstance(result, dict):
        if "sources" in result or "content" in result:
            return result
        if "raw" in result:
            # Try to parse the raw string again
            try:
                parsed = safe_json_parse(result["raw"])
                if isinstance(parsed, dict) and ("sources" in parsed or "content" in parsed):
                    return parsed
            except:
                pass
    
    return result

async def validate_sources(results):
    ai = AiHal()
    print("\n🔍 STEP 3: LLM Source Validation...\n")

    # Merge raw data first
    merged_sources = []
    merged_content = []

    for r in results:
        merged_sources.extend(r.get("sources", []))
        merged_content.extend(r.get("content", []))


    # Run validator agent
    validator_result = await run_single(
        ai.source_validator,
        ai.validation_task,
        {
            "sources": json.dumps(merged_sources),
            "content": json.dumps(merged_content)
        }
    )

    validated_sources = validator_result.get("validated_sources", [])
    validated_content = validator_result.get("validated_content", [])

    validated_sources  = sorted(
        validated_sources,
        key=lambda x : x.get("score",0.0),
        reverse=True
    )
    validated_sources = [
        s for s in validated_sources if s.get("score",0.0) > 0.5
    ]
    return validated_sources, validated_content

async def extract_facts(validated_content):
    ai = AiHal()

    results = await run_single(
        ai.extractor,
        ai.extraction_task,{
            "content": json.dumps(validated_content)
        }
    )

    facts = results.get("facts",[])

    return facts

async def generate_answer(facts, sources):
    ai = AiHal()

    print("\n✍️ STEP 5: Generating Answer...\n")

    result = await run_single(
        ai.answer_generator,
        ai.answer_task,
        {
            "facts": json.dumps(facts),
            "sources": json.dumps(sources)
        }
    )

    answer = result.get("answer", "")
    confidence = result.get("confidence", 0)
    justification = result.get("justification", "")

    return answer, confidence, justification

async def pipeline(user_query):
    ai = AiHal()

    print("\n🔹 STEP 1: Planner...\n")

    #planner
    planner_output = await run_crew(
        ai.crew(),
        inputs={"user_query": user_query}
    )

    try:
        plan = planner_output  
    except:
        raise Exception(f"Planner output not valid JSON: \n{planner_output}")
    
    print("\n✅ PLAN:\n", json.dumps(plan, indent=2))

    search_queries = plan.get("search_queries", [])

    print("\n⚡ STEP 2: Parallel Search...\n")

    # Run one agent with timeout protection
    try:
        result = await asyncio.wait_for(
            run_single(ai.search_agent_1, ai.search_task_1, {"search_queries": search_queries}),
            timeout=200
        )
        results = [result]
    except asyncio.TimeoutError:
        print("❌ Search timed out")
        results = [{"error": "timeout", "sources": [], "content": []}]

    print("\n⚡ STEP 3: validating Search...\n")

    validated_sources, validated_content = await validate_sources(results)

    print("\n⚡ STEP 4: extracting facts...\n")

    facts = await extract_facts(validated_content)

    print("\n⚡ STEP 4: generating answer...\n")

    answer, confidence, justification = await generate_answer(facts, validated_sources)

    print("\n⚡ STEP 4: final output...\n")

    final_output = {
        "plan": plan,
        "answer": answer,
        "confidence": confidence,
        "justification": justification,
        "sources": validated_sources,
        "facts": facts
    }

    print("\n📦 MERGED OUTPUT:\n", json.dumps(final_output, indent=2))

    return final_output

def run():
    """
    Run the full pipeline (Planner + Parallel Search)
    """
    query = input("Enter your query: ")

    try:
        result = asyncio.run(pipeline(query))
        print("\n🎯 FINAL OUTPUT:\n")
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the pipeline: {e}")


if __name__ == "__main__":
    run()