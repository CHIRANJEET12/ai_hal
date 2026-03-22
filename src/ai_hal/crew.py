from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class AiHal():
    """AiHal crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], 
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )
    
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True
        )
    
    @agent
    def search_agent_1(self) -> Agent:
        return Agent(
            config=self.agents_config['search_agent_1'],
            verbose=True
        )

    @agent
    def search_agent_2(self) -> Agent:
        return Agent(
            config=self.agents_config['search_agent_2'],
            verbose=True
        )

    @agent
    def search_agent_3(self) -> Agent:
        return Agent(
            config=self.agents_config['search_agent_3'],
            verbose=True
        )
    
    @agent
    def source_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['source_validator'],
            verbose=True
        )
    
    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['extractor'],
            verbose=True
        )
    
    @agent
    def answer_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['answer_generator'],
            verbose=True
        )


    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], 
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], 
            output_file='report.md'
        )
    
    @task
    def planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['planner_task'],
        )
    
    @task
    def search_task_1(self) -> Task:
        return Task(
            config=self.tasks_config['search_task_1'],
        )

    @task
    def search_task_2(self) -> Task:
        return Task(
            config=self.tasks_config['search_task_2'],
        )

    @task
    def search_task_3(self) -> Task:
        return Task(
            config=self.tasks_config['search_task_3'],
        )
    
    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['validation_task'],
        )
    
    @task
    def extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['extraction_task'],
        )
    
    @task
    def answer_task(self) -> Task:
        return Task(
            config=self.tasks_config['answer_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the AiHal-Planner crew"""


        return Crew(
            agents=[self.planner()], 
            tasks=[self.planner_task()], 
            process=Process.sequential,
            verbose=True,
        )
