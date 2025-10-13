# Pythonパッケージテンプレート
本プロジェクトはパッケージングできるpythonプロジェクトを作成するときに使用するテンプレートです。

## Build
以下にてビルドを実施

```
./build.sh
```

## Install
以下にてインストールを実施

```
pip install python_package_project_template-0.0.1-py3-none-any.whl
```

## How to use

```
from example_package import example
example.add_one(1)
```

## Clone this
このリポジトリを関係を保持したままCloneする
```
# 前提
GitHubにて空のリポジトリ作成

# 変数定義
UPSTREAM_REPOSITORY_NAME="python_package_project_template"
UPSTREAM_REPOSITORY_URL="git@github.com:daisuke6106/${UPSTREAM_REPOSITORY_NAME}.git"
NEW_REPOSITORY_NAME="NewRepName"
NEW_REPOSITORY_URL="git@github.com:daisuke6106/${NEW_REPOSITORY_NAME}.git"

# クローン->Push
git clone ${UPSTREAM_REPOSITORY_URL} ${NEW_REPOSITORY_NAME}
cd ${NEW_REPOSITORY_NAME}
git remote add     upstream ${UPSTREAM_REPOSITORY_URL}
git remote set-url origin   ${NEW_REPOSITORY_URL}
git branch -M main
git push -u origin main
```

[参考１](https://packaging.python.org/ja/latest/tutorials/packaging-projects/)
