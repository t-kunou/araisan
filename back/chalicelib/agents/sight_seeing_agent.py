from chalicelib.agents.components.state import State
from chalicelib.agents.weather_agent import WeatherAgent

from datetime import datetime
from langchain_core.output_parsers import StrOutputParser, BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing import Any

import json
import sys

class SightSeeingAgent:
    def __init__(self, llm):
       self.llm = llm

    def description(self):
        return "ユーザーの質問に対して、観光地の提案を行うエージェントです。"

    def agent_name(self):
        return "SightSeeingAgent"

    def get_answer(self, state: State) -> str:
        return state.sight_seeing_result

    def get_sight_seeing_suggention_node(self):
        def sight_seeing_suggention_node(state: State) -> dict[str, Any]:
            query = state.query
            location = state.location

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切な観光地の提案を行ってください。
質問: {query}
ユーザーの位置情報: {location}
今日の日付: {today}
天気情報: {weather}
回答は観光地の名前とその説明を簡潔に記述してください。
経路の選択肢を簡単に説明してください。
また、天気情報をもとに、服装や持ち物のアドバイスも含めてください。
""".strip()
            )
            chain = prompt | self.llm | StrOutputParser()
            sight_seeing_result = chain.invoke({"query": query, "location": location, "today": state.today, "weather": state.weather})
            print({"sight_seeing_result": sight_seeing_result})
            return {"sight_seeing_result": sight_seeing_result}
        return sight_seeing_suggention_node

    def build_workflow(self):
        weather_workflow = WeatherAgent(self.llm).build_workflow()
        workflow = StateGraph(State)

        workflow.add_node("weatehr_predict_node", weather_workflow) 
        workflow.add_node("sight_seeing_suggention", self.get_sight_seeing_suggention_node())

        workflow.set_entry_point("weatehr_predict_node")

        workflow.add_edge("weatehr_predict_node", "sight_seeing_suggention")
        workflow.add_edge("sight_seeing_suggention", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    sight_seeing_agent = SightSeeingAgent(llm)
    compiled_workflow = sight_seeing_agent.build_workflow()

    query = input
    # Example state to test the workflow
    initial_state = State(
        query=query,
        location="東京",
        today=datetime.now().strftime("%Y-%m-%d"),
    )

    result = compiled_workflow.invoke(initial_state)
    print(json.dumps(result, indent=2, ensure_ascii=False)) 

if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else []
    print("Argument:", argument)
    main(argument)