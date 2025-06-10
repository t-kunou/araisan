from typing import Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from components.state import State
from components.duck_duck_go_searcher import DuckDuckGoSearcher
import requests
import sys
from datetime import datetime

class AiNewsAgent:
    def __init__(self, llm):
        self.llm = llm

    def description(self):
        return "ユーザーの質問に対して、ウェブ検索を行い、情報を提供するエージェントです。"

    def get_answer(self, result: dict[str, Any]) -> str:
        return result.get("web_search_result", "")

    def get_generate_query_node(self):
        def generate_query_node(state: State) -> dict[str, Any]:
            query = state.query
            location = state.location

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、ウェブ検索用のクエリを生成してください。
質問: {query}
今日の日付: {today}
生成されたクエリは、ウェブ検索に適した形式で、具体的かつ明確なものにしてください。
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            generated_query = chain.invoke({"query": query, "location": location, "today": state.today})

            print({"generated_query": generated_query})
            return {"generated_query": generated_query}
        return generate_query_node

    def get_web_search_node(self):
        def web_search_node(state: State) -> dict[str, Any]:
            generated_query = state.generated_query

            searcher = DuckDuckGoSearcher()
            search_result = searcher.advanced_search_with_duckduckgo_search(
                query=generated_query,
                max_results=5,
                region="jp-jp",
                site="ledge.ai",
            )

            print(f"Search results: {search_result}")

            contexts = []
            for result in search_result:
                print(f"result: {result}")
                contexts.append(f"title: {result['title']}\ncontent: {result['snippet']}\n")

            print("contexts:", contexts)

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、ウェブ検索結果をもとに回答を生成してください。
質問: {query}
ウェブ検索結果:
{contexts}
今日の日付: {today}
回答は、ウェブ検索結果を参考にして、具体的かつ明確に記述してください。
""".strip()
            )
            chain = prompt | self.llm | StrOutputParser()
            web_search_result = chain.invoke({"query": state.query, "contexts": "\n".join(contexts), "today": state.today})
            print({"web_search_result": web_search_result})

            return {"web_search_result": web_search_result}
        return web_search_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("generate_query_node", self.get_generate_query_node())
        workflow.add_node("web_search_node", self.get_web_search_node())

        workflow.set_entry_point("generate_query_node")

        workflow.add_edge("generate_query_node", "web_search_node")
        workflow.add_edge("web_search_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow

def main(input):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    web_search_agent = AiNewsAgent(llm)
    compiled_workflow = web_search_agent.build_workflow()

    initial_state = State(query=input, location="石垣島", today=datetime.now().strftime("%Y-%m-%d"))
    result = compiled_workflow.invoke(initial_state)

    print(result)

if __name__ == "__main__":
    input_query = sys.argv[1]
    main(input_query)
