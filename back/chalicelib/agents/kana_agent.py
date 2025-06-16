from chalicelib.agents.components.state import State

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Any
from datetime import datetime

import json
import sys

class KanaAgent:
    def __init__(self, llm):
        self.llm = llm

    def get_convert_kana_node(self):
        def convert_kana_node(state: State) -> dict[str, Any]:
            answer = state.general_answer
            word_dict = {
                "朝会": "あさかい"
            }

            prompt = ChatPromptTemplate.from_template(
"""あなたはテキスト2スピーチのためにかな情報を提供するAIエージェントです。
他のエージェントの回答をひらがなに変化してください。
また、回答は分かち書きにしてください。
元の回答にない情報は追加しないでください。
answer: {answer}

辞書: {word_dict}
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            kana_answer = chain.invoke(
                {"answer": answer, "word_dict" : json.dumps(word_dict) }
            )

            print({"kana_answer": kana_answer})
            return {"kana_answer": kana_answer}
        return convert_kana_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("convert_kana_node", self.get_convert_kana_node())

        workflow.set_entry_point("convert_kana_node")

        workflow.add_edge("convert_kana_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    dinner_agent = KanaAgent(llm)
    compiled_workflow = dinner_agent.build_workflow()

    query = input
    # Example state to test the workflow
    initial_state = State(
        query=query,
        general_answer=query,
        location="東京",
        today=datetime.now().strftime("%Y-%m-%d"),
    )

    result = compiled_workflow.invoke(initial_state)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else []
    print("Argument:", argument)
    main(argument)