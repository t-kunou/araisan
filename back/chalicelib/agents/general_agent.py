from chalicelib.agents.araisan_agent import AraisanAgent
from chalicelib.agents.common_agent import CommonAgent
from chalicelib.agents.components.state import State
from chalicelib.agents.dinner_agent import DinnerAgent
from chalicelib.agents.kana_agent import KanaAgent
from chalicelib.agents.sight_seeing_agent import SightSeeingAgent
from chalicelib.agents.weather_agent import WeatherAgent
from chalicelib.agents.calendar_agent import CalendarAgent

from datetime import datetime
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph import StateGraph
from typing import Any

import sys


class GeneralAgent:
    def __init__(self, llm):
        self.llm = llm
        self.agents = {
            1: WeatherAgent(llm),
            2: DinnerAgent(llm),
            3: SightSeeingAgent(llm),
            9: CommonAgent(llm),
        }

    def get_judge_agent_node(self):
        def judge_agent_node(state: State) -> dict[str, Any]:
            query = state.query
            agent_descriptions = [f"{i}: {agent.description()}" for i, agent in self.agents.items()]

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切なエージェントを選択してください。
質問: {query}
エージェント候補: {agents}

回答はエージェントの番号のみを返してください。
""".strip()
            )
            chain = prompt | self.llm | StrOutputParser()
            agent_number = chain.invoke({"query": query, "agents": agent_descriptions})
            print({"selected_agent": agent_number})
            return {"selected_agent": agent_number}

        return judge_agent_node
    
    def get_result_node(self):
        def result_node(state: State) -> dict[str, Any]:
            agent_number = int(state.selected_agent)
            agent = self.agents.get(agent_number)

            general_answer = agent.get_answer(state)

            return {'general_answer': general_answer}
        return result_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("judge_agent_node", self.get_judge_agent_node())

        for agent in self.agents.values():
            agent_workflow = agent.build_workflow()
            workflow.add_node(f"{agent.agent_name()}", agent_workflow)

        workflow.add_node("result_node", self.get_result_node())
        
        #araisan_agent_workflow = AraisanAgent(self.llm).build_workflow()
        #workflow.add_node("AraisanAgent", araisan_agent_workflow)

        kana_agent_workflow = KanaAgent(self.llm).build_workflow()
        workflow.add_node("KanaAgent", kana_agent_workflow)

        workflow.set_entry_point("judge_agent_node")
        
        edge_rule = {index: agent.agent_name() for index, agent in self.agents.items()}
        print("Edge Rule:", edge_rule)

        workflow.add_conditional_edges(
            "judge_agent_node",
            lambda state: int(state.selected_agent),
            {index: agent.agent_name() for index, agent in self.agents.items()}
        )

        for agent in self.agents.values():
            workflow.add_edge(agent.agent_name(), "result_node")

        workflow.add_edge("result_node", "KanaAgent")
        #workflow.add_edge("AraisanAgent", "KanaAgent")
        workflow.add_edge("KanaAgent", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    agent = GeneralAgent(llm)

    compiled_workflow = agent.build_workflow()

    initial_state = State(query=input, location="東京", today=datetime.now().strftime("%Y-%m-%d"))
    result = compiled_workflow.invoke(initial_state)

    print("=====================")
    print(result['araisan_result'])
    print("=====================")

if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else []
    print("Argument:", argument)
    main(argument)