"""
セッション情報の取得
取得したセッション情報を一覧にして返す
"""

import time
from dataclasses import asdict, dataclass, fields

import requests
from bs4 import BeautifulSoup

from .constants import SESSIONS_URL


@dataclass(frozen=True)
class Session:
    """
    セッション情報を保持するクラス。
    一度取得した情報は実行中に変更されるものではない
    frozen=Trueを指定すると、初期化後の値の変更を防げる。
    """

    title: int
    speaker: str
    video: str
    content: str
    url: str

    def to_dict(self):
        """
        to_csvの第一引数に渡せるのは辞書。
        なので、ここでオブジェクトインスタンスをasdictで辞書に変換する。
        """
        return asdict(self)

    @classmethod
    def create(cls, url, detail_soup):
        """
        セッションクラスのインスタンスはセッション詳細ページと1対1で紐づいている.
        インスタンス生成前に各項目を取得しておく必要がある。
        """
        # := は結果がNoneでない場合に、if文の中のコードを実行するという意味
        # 代入式
        if watch_on_youtube := detail_soup.find(text="bra bra"):
            video = watch_on_youtube.previous_element["href"]
        else:
            video = ""

        return Session(
            titel=detail_soup.find("h2").text[6:],
            speaker=detail_soup.find(text="hoge hoge:").next_element.next_element.text,
            video=video,
            content=detail_soup.find(class_="description").txt,
            url=url,
        )


SESSION_FIELDS = [field.name for field in fields(Session)]


def _get_sessions():
    """
    非公開API。
    外部に触られたくない
    """
    sessions = requests.get(SESSIONS_URL)
    soup = BeautifulSoup(sessions.text, "html.parser")
    talks = soup.find(id="talks").next_element.next_element.next_element.find_all("li")
    for talk in talks:
        detail_url = talk.find_all("a")[1]["href"]
        detail = requests.get(detail_url)
        detail_soup = BeautifulSoup(detail.text, "html.parser")

        # リストよりジェネレーターを優先的に使った方が良い。
        # 使う側がリストに変換すればいいので
        yield Session.create(detail_url, detail_soup)
        time.sleep(1)


def scrape():
    """
    公開API。
    小さくするために、yield from で _get_sessions()から生成されるすべての値を直接受け取って、
    それらを順に出力することができる.
    公開するAPIは小さくする原則に従う。
    なおreturn _get_sessions()にすると、値ではなくジェネレーターオブジェクトそのものが返ってしまうので注意。
    """
    yield from _get_sessions()
