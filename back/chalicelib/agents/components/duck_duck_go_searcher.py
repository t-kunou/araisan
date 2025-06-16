import requests
from urllib.parse import quote
import json
from typing import Optional, List, Dict
import time
from duckduckgo_search import DDGS

class DuckDuckGoSearcher:
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def advanced_search_with_duckduckgo_search(self, 
                                               query: str,
                                               region: str = "jp-jp",
                                               language: str = "ja",
                                               site: Optional[str] = None,
                                               max_results: int = 10) -> List[Dict]:
        """
        duckduckgo-searchライブラリを使用した高度な検索
        注意: pip install duckduckgo-search が必要
        """
        try:
            # サイト指定がある場合はクエリに追加
            search_query = f"site:{site} {query}" if site else query

            with DDGS() as ddgs:
                results = []
                search_results = ddgs.text(
                    keywords=search_query,
                    region=region,
                    safesearch='moderate',
                    timelimit=None,
                    max_results=max_results
                )

                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'source': result.get('href', '').split('/')[2] if result.get('href') else ''
                    })

                return results

        except Exception as e:
            print(f"検索エラー: {e}")
            return []


# 使用例
def main():
    searcher = DuckDuckGoSearcher()

    print("3. 特定ドメインでの検索:")
    domain_results = searcher.advanced_search_with_duckduckgo_search(
        query="AIニュース",
        site="ledge.ai",
        region="jp-jp",
        max_results=5
    )

    for i, result in enumerate(domain_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print()

# 実行例
if __name__ == "__main__":
    main()