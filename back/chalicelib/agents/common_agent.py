from chalicelib.agents.components.state import State

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END
from langgraph.graph import StateGraph
from typing import Any
from datetime import datetime

import sys

class CommonAgent:
    def __init__(self, llm):
        self.llm = llm

    def description(self):
        return "ユーザーの質問に対して、他に適切なエージェントがない場合に回答するエージェントです。"
    
    def agent_name(self):
        return "CommonAgent"

    def get_answer(self, state: State) -> str:
        return state.common_answer

    def get_common_node(self):
        def common_node(state: State) -> dict[str, Any]:
            query = state.query
            location = state.location

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切な回答を返してください。
質問: {query}
ユーザーの位置情報: {location}
日付: {today}
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            answer = chain.invoke({"query": query, "location": location, "today": state.today})

            print({"common_answer": answer})
            return {"common_answer": answer}
        return common_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("common_node", self.get_common_node())
        workflow.set_entry_point("common_node")
        workflow.add_edge("common_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow


def main(input):
    llm = ChatOpenAI(model="gpt-4o")
    agent = CommonAgent(llm)

    compiled_workflow = agent.build_workflow()

    initial_state = State(query=input, location="石垣島", today=datetime.now().strftime("%Y-%m-%d"))
    result = compiled_workflow.invoke(initial_state)

    print(result)

if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else []
    print("Argument:", argument)
    main(argument)
