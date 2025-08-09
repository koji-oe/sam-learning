<!-- omit in toc -->
# Tips

- [取得した依存関係が解決できない場合](#取得した依存関係が解決できない場合)
- [取得したモジュールの格納場所の確認方法](#取得したモジュールの格納場所の確認方法)

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
