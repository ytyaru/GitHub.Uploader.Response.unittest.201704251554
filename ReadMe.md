# このソフトウェアについて

`./web/http/Response.py`の単体テストをした。

内部クラスと合わせて4クラスある。

* `Response.Headers.ContentType`
* `Response.Headers.Link`
* `Response.Headers`
* `Response`

# バグ発見

## `Response.Headers.ContentType`クラス

* `Split`関数
    * `suffix`を取得できなかった
```python
#if self.sub_type.endswith('+'):
if '+' in self.sub_type:
```

## `Response.Headers.Link`クラス

* `__get_page`関数
    * `TypeError: string indices must be integers`
        * `print('page={0}'.format(url.query['page']))`
            * URL文字列のうちpage引数値を返したつもりのコードと思われる
            * `urlparse.query`の返却値はdict型でなくstr型である
                * `k1=v1&k2=v2`の文字列になるのであって`{'k1': 'v1', 'k2': 'v2'}`ではない
                * 修正しようと思ったが、そもそもpage値を返すのでなくURLを返すべきでないのか？（以下に続く）
* `Next`,`Prev`,`First`,`Last`
    * 期待しているのはURL全体か、URLのpage引数値か
        * 呼出先では`url`変数に入れているが、実装元ではpageを返している
            * このコードが実行されたらURLとしてpage値を設定することになりURL参照できないはず
            * 今まではページネーションが必要な場面に出くわしていなかったため発見されなかったと思われる
```
$ find . -name "*.py" | xargs grep "Link.Next("
./web/service/github/api/v3/users/Emails.py:            url = self.__response.Headers.Link.Next(r)
./web/service/github/api/v3/users/SshKeys.py:            url = self.__response.Headers.Link.Next(r)
./web/service/github/api/v3/repositories/Repositories.py:            url = self.__response.Headers.Link.Next(r)
./web/service/github/api/v3/miscellaneous/Licenses.py:            url = self.__response.Headers.Link.Next(r)
```
Response.pyのLinkクラス。Next関数ではURLでなくpageを返そうとしている。
```
def Next(self, r):
    return self.__get_page(r, 'next')
def __get_page(self, r, rel='next'):
    if None is r:
        return None
    print(r.links)
    if rel in r.links.keys():
        url = urlparse(r.links[rel]['url'])
        print('page={0}'.format(url.query['page']))
        return url.query['page']
```
`Repositories.py`ではpageが欲しいわけではなくURL全体を求めている。`params`に`page`を渡してやる必要がある。
```python
repos = []
url = urllib.parse.urljoin('https://api.github.com', 'user/repos')
while (None is not url):
    web.log.Log.Log().Logger.debug(url)
    params = self.__GetCreateParameter(visibility, affiliation, type, sort, direction, per_page)
    web.log.Log.Log().Logger.debug(params)
    r = requests.get(url, **params)
    repos += self.__response.Get(r)
    url = self.__response.Headers.Link.Next(r)
return repos
```

```python
url = self.__response.Headers.Link.Next(r)
```
上記コードを以下のどれかに修正したい。
```python
# 案1
url = self.__response.Headers.Link.Get(r, rel='next')
# 案2
url = self.__response.Headers.Link.Next(r)
# 案3
url = self.__response.Headers.Link.NextUrl(r)
page = self.__response.Headers.Link.NextPage(r)
# 案4
url = self.__response.Headers.Link.Next(r)
page = self.__response.Headers.Link.NextPage(r)
```
案4を採用する。したがって`Response.py`は以下のようになる。
```python
def Next(self, r):
    return self.__get_url(r, 'next')
def NextPage(self, r):
    return self.__get_page(r, 'next')
def __get_page(self, r, rel='next'):
    ...
    if rel in r.links.keys():
        return r.links[rel]['url']
    else:
        return None
def __get_page(self, r, rel='next'):
    ...
    if rel in r.links.keys():
        url = urlparse(r.links[rel]['url'])
        query = {}
        for kv in url.query.split('&'):
            key, value = kv.split('=')
            query[key] = value
        if 'page' in query.keys():
            return query['page']
        else:
            return None
    else:
        return None
```

ここまで考えたが、そもそもLinkクラスは必要か？`requests`ライブラリのおかげで`r.links['next']['url']`, `r.links['next']['page']`などとすれば良いだけである。Linkクラスは無駄なラッパに思える。'next'などの文字リテラルは使いたくない。しかし`Next()`などの関数にしたところで、Pythonは未定義な関数名をコンパイルエラーで出してくれるわけではない。存在しない文字リテラルと同様に実行時エラーにならないとエラーを見つけられない。ならば単体テストをしてコードを実行し確かめることが重要ではないか。

A. Linkクラスの呼出箇所をすべて`r.links['next']['url']`のように修正する
B. ページネーションでループしてHTTPリクエストするクラスを生成する

Bを採用。

## `Paginator.py`クラス新規生成

`Paginator.py`クラスを新規生成して以下の関数をつくる。

```python
def Paginate(self, url, **kwargs):
    response = []
    while (None is not url):
        r = requests.get(url, **kwargs)
        response += self.__response.Get(r)
        if 'links' in r or None is r.links or 'next' not in r.links or 'url' not in r.links['next']:
            url = None
        else:
            url = r.links['next']['url']
    return response
```

# バグとは言えないが気になる点

* `Response.Headers.ContentType`クラス
    * `Split`関数
        * `sub_type`
            * [サブタイプはツリー、サブタイプ名、サフィックスに分解できる](https://ja.wikipedia.org/wiki/%E3%83%A1%E3%83%87%E3%82%A3%E3%82%A2%E3%82%BF%E3%82%A4%E3%83%97#.E5.91.BD.E5.90.8D.E8.A6.8F.E5.89.87)が、すべて含めてサブタイプ名とした
                * 理由は需要があるのかわからないのに面倒が増えるから

# テスト省略

* `Response`クラス
    * Image, BeautifulSoupについてもテストすべきだが、今回はGitHubAPIが返すJSONさえ確認できればOKなので省略

# 前回までのGitHubアップローダ単体テスト用リポジトリ

* [GitHub.API.Authentication.Abstract.201704141006](https://github.com/ytyaru/GitHub.API.Authentication.Abstract.201704141006)
* [Github.Uploader.SshConfigurator.unittest.201704221606](https://github.com/ytyaru/Github.Uploader.SshConfigurator.unittest.201704221606)
* [Github.Uploader.SshKeyGen.unittest.201704221809](https://github.com/ytyaru/Github.Uploader.SshKeyGen.unittest.201704221809)
* [Github.Uploader.Json2Sqlite.unittest.201704230804](https://github.com/ytyaru/Github.Uploader.Json2Sqlite.unittest.201704230804)
* [GitHub.Uploader.Log.unittest.201704251509](https://github.com/ytyaru/GitHub.Uploader.Log.unittest.201704251509)

# 開発環境

* Linux Mint 17.3 MATE 32bit
* [Python 3.4.3](https://www.python.org/downloads/release/python-343/)
* [SQLite](https://www.sqlite.org/) 3.8.2

## WebService

* [GitHub](https://github.com/)
    * [アカウント](https://github.com/join?source=header-home)
    * [AccessToken](https://github.com/settings/tokens)
    * [Two-Factor認証](https://github.com/settings/two_factor_authentication/intro)
    * [API v3](https://developer.github.com/v3/)

# ライセンス

このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

Library|License|Copyright
-------|-------|---------
[requests](http://requests-docs-ja.readthedocs.io/en/latest/)|[Apache-2.0](https://opensource.org/licenses/Apache-2.0)|[Copyright 2012 Kenneth Reitz](http://requests-docs-ja.readthedocs.io/en/latest/user/intro/#requests)
[dataset](https://dataset.readthedocs.io/en/latest/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2013, Open Knowledge Foundation, Friedrich Lindenberg, Gregor Aisch](https://github.com/pudo/dataset/blob/master/LICENSE.txt)
[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright © 1996-2011 Leonard Richardson](https://pypi.python.org/pypi/beautifulsoup4),[参考](http://tdoc.info/beautifulsoup/)
[pytz](https://github.com/newvem/pytz)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2003-2005 Stuart Bishop <stuart@stuartbishop.net>](https://github.com/newvem/pytz/blob/master/LICENSE.txt)
[furl](https://github.com/gruns/furl)|[Unlicense](http://unlicense.org/)|[gruns/furl](https://github.com/gruns/furl/blob/master/LICENSE.md)
[PyYAML](https://github.com/yaml/pyyaml)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2006 Kirill Simonov](https://github.com/yaml/pyyaml/blob/master/LICENSE)

