import sys
import warnings

from datetime import datetime

from ai_hal.crew import AiHal

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    user_query = input("Ask a question?")
    ai_hal_crew = AiHal()

    try:
        crew_instance = ai_hal_crew.crew()

        result = crew_instance.kickoff(inputs={"user_query": user_query,"search_queries": ""})
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
if __name__ == "__main__":
    run()