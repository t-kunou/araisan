
# プロジェクトのREADME

## Pylintの実行方法

pylintを実行するには、以下のコマンドを使用します：

```bash
pylint あなたの_pythonファイル.py
```

`あなたの_pythonファイル.py` を実際のPythonファイルのパスに置き換えてください。

## requirements.txtからライブラリをインストールする方法

requirements.txtにリストされているライブラリをインストールするには、以下のコマンドを使用します：

```bash
pip install -r requirements.txt
```

## Dockerイメージを作成する手順

DockerfileからDockerイメージを作成するには、以下のコマンドを使用します：

```bash
docker build -t あなたのイメージ名 .
```

`あなたのイメージ名` を使用したいイメージの名前に置き換えてください。

## Dockerコンテナを起動する方法

作成したDockerイメージを使用してコンテナを起動するには、以下のコマンドを使用します：

```bash
docker run -p 51958:51958 --name あなたのコンテナ名 あなたのイメージ名
```

`あなたのコンテナ名` を使用したいコンテナの名前に置き換えてください。
