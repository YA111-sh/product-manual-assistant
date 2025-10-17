# service/crew_setup.py

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from service.helpers import small_talk_response, document_response
import os
from dotenv import load_dotenv


load_dotenv()

# Azure LLM setup
azure_llm = LLM(
    model="azure/gpt-4.1-mini",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_API_VERSION", "2024-12-01-preview"),
)

@CrewBase
class ProductManualCrew:

    @agent
    def chat_agent(self) -> Agent:
        def chat_exec_fn(inputs: dict) -> str:
            user_query = inputs.get("user_query", "")
            return small_talk_response(user_query) or "Hello! How can I help you with the product manual today?"

        return Agent(
            name="Chat Agent",
            role="Handles greetings and casual conversation.",
            goal="Respond quickly and pleasantly to small talk.",
            backstory="Friendly assistant for chatting and casual conversation.",
            llm=azure_llm,
            exec_fn=chat_exec_fn
        )

    @agent
    def doc_agent(self) -> Agent:
        def doc_exec_fn(inputs: dict) -> str:
            user_query = inputs.get("user_query", "")
            response = document_response(user_query)
            return response + "\n\n[EXECUTED doc_exec_fn]"
            

        return Agent(
            name="Document Agent",
            role="Handles product manual queries.",
            goal="Provide accurate answers from manuals.",
            backstory="Technical assistant who searches manuals and provides correct answers.",
            llm=azure_llm,
            exec_fn=doc_exec_fn
        )

    @task
    def manual_query_task(self) -> Task:
        return Task(
            name="Manual Query Task",
            description="Search manuals and answer user questions.",
            agent=self.doc_agent(),
            expected_output="A factual and helpful answer from the manual."
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.doc_agent()],
            tasks=[self.manual_query_task()],
            process=Process.sequential,
            verbose = True,
        )

    # ✅ Run manual query directly
    def run_manual_task(self, user_query: str) -> str:
        # task = self.manual_query_task()
        crew_instance = self.crew()
        # crew_instance.tasks = [task]
        result = crew_instance.kickoff(inputs={"user_query": user_query})
        if isinstance(result, dict):
            return result.get("assistant_message") or result.get("final_output") or str(result)
        elif hasattr(result, "output"):
            return result.output
        else:
            return str(result)
