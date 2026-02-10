# 第15章：Factory Method ②：.NET定番例を読む🔐

![第15章. Factory Method ②：標準クラスで体感](./picture/gof_cs_study_015_dotnet_factories.png)

## ねらい 🎯

* 「Factory MethodっぽいAPI」を .NET標準で見つけて、“現実の形”を体に入れる😊
* 「呼び出し側が、何を知らなくて済むのか？」を言語化できるようにする🧠✨
* 例外・`Dispose`・契約（ルール）まで含めて読めるようになる🔍🧹

---

## 到達目標 ✅

* `Create()` 系APIで「戻り型が抽象寄り」になっている理由を説明できる🙂
* 「差し替え点（どこを変えれば挙動が変わる？）」を3つ挙げられる🔁
* `IDisposable` の扱い（`using`）を見落とさずに読める🧤♻️

---

## 手順 🧭

### 1) まずは“Factory Method発見テンプレ”で読む🔍✨

APIを見たら、この順でチェックすると迷子になりにくいよ😊

* **① 生成メソッド名**：`Create` / `CreateXxx` / `CreateClient` みたいな名前？🏭
* **② 戻り型**：`abstract class` / `interface` / 基底クラス寄り？（具体型じゃない？）🧩
* **③ 呼び出し側が隠せるもの**：

  * 具体クラス名（どれが作られてるか）🙈
  * 初期化の面倒（設定、内部構成）🧰
  * ライフサイクル（使い回し・破棄のルール）♻️
* **④ 契約**：例外 / `null` になる？ / `Dispose` 必要？⚠️
* **⑤ 差し替え点**：引数（名前/設定）や登録（DI）で変わる？🔁

---

### 2) 定番例①：暗号APIの `Create()` を読む🔐🧪

暗号系は「具体実装を隠して、使い方だけを統一」してる代表例だよ✨

* **ポイント**

  * `SHA256.Create()` は **SHA256の具体実装（OS依存や最適化）** を呼び出し側から隠す🙈
  * 呼び出し側は **“SHA256としての契約”** だけ知ってればOK👌
  * 多くが `IDisposable`（リソース持つ）なので `using` が超大事🧤

```csharp
using System.Security.Cryptography;
using System.Text;

// 例：SHA-256 ハッシュを作る（Factory Method: SHA256.Create）
static string ComputeSha256Hex(string text)
{
    byte[] data = Encoding.UTF8.GetBytes(text);

    using SHA256 sha = SHA256.Create(); // ← ここがFactory Methodっぽい
    byte[] hash = sha.ComputeHash(data);

    return Convert.ToHexString(hash); // .NET標準のHEX変換
}
```

✅ **呼び出し側が知らなくてよい情報（例）**

* `SHA256` の具体クラス名（どの実装か）
* 内部でどのネイティブ機能を使うか
* 実装差（環境で最適化される/されない等）

⚠️ **読み落としがち**

* `using` しないと、リソースが残る可能性（特に大量処理で影響）💦
* `ComputeHash` は **バイト列** 前提なので、文字列→バイト変換の規約（UTF-8等）を決める必要がある🧾


```mermaid
graph LR
    User[呼び出し側] -->|Create| Abstract[抽象クラス: SHA256]
    Abstract -.->|隠蔽| Concrete[具体実装: SHA256Managed / CNG]
    User -->|使う| Abstract
```

---

### 3) 定番例②：`TextWriter` と `StreamWriter`（＋`File.CreateText`）📝📁

ここは「戻り型を抽象（`TextWriter`）に寄せる」感覚を掴むのに最高💕

* `StreamWriter` はファイルへ書ける具体クラス
* でも呼び出し側は **`TextWriter` として扱う** と差し替えしやすい✨
* さらに `File.CreateText(path)` は “生成を押し出す” 典型（Factory Methodっぽい）🏭

```csharp
using System.IO;
using System.Text;

// 依存先を TextWriter にするのがミソ🧡
static void WriteOrderSummary(TextWriter writer, int orderId, decimal total)
{
    writer.WriteLine($"OrderId: {orderId}");
    writer.WriteLine($"Total: {total:0.00}");
}

// 本番：ファイルに書く📁
static void WriteToFile(string path)
{
    using TextWriter writer = File.CreateText(path); // ← 生成を押し出す（Factory Methodっぽい）
    WriteOrderSummary(writer, orderId: 1001, total: 2980m);
}

// テスト：メモリに書く🧪（差し替えが超ラク）
static string WriteToString()
{
    using var sw = new StringWriter();
    WriteOrderSummary(sw, orderId: 1001, total: 2980m);
    return sw.ToString();
}
```

✅ **呼び出し側が知らなくてよい情報（例）**

* 書き込み先が「ファイル」なのか「文字列」なのか
* `Stream` の扱い、エンコーディングやバッファ戦略の細部（必要なら外から注入）

⚠️ **契約ポイント**

* `StreamWriter` / `TextWriter` は基本 `IDisposable`：`using` を忘れない♻️
* ファイルの場合、エンコーディング指定（UTF-8など）を要件に合わせる🧾

  * 例：`new StreamWriter(path, append: false, Encoding.UTF8)`

---

### 4) 定番例③：`IHttpClientFactory.CreateClient()` 🌐🏭

「生成＋初期化＋ライフサイクル（使い回し）」が絡むと、Factory Methodの価値が爆上がりする🔥

* `IHttpClientFactory` は **HttpClient生成の窓口**
* `CreateClient("name")` は **“名前で構成を切り替える差し替え点”** を提供する🧩
* 呼び出し側は「ハンドラ構成・プール・DNS更新」みたいな複雑さを抱えずに済む🙈✨

```csharp
using System;
using System.Net.Http;
using Microsoft.Extensions.DependencyInjection;

static ServiceProvider BuildServices()
{
    var services = new ServiceCollection();

    // 名前付きクライアント（差し替え点）🧩
    services.AddHttpClient("github", client =>
    {
        client.BaseAddress = new Uri("https://api.github.com/");
        client.DefaultRequestHeaders.UserAgent.ParseAdd("GofLearningApp/1.0");
    });

    return services.BuildServiceProvider();
}

static async Task<string> FetchRootAsync(IServiceProvider sp)
{
    var factory = sp.GetRequiredService<IHttpClientFactory>();
    HttpClient client = factory.CreateClient("github"); // ← Factory Method

    // 必要な範囲で普通に使うだけでOK🙂
    return await client.GetStringAsync("");
}
```

✅ **呼び出し側が知らなくてよい情報（例）**

* `HttpMessageHandler` のパイプライン構成
* 接続の再利用・寿命管理（細かい運用）
* クライアント構成（名前で切り替え）

⚠️ **読み落としがち**

* `HttpClient` の使い捨て/使い回しの流儀は、DI前提で整理される（だからFactoryが便利）🧠
* 例外（通信失敗）をどう扱うかは呼び出し側の責務：リトライ等は別章で扱うとスッキリ🔁

---

## よくある落とし穴 ⚠️😵

* **「Createがある＝全部Factory Method！」と思い込む**

  * 大事なのは“隠してるもの”があるかどうか🙈
* **戻り型が具体型だと効果が薄い**

  * `StreamWriter` を `TextWriter` として受ける、みたいな「抽象寄せ」が効く✨
* **`Dispose` を見落としてバグる**

  * 暗号/Stream/Writer は `using` 基本！🧤
* **“読むだけ”で終わる**

  * 1回は「差し替え」までやって体験しないと、刺さらない💦

---

## 演習 🧪💗（10〜30分×2本）

### 演習A：Factory Method “読解メモ”を作る📝✨

次の3つについて、テンプレでメモしてみよう😊

* `SHA256.Create()`
* `File.CreateText(path)`
* `IHttpClientFactory.CreateClient(name)`

メモ項目（コピペして使ってOK💕）

* 生成メソッド名：
* 戻り型（抽象？）：
* 隠してるもの（3つ）：
* 差し替え点（どこで変わる？）：
* 契約（例外/Dispose）：

### 演習B：`TextWriter` 差し替えテストを1本書く🧪🌸

「ファイルに書く処理」を、テストでは `StringWriter` に差し替えて検証するよ✨
（`WriteOrderSummary` を使う）

```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.IO;

[TestClass]
public class OrderSummaryTests
{
    [TestMethod]
    public void WriteOrderSummary_WritesExpectedLines()
    {
        using var sw = new StringWriter();

        // Act
        WriteOrderSummary(sw, orderId: 1001, total: 2980m);
        var text = sw.ToString();

        // Assert
        StringAssert.Contains(text, "OrderId: 1001");
        StringAssert.Contains(text, "Total: 2980.00");
    }

    // テスト内に置いてOK（学習用の最小）🙂
    private static void WriteOrderSummary(TextWriter writer, int orderId, decimal total)
    {
        writer.WriteLine($"OrderId: {orderId}");
        writer.WriteLine($"Total: {total:0.00}");
    }
}
```

---

## チェック ✅🌟

* `Create()` を見たとき、「何が隠れてるか」を3つ言える？🙈
* 「戻り型が抽象寄り」だと何が嬉しい？（差し替え/テスト/依存）を説明できる？🧩
* `IDisposable` を見抜いて `using` できた？🧤♻️
* `TextWriter` に寄せると、テストがラクになるのを体感できた？🧪💕
