from pydantic import BaseModel, Field
import operator
from typing import Annotated

class State(BaseModel):
    query: str = Field(
        ..., description="ユーザーからの質問",
    )
    messages: Annotated[list[str], operator.add] = Field(
        default=[],
        description="回答履歴"
    )
    target_region_code: str = Field(
        default="",
        description="選定された地域コード"
    )
    location: str = Field(
        ...,
        description="ユーザーの位置情報"
    )
    weather: str = Field(
        default="",
        description="天気予報の結果"
    )
    seasonal_foods: Annotated[list[str], operator.add] = Field(
        default_factory=list,
        description="季節の食材のリスト"
    )
    dinner_suggestion: str = Field(
        default="",
        description="季節の食材を使った夕食の提案"
    )
    today: str = Field(
        default="",
        description="今日の日付"
    )
    selected_agent: str = Field(
        default="",
        description="選択されたエージェントの番号"
    )
    common_answer: str = Field(
        default="",
        description="共通エージェントの回答"
    )
    general_answer: str = Field(
        default="",
        description="フロー全体の回答"
    )
    sight_seeing_result: str = Field(
        default="",
        description="観光地の提案結果"
    )
    web_search_result: str = Field(
        default="",
        description="Web検索の結果"
    )
    generated_query: str = Field(
        default="",
        description="生成されたクエリ"
    )
    araisan_result: str = Field(
        default="",
        description="アライサンの結果"
    )
    kana_answer: str = Field(
        default="",
        description="かな変換された回答"
    )
    target_date_string: str = Field(
        default="",
        description="ターゲット日付の文字列"
    )
    calendar_event: str = Field(
        default="",
        description="カレンダーイベントの情報"
    )
