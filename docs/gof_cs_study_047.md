# 第47章：Facade ②：.NETで体感（File / HttpClient）📦🌐

## ねらい 🎯✨

* 「中はめちゃくちゃ複雑だけど、入口はシンプル！」という **Facadeの気持ち**を、.NETの代表例で体感するよ😊
* 公式ドキュメントを読みながら、「呼ぶ側が知らなくて済んでること」を見抜けるようになるよ👀📘

---

## 到達目標 ✅🌸

* `File` / `Directory` を見て「何を隠してくれてる入口なのか」を3つ説明できる🙂📁
* `HttpClient` を見て「何を隠してくれてる入口なのか」を3つ説明できる🙂🌐 ([Microsoft Learn][1])
* `HttpMessageHandler` を差し替えて、**ネットに出ずに** `HttpClient` の動作をテストできる🧪✨（差し替え点が分かる）

---

## 手順 🧭🧩

### 1) `File` は「ファイル操作の入口（Facade）」📄🚪

![Image](./picture/gof_cs_study_047_facade_dotnet_apis.png)

`File` の良さは、**細かい設定を知らなくても**「読み書き」ができるところだよ😊
たとえば本当は裏でこういう面倒がある👇

* 文字コード（Encoding）どうする？🌀
* `Stream` をどう開く？（共有モード、バッファ、権限…）🔓
* 例外（存在しない/権限ない/ロック中）どう扱う？⚠️

まずは「入口の便利さ」を体感しよう👇✨

```csharp
using System.Text;

var dir = Path.Combine(Path.GetTempPath(), "gof-facade");
Directory.CreateDirectory(dir);

var path = Path.Combine(dir, "hello.txt");

await File.WriteAllTextAsync(path, "Hello Facade 👋✨", Encoding.UTF8);
var text = await File.ReadAllTextAsync(path, Encoding.UTF8);

Console.WriteLine(text);
```

次に、**同じことを低レベルでやると何が増えるか**を眺めてみるよ👀
（※ “これを毎回書かなくていい” が Facade のご褒美🍬）

```csharp
using System.Text;

var path = Path.Combine(Path.GetTempPath(), "gof-facade", "hello-low.txt");

await using var fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None);
await using var sw = new StreamWriter(fs, Encoding.UTF8);
await sw.WriteAsync("Hello Low-level 👋🧰");
```

✅ 観察ポイント（メモしてね📝）

* `File.WriteAllTextAsync` は **「開く + 書く + 閉じる」** をまとめてくれてる？
* 低レベル版は `using` が増えた？（資源管理の責務が呼ぶ側に来た）
* 例外が起きたとき、どこで何が起きたか追いやすい/追いにくいは？🤔

---

### 2) `HttpClient` は「HTTP通信の入口（Facade）」📡🚪

`HttpClient` は “HTTPで通信する” っていう巨大な話を、かなりスッキリした形で触らせてくれる入口だよ🙂🌐 ([Microsoft Learn][1])

でも裏側には、こんな複雑さがいる👇

* DNS / 接続の再利用 / ソケット管理 🧵
* TLS(HTTPS) / プロキシ / リダイレクト 🔐
* リクエスト/レスポンスのパイプライン（ハンドラ）🧩

ここで大事なのが、**入口（HttpClient）はシンプルだけど、差し替え点（Handler）はちゃんとある**ってこと✨

```mermaid
classDiagram
    class HttpClient {
        +GetAsync()
        +PostAsync()
    }
    class HttpMessageHandler {
        <<Abstract>>
        #SendAsync()
    }
    class SocketsHttpHandler {
        (Actual Network)
    }
    class DelegatingHandler {
        (Middleware)
    }
    
    HttpClient o-- HttpMessageHandler : Uses
    HttpMessageHandler <|-- SocketsHttpHandler
    HttpMessageHandler <|-- DelegatingHandler
    DelegatingHandler --> HttpMessageHandler : Inner
    
    note for HttpClient "入口(Facade)"
    note for HttpMessageHandler "差し替え点"
```

それは “ネット無しテスト” で体感するよ🧪

---

### 3) 差し替え点を触る：`HttpMessageHandler` を偽物にする🪄🧪

これができると、

* 本番：本物のネットワークへ🌐
* テスト：偽物の応答で安定🧪
  って切り替えできる😊

```csharp
using System.Net;
using System.Net.Http;

sealed class FakeHandler : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        // どんなリクエストが来たか覗ける👀
        if (request.RequestUri?.AbsolutePath == "/ping")
        {
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent("{\"ok\":true}")
            });
        }

        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound));
    }
}

var client = new HttpClient(new FakeHandler())
{
    BaseAddress = new Uri("https://example.test")
};

var json = await client.GetStringAsync("/ping");
Console.WriteLine(json); // {"ok":true}
```

✅ 観察ポイント（ここ超Facadeっぽい💡）

* 呼ぶ側は「HTTPの全部」を知らなくていい（`GetStringAsync` だけでOK）
* でも裏側の差し替え（`HttpMessageHandler`）で挙動が変えられる
* “入口は簡単、内部は差し替え可能” が見えたら勝ち🏆✨

---

### 4) 依存性注入を使うアプリでは `IHttpClientFactory` の入口もある🧩🏭

WebアプリやDI前提のアプリだと、`HttpClient` を作りっぱなしにせず、**工場（Factory）経由で扱うのが推奨される流れ**があるよ🙂
（接続管理まわりの事故を避けやすくするためのガイドが用意されてる🧯） ([Microsoft Learn][2])

---

## 落とし穴 ⚠️😵‍💫

### `File` / `Directory` あるある📁

* パス結合を文字列連結でやってバグる（`Path.Combine` を使う）🧩
* 文字コードを意識せず文字化け（必要なら `Encoding.UTF8` を渡す）🌀
* 大きいファイルを `ReadAllText` で一気読みしてメモリが苦しい😵（必要ならStream系へ）

### `HttpClient` あるある🌐

* リクエストごとに `new HttpClient()` を乱発して、接続まわりが苦しくなる系の事故😱

  * ガイドラインとして **再利用**や **Factory（DI環境）** の話が用意されてるよ📘 ([Microsoft Learn][3])
* タイムアウト/キャンセル無しで「待ちっぱなし」になる⏳🫠（`CancellationToken` も意識✨）
* `HttpResponseMessage` / `HttpContent` の扱いが雑でリソースが残る（状況により `using` を検討）🧹

---

## 演習 ✍️🎀（10〜30分×2）

### 演習A：`File` を入口として使う📄✨

1. 一時フォルダに `order.txt` を作って、注文IDを1行だけ書く🛒
2. 同じファイルを読んで、文字列が一致することを確認する✅
3. できたら「低レベル版（FileStream + StreamWriter）」も書いて、差分をメモ📝

### 演習B：`HttpClient` をネット無しでテスト🧪🪄

1. `FakeHandler` を少し改造して、`/orders/123` を返すようにする📦
2. `GetStringAsync("/orders/123")` の戻りを `Assert` で検証する✅
3. “Facadeとして `HttpClient` は簡単 / Handlerで差し替えできる” を1文で書く📝✨

---

## チェック ✅🔍

* `File` が隠している面倒を **3つ**言える？（例：Stream管理/Encoding/例外など）📄
* 低レベル実装と比べて、`File` の「入口の価値」を説明できる？🚪✨
* `HttpClient` が隠している面倒を **3つ**言える？（接続/TLS/パイプラインなど）🌐
* `HttpMessageHandler` を差し替えて、**ネット無し**でテストできた？🧪🎉
* 「入口は簡単・内部は複雑・でも差し替え点がある」って言えた？🧩🌸

[1]: https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient?view=net-10.0 "https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient?view=net-10.0"
[2]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0 "https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0"
[3]: https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines "https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines"
