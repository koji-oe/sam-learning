<!-- omit in toc -->
# Tips

- [取得した依存関係が解決できない場合](#取得した依存関係が解決できない場合)
- [取得したモジュールの格納場所の確認方法](#取得したモジュールの格納場所の確認方法)
- [モジュールのオフライン展開](#モジュールのオフライン展開)
- [SAMテンプレートにおけるyamlタグエラー対策](#samテンプレートにおけるyamlタグエラー対策)
- [ローカルのAPI起動時に環境変数を設定する方法](#ローカルのapi起動時に環境変数を設定する方法)

## 取得した依存関係が解決できない場合

`pip install`したモジュールが認識されない場合がある。  
この場合はvscodeのLanguageServerの再起動を試すとよい。

1. Pythonスクリプトを開く
1. `Ctrl`+`Shift`+`P`
2. `Python: Restart Language Server`を実行

## 取得したモジュールの格納場所の確認方法

`pip install`したモジュールの格納場所を調べるには以下のコマンドを実行するとよい。  
今回はpytestを例にする。

```shell
python -m pip show pytest
```

以下に実行例を示す。  
`Location`にて格納場所が確認できる。

```shell
vscode ➜ /workspaces/sam-learning (main) $ python -m pip show pytest
Name: pytest
Version: 8.4.1
Summary: pytest: simple powerful testing with Python
Home-page: https://docs.pytest.org/en/latest/
Author: Holger Krekel, Bruno Oliveira, Ronny Pfannschmidt, Floris Bruynooghe, Brianna Laugher, Florian Bruhin, Others (See AUTHORS)
Author-email: 
License: MIT
Location: /home/vscode/.local/lib/python3.12/site-packages
Requires: iniconfig, packaging, pluggy, pygments
Required-by: 
```

## モジュールのオフライン展開

pipでインストールしたモジュールをオフライン環境に持ち込み、依存解決するには以下手順を実施するとよい。

1. オンライン環境で依存関係をアーカイブする。  
    以下により`./packages`に`.whl`や`.tar.gz`が保存される。

    ```shell
    pip download -r requirements.txt -d ./packages
    ```

2. オフライン環境に`packages`、`requirements.txt`を持ち込む。
3. オフライン環境にてネットワークアクセスなしでインストールする。

    ```shell
    pip install --no-index --find-links=./packages -r requirements.txt
    ```

## SAMテンプレートにおけるyamlタグエラー対策

> 【参考】  
> [Unresolved tagをちゃんと解決するyaml.customTags](https://zenn.dev/dannykitadani/articles/6678819ad7a4db)

vscodeのデフォルト設定では、`!Ref`等のSAMテンプレートのCloudFormation記法が誤りとして検出される。  
この警告をなくすため、カスタムタグを登録する。

`settings.json`にて以下設定を追加する。

```json
// samテンプレート用のカスタム定義
"yaml.customTags": [
    "!Base64",
    "!Base64 mapping",
    "!Cidr sequence",
    "!And sequence",
    "!Equals sequence",
    "!If sequence",
    "!Not sequence",
    "!Or sequence",
    "!Condition",
    "!FindInMap sequence",
    "!GetAtt",
    "!GetAtt sequence",
    "!GetAZs",
    "!ImportValue",
    "!Join sequence",
    "!Select sequence",
    "!Split sequence",
    "!Sub",
    "!Sub sequence",
    "!Transform mapping",
    "!Ref"
]
```

## ローカルのAPI起動時に環境変数を設定する方法

作成したAPIをローカルで起動する際には以下を実行する。  
これによりローカルコンテナでLambdaが動作する。

```shell
sam local start-api --port 3000
```

コンテナに環境変数を設定する際は、以下のように`--env-vars`パラメータで環境変数ファイルを設定するとよい。

```shell
sam local start-api --port 3000 --env-vars env/env.json
```

以下のように、template.yamlにて定義したResource名とEnvironment名と合わせる必要がある。

`env.json`

```json
{
    "AuthFunction": {
        "JWT_SECRET": "dev-secret"
    }
}
```

`template.yaml`

```yaml
# 認証用のLambda関数
AuthFunction:
    Type: AWS::Serverless::Function
    Properties:
        CodeUri: src/auth/
        Handler: app.lambda_handler
        Environment:
        Variables:
            JWT_SECRET_ARN: !Ref JwtSecret
            JWT_SECRET:
```
