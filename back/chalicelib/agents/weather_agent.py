from chalicelib.agents.components.state import State

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END
from langgraph.graph import StateGraph
from typing import Any

import json
import requests
import sys

class WeatherAgent:
    CODE = {
        "北海道": {
            "宗谷地方": "011000", "上川・留萌地方": "012000", "石狩・空知・後志地方": "016000", "網走・北見・紋別地方": "013000", "釧路・根室地方": "014100", "十勝地方": "014030", "胆振・日高地方": "015000", "渡島・檜山地方": "017000"
        },
        "東北": {
            "青森県": "020000", "秋田県": "050000", "岩手県": "030000", "宮城県": "040000", "山形県": "060000", "福島県": "070000"
        },
        "関東甲信": {
            "茨城県": "080000", "栃木県": "090000", "群馬県": "100000", "埼玉県": "110000", "東京都": "130000", "千葉県": "120000", "神奈川県": "140000", "長野県": "200000", "山梨県": "190000"
        },
        "東海": {
            "静岡県": "220000", "愛知県": "230000", "岐阜県": "210000", "三重県": "240000"
        },
        "北陸": {
            "新潟県": "150000", "富山県": "160000", "石川県": "170000", "福井県": "180000"
        },
        "近畿": {
            "滋賀県": "250000", "京都府": "260000", "大阪府": "270000", "兵庫県": "280000", "奈良県": "290000", "和歌山県": "300000"
        },
        "中国": {
            "岡山県": "330000", "広島県": "340000", "島根県": "320000", "鳥取県": "310000", "山口県": "350000"
        },
        "四国": {
            "徳島県": "360000", "香川県": "370000", "愛媛県": "380000", "高知県": "390000"
        },
        "九州": {
              "福岡県": "400000", "大分県": "440000", "長崎県": "420000", "佐賀県": "410000", "熊本県": "430000", "宮崎県": "450000", "鹿児島県": "460100", "奄美地方": "460040"
        },
        "沖縄": {
            "沖縄本島地方": "471000", "大東島地方": "472000", "宮古島地方": "473000", "八重山地方": "474000"
        }
    }

    def orverview_url(code):
        return f"https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{code}.json"

    def predict_url(code):
        return f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"

    def __init__(self, llm):
        self.llm = llm

    def description(self):
        return "ユーザーの質問に対して、天気予報を提供するエージェントです"

    def agent_name(self):
        return "WeatherAgent"

    def get_answer(self, state: State) -> str:
        return state.weather

    def get_judge_region_node(self):
        def judge_reagion_node(state: State) -> dict[str, Any]:
            # langgraph node what judge region code from user message
            query = state.query
            location = state.location
            # JSON encode from CODE
            region_codes = json.dumps(self.CODE, ensure_ascii=False)

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切な地域コードを返してください。

質問: {query}
ユーザーの位置情報: {location}

地域コード: {region_codes}

回答は地域コードの文字列のみを返してください。
""".strip()
            )

            chain = prompt | self.llm | StrOutputParser()
            target_region_code = chain.invoke({"query": query, "region_codes": region_codes, "location": location})

            print({"target_region_code": target_region_code})
            return {"target_region_code": target_region_code}

        return judge_reagion_node

    def get_predict_weather_node(self):
        def predict_weather_node(state: State) -> dict[str, Any]:
            target_region_code = state.target_region_code
            query = state.query

            overview_url = WeatherAgent.orverview_url(target_region_code)
            overview_response = requests.get(overview_url, timeout=10)
            overview_data = overview_response.json()

            predict_url = WeatherAgent.predict_url(target_region_code)
            predict_response = requests.get(predict_url, timeout=10)
            predict_data = predict_response.json()

            prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、適切な天気予報を返してください。
質問中に天気以外の情報が含まれている場合は、無視してください。
質問: {query}
地域の概要: {overview_data}
天気予報: {predict_data}
""".strip())

            chain = prompt | self.llm | StrOutputParser()
            answer = chain.invoke({
                "query": query,
                "overview_data": overview_data,
                "predict_data": predict_data
            })

            print({"answer": answer})
            return {"weather": answer}

        return predict_weather_node

    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("judge_region", self.get_judge_region_node())
        workflow.add_node("predict_weather", self.get_predict_weather_node())

        workflow.set_entry_point("judge_region")

        workflow.add_edge("judge_region", "predict_weather")
        workflow.add_edge("predict_weather", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow


def main(input):
    llm = ChatOpenAI(model="gpt-4o")
    agent = WeatherAgent(llm)

    compiled_workflow = agent.build_workflow()

    initial_state = State(query=input, location="石垣島")
    result = compiled_workflow.invoke(initial_state)

    print(result)

if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else []
    print("Argument:", argument)
    main()
