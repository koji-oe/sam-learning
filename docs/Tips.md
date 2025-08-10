<!-- omit in toc -->
# Tips

- [取得した依存関係が解決できない場合](#取得した依存関係が解決できない場合)
- [取得したモジュールの格納場所の確認方法](#取得したモジュールの格納場所の確認方法)
- [モジュールのオフライン展開](#モジュールのオフライン展開)
- [SAMテンプレートにおけるyamlタグエラー対策](#samテンプレートにおけるyamlタグエラー対策)
- [ローカルのAPI起動時に環境変数を設定する方法](#ローカルのapi起動時に環境変数を設定する方法)
- [ローカルのAPI起動のコンテナイメージpullに失敗する場合](#ローカルのapi起動のコンテナイメージpullに失敗する場合)
- [Lambdaレイヤーのパス解決](#lambdaレイヤーのパス解決)
- [`sam local start-api`実行時の接続エラー解消](#sam-local-start-api実行時の接続エラー解消)
- [Aurora DSQLにおけるトランザクション制約対策](#aurora-dsqlにおけるトランザクション制約対策)

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

## ローカルのAPI起動のコンテナイメージpullに失敗する場合

dev-containers内でdockerの認証がうまくいかないことが原因の可能性がある。  
その場合以下の内容でdev-containers内の`~/.docker/config.json`を編集することで解消することがある。

```shell
echo '{' > ~/.docker/config.json
echo '  "auths": {},' >> ~/.docker/config.json
echo '  "HttpHeaders": {' >> ~/.docker/config.json
echo '    "User-Agent": "Docker-Client/20.10.24 (linux)"' >> ~/.docker/config.json
echo '  }' >> ~/.docker/config.json
echo '}' >> ~/.docker/config.json
```

## Lambdaレイヤーのパス解決

Lambdaでは共通モジュールをレイヤーに切り出すことで、共通処理の一元管理やデプロイサイズの抑制が可能となる。  
vscodeによるローカル開発時とLambdaデプロイ時のパス解決方法について記載する。

現在以下の構成で、`layers/{レイヤー}/python/モジュール`といった構成でレイヤー資材を管理している。

```txt
.
├── layers
│   └── auth_layer
│       ├── python
│       │   └── auth_middleware.py
│       └── requirements.txt
└── src
    ├── auth
    │   ├── app.py
    │   └── requirements.txt
    └── users
        ├── app.py
        └── requirements.txt
```

ローカル開発時には、`lambda_handler`の配置先である`src/{Lambda関数}/モジュール`より`layer`配下のモジュールを解決するために、`.vscode/settings.json` にて以下の設定を追加している。

```json
"python.analysis.extraPaths": [
    "./sam-python-learning/layers/auth_layer/python"
],
```

Lambdaデプロイ時の動作では、LambdaにLayerをアタッチすると、実行環境ではそのLayerの中の`python/`ディレクトリが自動的に`sys.path`に追加される。

## `sam local start-api`実行時の接続エラー解消

`sam local start-api`によるローカルコンテナでのLambda実行にて、Aurora DSQL接続を検証するとDB接続エラーになることがある。

```txt
Invalid lambda response received: Invalid API Gateway Response Keys: {'errorType', 'requestId', 'errorMessage', 'stackTrace'} in {'errorMessage': 'connection is bad: connection to server at          
"2406:da14:1713:ba03:1755:b00b:6b7c:39c7", port 5432 failed: Network is unreachable\n\tIs the server running on that host and accepting TCP/IP connections?\nMultiple connection attempts failed. All  
failures were:\n- host: \'lyabujqnync4f2ifscd5rt4utu.dsql.ap-northeast-1.on.aws\', port: None, hostaddr: \'18.99.75.128\': connection failed: connection to server at "18.99.75.128", port 5432 failed:
FATAL:  unable to accept connection, access denied\nDETAIL:  Session Id: hrtcjl3zfmhx6gn4gr22mtatm4\nHINT:  The security token included in the request is invalid.\n- host:                            
\'lyabujqnync4f2ifscd5rt4utu.dsql.ap-northeast-1.on.aws\', port: None, hostaddr: \'2406:da14:1713:ba03:1755:b00b:6b7c:39c7\': connection is bad: connection to server at                               
"2406:da14:1713:ba03:1755:b00b:6b7c:39c7", port 5432 failed: Network is unreachable\n\tIs the server running on that host and accepting TCP/IP connections?', 'errorType': 'OperationalError',         
'requestId': 'fc6c4fc5-98fb-4ae1-a3af-2f1e9df19d7b', 'stackTrace': ['  File "/var/task/app.py", line 15, in lambda_handler\n    conn = psycopg.connect(\n', '  File "/var/task/psycopg/connection.py", 
line 125, in connect\n    raise type(last_ex)("\\n".join(lines)).with_traceback(None)\n']}                                                                                                             
2025-08-10 06:49:36 127.0.0.1 - - [10/Aug/2025 06:49:36] "POST /dsql/init HTTP/1.1" 502 -
```

上記エラーの場合、IPv6で接続を試みており、コンテナ内にIPv6ルートがないために接続エラーとなっている可能性が高い。  
この場合は、実行時のコマンドにオプションを付与してホストネットワークで動かすことで解消する。

```shell
sam local start-api --env-vars env/env.json --docker-network host
```

## Aurora DSQLにおけるトランザクション制約対策

Aurora DSQLでは1トランザクションで3000行までしか追加、削除、更新ができない。  
これに対する対策として、`limit`句や`returning`句を用いた対処法がある。

以下のように`limit`句を用いて1トランザクションにおける更新レコード数を制限し、`returning`句を用いて更新対象データの情報を取得することで削除件数が0となるまでトランザクションを分割して処理をクエリ返す。

```python
batch_size = 3000
total_deleted = 0

while True:
    cur.execute(
        """
        delete from users
        where id in (
            select id from users
            order by created_datetime
            limit %s
        )
        returning id
        """, (batch_size,)
    )
    deleted_rows = cur.fetchall()
    if not deleted_rows:
        break
    total_deleted += len(deleted_rows)
```

尚、Deleteの場合は上記の通り繰り返すことでいつか0件になると考えられるが、Updateの場合は更新範囲をずらしながら処理する必要がある。  
`offset`句を用いることもできるがパフォーマンスが低いため、`returning`句で主キーを利用した更新方式の方が推奨される。

```python
batch_size = 3000
last_max_id = None
total_updated = 0

while True:
    if last_max_id:
        cur.execute(
            """
            update users
            set password = 'newpassword'
            where id in (
                select id from users
                where id > %s
                order by id
                limit %s
            )
            returning id
            """,
            (last_max_id, batch_size)
        )
    else:
        # 初回はlast_max_idなし
        cur.execute(
            """
            update users
            set password = 'newpassword'
            where id in (
                select id from users
                order by id
                limit %s
            )
            returning id
            """,
            (batch_size,)
        )
    updated_rows = cur.fetchall()
    if not updated_rows:
        break

    last_max_id = max(row[0] for row in updated_rows)
    total_updated += len(updated_rows)
```
