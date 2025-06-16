import datetime
import json
import requests

from flask import jsonify, session
from chalicelib.agents.components.state import State

from typing import Any
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate


class CalendarAgent:
    def __init__(self, llm):
        self.llm = llm

    def description(self):
        return "カレンダーの予定を取得するエージェントです。"
    
    def agent_name(self):
        return "CalendarAgent"
    
    def get_answer(self, state: State) -> str:
        return state.calendar_event
    
    def get_date_node(self):
        def date_node(state: State) -> dict[str, Any]:
            query = state.query
            today = datetime.datetime.utcnow().date()

            prompt = ChatPromptTemplate.from_template("""
以下の質問に対して、対象の日付を取得してください。
質問: {query}
今日の日付: {today}
回答はISO 8601形式の日付（YYYY-MM-DD）で返してください。
日付のみを回答してください。
""".strip()
            )
            chain = prompt | self.llm | StrOutputParser()

            target_date_string = chain.invoke({"query": query, "today": today})

            print({"target_date_string": target_date_string})
            return {"target_date_string": target_date_string}
        return date_node

    def get_schedule_node(self):
        def schedule_node(state: State) -> dict[str, Any]:
            print("Schedule node started with state:", state)
            query = state.query
            target_date_string = state.target_date_string

            request_session = requests.Session()

            access_token = session.get("access_token")
            if not access_token:
                return {"calendar_event": '認証情報の取得に失敗しました。ログインしてください。'}


            target_date = datetime.datetime.strptime(target_date_string, "%Y-%m-%d").date()
            time_min = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
            time_max = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"

            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": True,
                "orderBy": "startTime"
            }
            response = requests.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                params=params
            )
            if response.status_code != 200:
                return {"calendar_event": 'カレンダー情報の取得に失敗しました。'}

            events = response.json().get("items", [])
            event_summaries = []
            for event in events:
                print(f"Event: {event}")
                # 日時はdateTimeまたはdateのどちらか
                start = event.get("start", {})
                if "dateTime" in start:
                    date = start["dateTime"]
                else:
                    date = start.get("date")
                summary = event.get("summary", "")
                event_summaries.append(f"日時: {date}, 概要: {summary}")

            prompt = ChatPromptTemplate.from_template("""
以下の質問に対して、取得済みの予定から返答を生成してください。
質問: {query}
対象日: {target_date_string}
取得済みの予定: {event_summaries}
""".strip()
            )
            chain = prompt | self.llm | StrOutputParser()
            
            calendar_events = chain.invoke(
                {
                    "query": query,
                    "target_date_string": target_date_string,
                      "event_summaries": ",".join(event_summaries)
                }
            )

            print({"calendar_event": calendar_events})
            return {"calendar_event": calendar_events}
        return schedule_node
    
    def build_workflow(self):
        workflow = StateGraph(State)

        workflow.add_node("date_node", self.get_date_node())
        workflow.add_node("schedule_node", self.get_schedule_node())

        workflow.set_entry_point("date_node")
        workflow.add_edge("date_node", "schedule_node")
        workflow.add_edge("schedule_node", END)

        compiled_workflow = workflow.compile()
        compiled_workflow.get_graph().print_ascii()

        return compiled_workflow
