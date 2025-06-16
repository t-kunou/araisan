from chalicelib.agents.components.state import State
from chalicelib.agents.weather_agent import WeatherAgent

from datetime import datetime
from langchain_core.output_parsers import StrOutputParser, BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing import Any

import ast
import json
import sys

class ListOutputParser(BaseOutputParser):
    def parse(self, text: str):
        try:
            return ast.literal_eval(text)
        except Exception:
            return [text]

class DinnerAgent:
    def __init__(self, llm):
       self.llm = llm

    def description(self):
        return "季節の食材を使った夕食の提案を行うエージェントです。"

    def agent_name(self):
        return "DinnerAgent"

    def get_answer(self, state: State) -> str:
        return state.dinner_suggestion

    def get_start_node(self):
        def start_node(state: State) -> dict[str, Any]:
            print("Workflow started with state:", state)
            return {}
        return start_node

    def get_seasonal_food_node(self):
        def seasonal_food_node(state: State) -> dict[str, Any]:
            query = state.query
            location = state.location

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切な季節の食材のリストを返してください。
質問: {query}
ユーザーの位置情報: {location}
今日の日付: {today}

回答は ['鯵', '鰯', '秋刀魚'] のような形式で、季節の食材をカンマ区切りでリストしてください。
""".strip()
            )

            #chain = prompt | self.llm | StrOutputParser()
            chain = prompt | self.llm | ListOutputParser()
            seasonal_foods = chain.invoke({"query": query, "location": location, "today": state.today})

            print({"seasonal_foods": seasonal_foods}) 
            return {"seasonal_foods": seasonal_foods}
        return seasonal_food_node

    def get_dinner_suggestion_node(self):
        def dinner_suggestion_node(state: State) -> dict[str, Any]:
            seasonal_foods = state.seasonal_foods
            query = state.query

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、季節の食材を一品以上使った料理の提案をしてください。
また、天気情報も考慮してください。
質問: {query}
季節の食材: {seasonal_foods}
天気情報: {weather}

出力は以下のように、料理名、説明、選択理由を文章として簡潔にに答えてください。
例:
鯵のたたき。新鮮な鯵を使用したたたきで、薬味と一緒に食べると美味しい。季節の食材である鯵を使っていて、暑い天気とさっぱりとした料理が合うため。
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            dinner_suggestion = chain.invoke({"query": query, "seasonal_foods": seasonal_foods, "weather": state.weather})

            print({"dinner_suggestion": dinner_suggestion}) 
            return {"dinner_suggestion": dinner_suggestion}
        return dinner_suggestion_node

    def build_workflow(self):
        weathre_workflow = WeatherAgent(self.llm).build_workflow()

        workflow = StateGraph(State)

        workflow.add_node("start_node", self.get_start_node())
        workflow.add_node("seasonal_food_node", self.get_seasonal_food_node())
        workflow.add_node("weather_node", weathre_workflow)
        workflow.add_node("dinner_suggestion_node", self.get_dinner_suggestion_node())

        workflow.set_entry_point("start_node")
        workflow.add_edge("start_node", "seasonal_food_node")
        workflow.add_edge("start_node", "weather_node")
        workflow.add_edge(["seasonal_food_node", "weather_node"], "dinner_suggestion_node")
        workflow.add_edge("dinner_suggestion_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    dinner_agent = DinnerAgent(llm)
    compiled_workflow = dinner_agent.build_workflow()

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