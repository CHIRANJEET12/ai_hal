from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import SerperDevTool

@CrewBase
class AiHal():
    """AiHal crew for hallucination reduction pipeline"""

    agents_config: 'config/agents.yaml'
    tasks_config: 'config/tasks.yaml'
    
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],  # type: ignore[index]
            # tools=[SerperDevTool()],
            verbose=True,
        )   
    @agent
    def search_agent_1(self) -> Agent:
        return Agent(
            config=self.agents_config["search_agent_1"],  # type: ignore[index]
            tools=[SerperDevTool()],
            max_iter=2,
            verbose=True,
        )
    
    @agent
    def source_validator(self) -> Agent:
        return Agent(
            config=self.agents_config["source_validator"],  # type: ignore[index]
            # tools=[SerperDevTool()],
            verbose=True,
        )       
    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["extractor"],  # type: ignore[index]
            # tools=[],
            verbose=True,
        )
    @agent
    def answer_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["answer_generator"],  # type: ignore[index]
            # tools=[SerperDevTool()],
            verbose=True,
        )       
    
    @task
    def planner_task(self) -> Task:
        return Task(
            config=self.tasks_config["planner_task"],  # type: ignore[index]
        )
    @task
    def search_task_1(self) -> Task:
        return Task(
            config=self.tasks_config["search_task_1"],  # type: ignore[index]
        )                                                               
    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["validation_task"],  # type: ignore[index]
        )
    @task
    def extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config["extraction_task"],  # type: ignore[index]
        )
    @task
    def answer_task(self) -> Task:
        return Task(
            config=self.tasks_config["answer_task"],
            output_file="output/answer.txt"  # type: ignore[index]
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the AiHal Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
