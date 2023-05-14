"""
エントリポイント
引数の解析(ユーザーからのインプットのハンドリング)
CSVの作成(ユーザーへのアウトプットのハンドリング)
パッケージからセッション情報を受け取る
"""

import argparse
import csv

from pyconus import scrape


def to_csv(sessions: list, output, fields):
    with open(output, "w") as f:
        # ディクショナリのリストを書き込むためのクラス
        # fieldnamesはヘッダーの名前
        # extrasactionは指定されたキー以外のキーを持っている場合の動作を制御する
        # ignoreにすると、無視。デフォルトだと例外を出す。
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for session in sessions:
            writer.writerow(session)


def main():
    """
    デフォルトの引数を用意してもOK
    add_argument()を使って、fieldを選べるようにもできる
    """
    default = [field for field in FIELDS]
    # コマンドライン引数をパース(解析)するための情報を保持する
    parser = argparse.ArgumentParser()
    # output(今回はファイル名)を設定する。何も設定しなかったら、デフォルト値が呼び出される。
    parser.add_argument("--output", default="pyconus.csv")
    #  fieldsを指定できる。'+'をつけることで、複数の引数を入力することができる
    parser.add_argument(
        "--fields",
        nargs="+",
        choices=FIELDS,
        default=default,
        help=f"出力ファイルに含めるフィールド (default: {' '.join(default_fields)})",
    )

    # コマンドラインを解析して、その値をargsとして保持
    args = parser.parse_args()
    print(args.output)
    print(args.fields)

    # ジェネレーター式を利用して辞書に変換。()を使う。要素を一つずつ生成する。
    # メモリの効率を高める。
    sessions = (session.to_dict() for session in scrape())
    to_csv(sessions, args.output, args.fields)


if __name__ == "__main__":
    main()
