# AWS Lambda の Python ランタイムイメージを使用します
# Python 3.9 をベースにしています
FROM public.ecr.aws/lambda/python:3.11

# 作業ディレクトリを /var/task に設定します。
# Lambda がコードを実行するデフォルトの場所です。
WORKDIR /var/task

COPY requirements.txt .

RUN pip install -r requirements.txt --target .

COPY app.py .

COPY agents/ agents/

CMD [ "app.lambda_handler" ]
