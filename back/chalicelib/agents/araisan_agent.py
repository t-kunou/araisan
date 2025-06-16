from chalicelib.agents.components.state import State

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Any
from datetime import datetime

import json
import sys

class AraisanAgent:
    def __init__(self, llm):
        self.llm = llm

    def get_araisan_result_node(self):
        def araisan_result_node(state: State) -> dict[str, Any]:
            general_result = state.general_answer

            prompt = ChatPromptTemplate.from_template(
"""あなたはぶっきらぼうな回答を返すAIエージェントです。
他のエージェントの回答をぶっきらぼうな回答に変換してください。
また、話し言葉として自然な形にしてください。
最後に「知らんけど」、「たぶんな」、「まあ、嘘だけど」のような不必要でいい加減な一言を付け加えてください。
質問: {query}
回答: {general_result}
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            araisan_result = chain.invoke({"general_result": general_result, "query": state.query})

            print({"araisan_result": araisan_result})
            return {"araisan_result": araisan_result}
        return araisan_result_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("araisan_result_node", self.get_araisan_result_node())

        workflow.set_entry_point("araisan_result_node")

        workflow.add_edge("araisan_result_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    dinner_agent = AraisanAgent(llm)
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