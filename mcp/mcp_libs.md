了解です。Python SDK（例：fastMCP）およびTypeScript向けのMCPライブラリとその使い方について、可能な限り多様な実装やツールを調査します。

PythonおよびTypeScript環境におけるMCPクライアント／サーバの構築法、SDKのインストール、コード例、対応プロトコルなどを含めた技術的なガイドとしてまとめてお届けします。しばらくお待ちください。

# MCP（Model Context Protocol）実装とSDK活用ガイド

MCP（Model Context Protocol）は、Anthropic社によって提唱された**LLM向けのオープン標準プロトコル**です ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=The%20Model%20Context%20Protocol%20,tools%2C%20data%20sources%2C%20and%20systems))。複数のAIアプリケーション（チャットボット、IDEアシスタント、エージェントなど）と多様な外部ツール・データソースを接続する際の統合的な仕組みを提供します。例えば**「AI統合のためのUSB」**になぞらえられるように、MCP登場以前は各AIごと・各ツールごとにカスタム連携が必要だったものが、MCPにより共通インターフェースで接続可能になります ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=Think%20of%20it%20like%20USB,effort%20across%20teams%2C%20inconsistent%20implementations))。MCPはクライアント-サーバモデルを採用し、LLM側（ホストアプリ）にはMCPクライアント、外部ツール側にはMCPサーバを配置します。それによって**LLMから外部機能を安全・標準化された方法で利用**できるようになります。

## MCPの基本概念: Tools・Resources・Prompts

 ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction))MCPでは、サーバ側がLLMに対して**Tools（ツール）**・**Resources（リソース）**・**Prompts（プロンプト）**の3種類のエンドポイントを公開します ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=The%20current%20components%20of%20MCP,servers%20include))。図に示すように、**Tools**はLLM（モデル）が呼び出す関数的な操作（モデル制御で実行される動作）で、たとえばデータベース更新やAPIコールなど**外部アクション**を実行します。一方**Resources**はホストアプリ（ユーザーアプリ側）が提供する**データ参照**用エンドポイントで、ファイル内容やデータベースレコードなど静的/動的データをLLMが読み取るために使います（REST APIで言うGETに相当し、副作用を伴わない） ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=1.%20Tools%20%28Model,Selected%20before%20running%20inference))。そして**Prompts**はユーザーが管理する**テンプレート**で、LLMとサーバの対話パターンを定義します。たとえばドキュメントQ&A用の質問テンプレートや、コードレビュー要求の定型文など、LLMへの指示文を事前定義して再利用できます。

MCPクライアント（LLM側）はこれら**Tools**を呼び出し、**Resources**を要求し、**Prompts**をLLM入力に差し込むことで、動的にコンテキストや機能を取り込めます ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=MCP%20aims%20to%20simplify%20this,server%20architecture%20where))。MCPによりアプリ開発者はLLMと外部リソースの連携部分を共通化でき、**モジュール性・セキュリティ・再利用性**が向上します ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=1,saving%20you%20time%20and%20effort)) ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=For%20TypeScript%20developers%2C%20MCP%E2%80%99s%20type,backend%2C%20and%20AI%20layer%20effortlessly))。

以下では、PythonおよびTypeScript/JavaScript環境でMCPサーバ・クライアントを実装し活用するための主要なSDKやライブラリを紹介します。各ライブラリのインストール方法や基本的な使い方（コード例）、対応する通信方式、ツール/リソース/プロンプト定義方法、および開発元・メンテナンス状況についてまとめます。

## Python向けMCP実装ライブラリ

### FastMCP（公式Python SDK）

**FastMCP**はモデルコンテキストプロトコルの**公式Python SDK**であり、MCPサーバおよびクライアントを**シンプルかつPythonic**に実装できるライブラリです ([FastMCP: Simplifying AI Context Management with the Model Context Protocol - DEV Community](https://dev.to/mayankcse/fastmcp-simplifying-ai-context-management-with-the-model-context-protocol-37l9#:~:text=FastMCP%20is%20a%20Python%20SDK,specification%2C%20making%20it%20easier%20to))。FastMCPという名称が示す通り、FastAPIライクな直感的インターフェースでMCPの全機能を利用できます。Apache-2.0ライセンスで公開されており、2025年4月時点の最新版はv2.2.0（メンテナ: Jeremiah Lowin）です ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=fastmcp%202)) ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=SPDX%20License%20Expression%20,Requires%3A%20Python%20%3E%3D3.10))。Anthropic社の提唱後、VMwareのSpring AIチームなどコミュニティによって開発が進められており、MCP標準化団体の公式リポジトリ（modelcontextprotocol/python-sdk）で積極的にメンテナンスされています ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=,them%20to%20the%20MCP%20community)) ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=SDK%20and%20Server%20Improvements))。

**インストール方法:** FastMCPはPyPIからインストール可能です。通常のpip環境では以下のようにインストールします（Python 3.10+が必要）:

```bash
pip install fastmcp
```

または推奨される開発ワークフロー管理ツール**Astral UV**を利用して`uv add "fastmcp"`とする方法もあります ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=fastmcp%202)) ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=uv%20pip%20install%20fastmcp))。インストールにより、ライブラリ本体と開発用CLIコマンドが導入されます。

**基本的な使い方（サーバ実装）:** FastMCPを使って**MCPサーバ**を構築するのは非常に簡単です。以下に「Demo」という名前のMCPサーバを作成し、足し算を行うツール`add`を提供する最小例を示します ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=,FastMCP)):

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
``` ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=,FastMCP))

上記では`FastMCP("Demo")`でサーバインスタンスを生成し、`@mcp.tool()`デコレータで関数をツールとして登録しています。関数のdocstringやシグネチャから、MCPクライアントに伝えるツールの説明やパラメータ型が自動取得されます。**Resources**（リソース）を公開する場合は`@mcp.resource("<スキーマ>")`デコレータを使用し、例えば動的リソースなら `@mcp.resource("greeting://{name}")` のようにURIパターンを指定して関数を登録します ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=,Hello%2C%20%7Bname))。**Prompts**（プロンプト）も`@mcp.prompt()`デコレータで関数を登録し、関数内で定型の指示メッセージ（文字列やMessageオブジェクトのリスト）を返すことで定義できます ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=%40mcp.prompt%28%29%20def%20debug_error%28error%3A%20str%29%20,I%27m%20seeing%20this%20error))。

**サーバの起動とCLIツール:** FastMCPインストール後は、`fastmcp`というコマンドラインツールが利用できます。このCLIからサーバスクリプトを起動したり、開発モードでデバッグしたりできます。例えば上記の`server.py`を起動するには以下のように実行します:

```bash
fastmcp run server.py
``` ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=Run%20the%20server%20locally%3A))

このコマンドにより`server.py`内のFastMCPサーバが起動し、デフォルトでは**標準入出力（STDIO）**を介してホストと接続待機します。Claude DesktopなどMCP対応クライアントはこのサーバプロセスをサブプロセスとして起動し、STDIN/STDOUTでプロトコルメッセージをやり取りすることで連携します ([FastMCP: Simplifying AI Context Management with the Model Context Protocol - DEV Community](https://dev.to/mayankcse/fastmcp-simplifying-ai-context-management-with-the-model-context-protocol-37l9#:~:text=,sources%20accessible%20over%20the%20internet))。開発時には`fastmcp dev server.py`と実行することで、MCP Inspector（後述）というWebベースのデバッグUIを立ち上げつつサーバを起動できます。さらにFastMCPは、他の用途向けに`fastmcp install`（Claude Desktopへの組み込み用）や`fastmcp version`（バージョン確認）等のサブコマンドも提供します ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=uv%20pip%20install%20fastmcp))。

FastMCPライブラリ自体をコードから用いて**MCPクライアント**を実装することも可能です。例えば、FastMCPの`Client`クラスや各種トランスポートを使えば、Pythonアプリケーションから任意のMCPサーバに接続しツール呼び出しを行えます。FastMCP v2ではMCPクライアント向けにLLMのFunction Callingやストリーミング結果取得を簡単に扱う機能も統合されました ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=,Composing%20MCP%20Servers))。

**備考（高度な機能）:** FastMCPは単なるプロトコル実装に留まらず、便利な機能が多数用意されています。例えばFastMCPサーバから**OpenAPIドキュメントやFastAPIアプリを自動生成**する機能、複数のMCPサーバを**プロキシ経由で合成**する機能などが提供されています ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=,For%20Advanced%20Use%20Cases))。また、`FastMCP`オブジェクトには`dependencies=[...]`引数でpipパッケージ依存関係を指定でき、Claude Desktopにサーバをインストールする際に自動で環境構築する仕組みもあります ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=,numpy))。開発の活発さもあり、バージョン1系から2系で大きくAPIが改善されました（v2ではより高水準なFastMCP APIが導入されました ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=SDK%20and%20Server%20Improvements))）。

### CHUK-MCP（Python用クライアント実装ライブラリ）

**CHUK-MCP**はMCPプロトコルの**低レベルPythonクライアント実装**です ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=A%20Python%20client%20implementation%20for,MCP)) ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=This%20client%20implementation%20provides%20a,to%20interact%20with%20MCP%20servers))。オープンソース開発者のChris Hay氏（GitHub: chrishayuk）によってMITライセンスで公開されており、pipで`chuk-mcp`としてインストールできます ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=Installation))。FastMCPがMCPサーバを手軽に構築するための高水準SDKであるのに対し、CHUK-MCPはMCP通信を細かく扱うための**軽量クライアントライブラリ**として位置付けられます。

CHUK-MCPを使うと、自前のPythonコードから任意のMCPサーバに接続してメッセージの送受信やツール呼び出しを行えます。例えば、以下のようにサーバプロセス（コマンドと引数）を指定してSTDIO経由のクライアントを起動し、MCPハンドシェイクとpingを送ることができます ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=async%20def%20main%28%29%3A%20,option%22%2C%20%22value%22%5D%2C)) ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=return)):

```python
import anyio
from chuk_mcp.mcp_client.transport.stdio import stdio_client, StdioServerParameters
from chuk_mcp.mcp_client.messages.initialize import send_initialize
from chuk_mcp.mcp_client.messages.ping import send_ping

async def main():
    server_params = StdioServerParameters(command="path/to/mcp/server", args=["--option", "value"])
    async with stdio_client(server_params) as (read_stream, write_stream):
        init_result = await send_initialize(read_stream, write_stream)
        if not init_result:
            print("Server initialization failed")
            return
        ping_ok = await send_ping(read_stream, write_stream)
        print("Ping successful" if ping_ok else "Ping failed")

anyio.run(main)
``` ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=async%20def%20main%28%29%3A%20,option%22%2C%20%22value%22%5D%2C)) ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=return))

上記のようにCHUK-MCPは非同期IOライブラリ(anyio)上で動作し、`send_initialize`や`send_ping`といった関数でMCPプロトコルメッセージを直接送信します。またツールやリソースを使うAPIも用意されており、例えば接続後に`send_tools_list`で利用可能ツール一覧を取得し、`send_tools_call(name="ツール名", arguments={...})`でツールを呼び出すことができます ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=,%7Btool%5B%27description)) ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=,result))。以下は登録されている`get_weather`というツールを呼び出す例です:

```python
tools_response = await send_tools_list(read_stream, write_stream)
for tool in tools_response.get("tools", []):
    print(f"Available tool: {tool['name']} - {tool['description']}")
result = await send_tools_call(read_stream, write_stream, name="get_weather", arguments={"location": "San Francisco"})
print("Tool result:", result)
``` ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=,%7Btool%5B%27description)) ([GitHub - chrishayuk/chuk-mcp](https://github.com/chrishayuk/chuk-mcp#:~:text=,result))

CHUK-MCPはこのように**コードから直接MCP通信を扱いたい場合に適した低レベルAPI**を提供します。FastMCPに比べ開発者数は少ないものの、GitHub上で継続的にアップデート（v0.1系）されており、作者による関連プロジェクト（対話型CLIツールの**mcp-cli**や、現在時刻を提供する**chuk-mcp-time-server**など ([chuk-mcp-time-server 0.1.10 on PyPI - Libraries.io](https://libraries.io/pypi/chuk-mcp-time-server#:~:text=chuk,5%3B%20Dependent%20packages%3A%200))）も存在します。例えばmcp-cliはCHUK-MCPを利用した対話シェルで、対話形式でMCPツールを実行したりコンテキスト管理を行えるCLIアプリです ([GitHub - chrishayuk/mcp-cli](https://github.com/chrishayuk/mcp-cli#:~:text=%23%20Generate%20summary%20mcp,output%20%22%24%7Bfile%25.md%7D.summary.md)) ([GitHub - chrishayuk/mcp-cli](https://github.com/chrishayuk/mcp-cli#:~:text=,core%20dependency))。

### その他のPython関連ツール

上記以外にも、MCPエコシステムに関連したPythonツールがいくつか存在します。たとえば**MCP Builder**は特殊なMCPサーバ実装で、**他のMCPサーバをインストール・設定するための補助サーバ**です ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=mcp)) ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=Features))。MCP BuilderをClaude Desktop等に組み込むと、LLMに「〇〇というMCPサーバをインストールして」と命令することで、裏でpipやnpmからパッケージを取得して設定ファイルを更新するといった自動操作を行えます ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=)) ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=Once%20integrated%20with%20Claude%20Desktop%2C,you%20can%20ask%20Claude%20to))。このように、MCPそのものを支援するメタツールもコミュニティから提供されています。

また、既成のMCPサーバ実装もPyPI上で共有されています。例えば**DuckDuckGo-MCP-Server**（Python製、DuckDuckGo検索を行うツールを提供）や**BlenderMCP**（Blender操作用のMCPサーバ）など、特定の機能に特化したサーバが有志により公開されています ([DuckDuckGo Search MCP Server](https://mcp.so/en/server/nickclyde_duckduckgo-mcp-server/MCP-Mirror#:~:text=DuckDuckGo%20Search%20MCP%20Server%20,through%20the%20Model%20Context)) ([DuckDuckGo Search MCP Server | MCP Server | McpHubs | McpHubs](https://www.mcphubs.ai/servers/nickclyde#:~:text=DuckDuckGo%20Search%20MCP%20Server%20,by%20editing%20the%20configuration))。これらは`pip install duckduckgo-mcp-server`のようにインストールしてClaude Desktopに登録するだけで利用可能です。必要な機能に近いサーバが既に公開されていないか探してみるのも良いでしょう。

## TypeScript/JavaScript向けMCP実装ライブラリ

### 公式TypeScript SDK（@modelcontextprotocol/sdk）

Anthropicらの提唱するMCPは言語非依存のオープン仕様であり、JavaやKotlin、C#版SDKも登場していますが ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Java%20SDK%20released)) ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=C))、ここではフロントエンド/バックエンド開発者に馴染み深い**TypeScript公式SDK**を紹介します。公式の**MCP TypeScript SDK**はnpmパッケージ`@modelcontextprotocol/sdk`として提供されており、サーバ・クライアント両機能の実装が可能です ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=The%20Model%20Context%20Protocol%20allows,specification%2C%20making%20it%20easy%20to))。Apache-2.0ライセンスで公開され、2025年2月にv1.7.0がリリースされるなど継続的にアップデートされています ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Typescript%20SDK%20release))。このSDKにより、Node.jsやブラウザ環境で標準的なMCP通信を扱うことができます。

**インストール方法:** npmまたはyarnでパッケージを追加するだけです:

```bash
npm install @modelcontextprotocol/sdk
``` ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=Ready%20to%20give%20it%20a,start%20building%20smarter%20apps%20today))

インストール後、SDK内のモジュールをインポートして利用できます。TypeScript用に型定義も含まれているため、エディタの補完や型チェックが活用できます。

**基本的な使い方（サーバ実装）:** MCP TypeScript SDKを用いてMCPサーバを構築する場合、`McpServer`クラスを使います。以下はPythonの例と同様、足し算ツール`add`と動的挨拶リソース`greeting://{name}`を公開するシンプルなサーバ実装例です。

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// MCPサーバの作成
const server = new McpServer({ name: "Demo", version: "1.0.0" });

// ツールの登録（addツール: 2数の和を返す）
server.tool(
  "add",
  { a: z.number(), b: z.number() },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }]
  })
);

// リソースの登録（greetingリソース: 名前に応じた挨拶文を返す）
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [{ uri: uri.href, text: `Hello, ${name}!` }]
  })
);

// 標準入出力で待ち受け開始
const transport = new StdioServerTransport();
await server.connect(transport);
``` ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Create%20an%20MCP%20server,)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Add%20a%20dynamic%20greeting,name%7D%21%60%20%7D%5D)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Start%20receiving%20messages%20on,connect%28transport))

上記コードでは、まず`McpServer`を生成し（サーバ名とバージョンを指定可能）、`server.tool(名前, 引数スキーマ, 実装関数)`でツール、`server.resource("ラベル", ResourceTemplate(URI), 実装関数)`でリソースを登録しています。TypeScript SDKでは**パラメータのバリデーション**に[zod](https://github.com/colinhacks/zod)を活用している点が特徴です。例では`{ a: z.number(), b: z.number() }`のようにツール引数を定義しておくことで、不正な型の入力が来た場合に自動的にエラー応答を返します ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Add%20an%20addition%20tool,))。Prompts（プロンプト）についても`server.prompt(name, schema, 実装)`メソッドで定義可能で、コールバック関数内で`{ messages: [...]{...} }`の形でテンプレートメッセージを返すことで設定できます ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=server.prompt%28%20%22review,code%7D%60%20%7D%2C%20%7D%5D%2C))。

**通信方式（トランスポート）の選択:** 上記例では`StdioServerTransport`を用いて標準入出力経由で接続待機しています ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=import%20,zod)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Start%20receiving%20messages%20on,connect%28transport))。これは主にローカルでホストアプリ（例: Claude Desktop）がサーバを子プロセスとして実行するケースを想定したトランスポートです。SDKには他にも**HTTPストリーミング用トランスポート**が用意されています。典型的なのは**SSE（Server-Sent Events）**を用いたトランスポートで、`SSEServerTransport`クラスを利用します。例えばExpress.jsサーバ内でエンドポイント`/sse`に対し以下のように組み込むことで、HTTP経由のMCP通信を処理できます ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=const%20transport%20%3D%20new%20StdioServerTransport,connect%28transport)) ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=app.get%28,app.listen%283001)):

```typescript
import express from "express";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const app = express();
app.get("/sse", async (req, res) => {
  const transport = new SSEServerTransport("/messages", res);
  await server.connect(transport);
});
app.listen(3001);
``` ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=const%20transport%20%3D%20new%20StdioServerTransport,connect%28transport)) ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=app.get%28,app.listen%283001))

上記では、クライアント（LLMホスト側）が`GET /sse`で接続してきた際に`SSEServerTransport`を生成し、サーバと接続しています。このようにするとHTTPレスポンスをサーバから逐次送信（サーバ送信イベント）する形でMCPメッセージをクライアントに届けます。TypeScript SDKでは**ストリーム可能HTTP（Streamable HTTP）**方式にも対応しており、SSEを使わずともチャットのような双方向ストリーミングを実現できます。実際、プロトコル仕様は2024年末に改定され、**従来のHTTP+SSE方式は将来的に非推奨**となり、新たな「ストリーム可能HTTP」1本に統一されつつあります ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=Note%3A%20The%20SSE%20transport%20is,implementations%20should%20plan%20to%20migrate))。SDK内部では後方互換のため`SSEServerTransport`（レガシー）と`StreamableHTTPServerTransport`（新方式）が実装されており、上記Express統合例でも`/sse`を従来用、`/mcp`など別エンドポイントを新方式用に使い分けることが可能です ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Modern%20Streamable%20HTTP%20endpoint)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Legacy%20SSE%20endpoint%20for,messages%27%2C%20res))。したがって、新規開発では可能であれば**Streamable HTTP**での実装が推奨されます。

**クライアント実装:** TypeScript SDKはクライアント側ライブラリとしても利用できます。ブラウザまたはNode.js上で`Client`クラスと各種`...ClientTransport`を使えば、任意のMCPサーバに接続可能です ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=import%20,StreamableHTTPClientTransport%20%7D%20from)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=transport))。例えば、`Client`を作成し`client.connect(new SSEClientTransport(serverUrl))`とすればサーバからResource一覧やTool実行を呼び出せます。もっとも一般的なクライアントはAnthropicのClaudeなどホストアプリ自身なので、開発者が直接TS SDKでクライアントを書く場面は多くありませんが、テストやカスタム統合では活用できます。

**メンテナンス状況:** MCP TypeScript SDKは公式のGitHubリポジトリ（modelcontextprotocol/typescript-sdk）で開発されています。Spring AIチームなどが中心となり頻繁に改良が加えられており、2025年現在バージョン1系後半がリリースされています ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Typescript%20SDK%20release))。TypeScriptということで、他のNodeエコシステムとの親和性も高く、たとえば前述のMCP Builderは`npx @modelcontextprotocol/inspector`でこのSDKを利用した検証UIを起動する機能を提供しています ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=,m%20mcp_builder.server)) ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=mcp%20dev%20path%2Fto%2Fmcp_builder%2Fserver))。SDK自体の信頼性も向上しており、各種例外ハンドリングや型定義が充実しています。

### Node.js製のMCPサーバ実装例：MCP NPX Fetch

公式SDKを利用すればTypeScript/JavaScriptで自由にMCPサーバを開発できますが、コミュニティによって既成のサーバもNPMパッケージとして提供されています。その一つが**MCP NPX Fetch**です。これは**ウェブの情報取得に特化したMCPサーバ実装**で、指定URLのHTML/JSON/Markdownなどを取得して返す一連のツール（`fetch_html`・`fetch_json`・`fetch_markdown`等）を提供します ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=Protocol%20github)) ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=Features))。Tokenizin AgencyによってMITライセンスで開発されており、内部的には前述の公式SDKを用いて実装されています ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=Technical%20Stack))。

**インストール・起動:** グローバルにインストールしてコマンドとして使うか、その場でnpx実行できます。

- グローバルインストール: `npm install -g @tokenizin/mcp-npx-fetch`  
- npxで一時実行: `npx @tokenizin/mcp-npx-fetch`

実行すると`fetch_html`等のツールを持つMCPサーバが起動し、デフォルトではSTDIOで待ち受けます ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=CLI%20Usage))。Claude Desktopに組み込む場合は、設定ファイルの`mcpServers`に`"command": "npx", "args": ["-y", "@tokenizin/mcp-npx-fetch"]`と追記することで、プロンプトからウェブ取得を行うよう指示できます ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=%7B%20,fetch%22%5D%2C%20%22env%22%3A%20%7B%7D%20%7D))。

**機能:** MCP NPX Fetchは**HTTPリクエストの発行と結果変換**を行うツール群を実装しています。たとえば`fetch_html`ツールは指定URLからHTML文字列を取得し、`fetch_json`はJSONをパースして返します ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=Available%20Tools)) ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=))。OpenAIプラグイン的なWebブラウザ機能をClaude等で実現する目的で利用可能です。加えて、カスタムHTTPヘッダの指定や、取得内容のMarkdown変換（内部でjsdomやTurndownライブラリを使用）などもサポートしており ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=,Desktop%20and%20other%20MCP%20clients)) ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=A%20powerful%20MCP%20server%20for,with%20ease))、実用的なWebアクセス手段となっています。

**メンテナンス状況:** MCP NPX Fetchは2024年末頃に公開され、数十件のコミットを経て安定版v1.0.0がリリースされています ([Tokenizin - NPM](https://www.npmjs.com/~tokenizin-com#:~:text=Tokenizin%20,%E2%80%A2%204%20months%20agopublished))。開発元のTokenizin Agencyによる継続的なメンテナンスが行われており、Claude Desktopや他のMCPクライアントとの互換性も確認されています ([GitHub - tokenizin-agency/mcp-npx-fetch: A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.](https://github.com/tokenizin-agency/mcp-npx-fetch#:~:text=,Desktop%20and%20other%20MCP%20clients))。

なお、Node.js関連では他にも**MCP Inspector**という公式ツールが存在します。これは`npx @modelcontextprotocol/inspector`で起動できる開発支援用の**Web UIクライアント**で、ローカルのMCPサーバをWebブラウザ上で手軽にテストできます ([GitHub - XD3an/mcp-builder: A Python-based MCP server to install other MCP servers.](https://github.com/XD3an/mcp-builder#:~:text=mcp%20dev%20path%2Fto%2Fmcp_builder%2Fserver))。サーバのリソースやツール一覧を閲覧したり、実際にツールを呼び出して結果を見ることが可能で、デバッグ用途に非常に便利です。

## MCP通信方式と実装例

MCPで使用される通信方式（トランスポート）は、**標準入出力（STDIO）**と**HTTPストリーミング**の2種類が主流です。各SDKはこれらを抽象化した**Transport**クラスを提供しており、サーバ側実装では用途に応じて選択します。

- **STDIO**: 標準入出力を通じた双方向通信。ローカルでLLMホストがサーバプロセスを起動する場合によく使われます。Python SDKでは`mcp.run()`実行時にデフォルトでSTDIO待ち受けを開始し、TS SDKでは`StdioServerTransport`を用いて`server.connect()`することで有効になります ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=import%20,zod)) ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Start%20receiving%20messages%20on,connect%28transport))。STDIO方式はシンプルでファイアウォールなどの影響も受けないため、**デスクトップアプリ（例: Claude Desktop）やIDE拡張**との連携に適しています。

- **HTTPストリーミング**: ネットワーク経由で通信する方式で、プロトコルメッセージをHTTPレスポンスとして逐次送る形態です。従来は**Server-Sent Events (SSE)**を用いるのが一般的で、TS SDKの`SSEServerTransport`やPython SDKの`mcp.sse_app()`で実装できます（PythonではStarlette/FastAPI等に組み込む形 ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=You%20can%20mount%20the%20SSE,server%20with%20other%20ASGI%20applications))）。SSEではサーバ→クライアント方向のストリーミングが可能で、クライアントからのリクエストは通常HTTP POST等で行います。一方、**Streamable HTTP**と呼ばれる新方式では、単一のHTTP接続上で双方向のメッセージ交換を行うようプロトコルが拡張されました ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=const%20transport%20%3D%20transports.sse,else))。TS SDKでは`StreamableHTTPServerTransport`が提供されており、Express.jsで`app.get("/mcp", handleSessionRequest)`のようにハンドラを設定することで、SSEを使わないストリーミング通信を実現します ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Modern%20Streamable%20HTTP%20endpoint))。この方式ではサーバ側はチャットの応答をチャンク送信し、クライアント側はEventStreamではなく通常のHTTPストリームとして受信します。**現在はSSEと並行してサポートされていますが、将来的にはStreamable HTTPへの一本化が予定**されています ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=Note%3A%20The%20SSE%20transport%20is,implementations%20should%20plan%20to%20migrate))。

- **その他の方式**: MCP仕様上は上記2系統が中心ですが、理論上はWebSocketなど他の全二重通信も実装可能です（実際、MCPクライアントとサーバの間でJSON-RPCメッセージをやり取りできれば手段は問いません）。しかし既存SDKやホストアプリが公式にサポートしているのはSTDIOとHTTP系（SSE/Streamable HTTP）のみです。なお、Anthropic Claudeの場合はクラウド上ではなくローカル実行のClaude Desktopを介してのみMCPサーバと通信でき（2025年4月時点）、OpenAI ChatGPTなど他社LLMは現状MCP非対応ですが、コミュニティが独自クライアントを実装する動きはあります。

## ツール・リソース・プロンプト定義方法のまとめ

各SDKにおける**Tools/Resources/Promptsの定義**方法を整理します。

- **Python (FastMCP)**: デコレータを用いた宣言的アプローチ。`@mcp.tool()`を付与した関数はツールとして登録され、関数名がツール名、docstringが説明文、引数名・型アノテーションがパラメータ定義として自動認識されます。戻り値はツール呼び出しの結果となり、その型も自動的にJSONシリアライズされLLMに返されます。`@mcp.resource("schema")`を使えばリソースURIと紐付けられ、URIパラメータも関数引数経由で受け取れます ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=,Hello%2C%20%7Bname))。`@mcp.prompt()`ではプロンプト名は自動生成（関数名ベース）され、返り値は文字列またはメッセージオブジェクトのリストでテンプレート内容を表現します ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=%40mcp.prompt%28%29%20def%20review_code%28code%3A%20str%29%20,Please%20review%20this%20code%3A%5Cn%5Cn%7Bcode))。Pythonの場合、型チェックやスキーマ定義は基本的にPythonの型ヒント任せですが、必要なら関数内で明示的なバリデーションも可能です。

- **TypeScript (公式SDK)**: メソッド呼び出しによる定義。`server.tool(name, schema, handler)`のように名前を文字列で指定し、パラメータスキーマはzodスキーマで明示、ハンドラ関数では引数をオブジェクトで受け取り処理を実装します ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=%2F%2F%20Add%20an%20addition%20tool,))。ツール結果は`{ content: [ {type: "text", text: "..."} ] }`等の**Contentオブジェクト**で返します（MCPプロトコルではレスポンスをテキスト・画像など複数種類のコンテンツで返せるため、SDK側でその形式に沿ったオブジェクトを組み立てます）。`server.resource(label, template, handler)`ではリソースラベルとResourceTemplateを渡し、URI→コンテンツの取得処理を実装します ([GitHub - modelcontextprotocol/typescript-sdk: The official Typescript SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/typescript-sdk#:~:text=server.resource%28%20,name%7D%21%60%20%7D%5D%20%7D%29))。`server.prompt(name, schema, handler)`ではhandler内で`{ messages: [ { role: "...", content: {type: "text", text: "..."} } , ...] }`の形でメッセージ一覧を返します ([What is the Model Context Protocol ? How to Use It with TypeScript ? | Medium](https://medium.com/@halilxibrahim/simplifying-ai-integration-with-mcp-a-guide-for-typescript-developers-c6f2b93c1b56#:~:text=server.prompt%28%20%22review,code%7D%60%20%7D%2C%20%7D%5D%2C))。TypeScriptではコンパイル時に型整合性が検証されるため、安全にプロンプトのパラメータや戻り値を扱えます。また、ツール/リソース/プロンプトごとに`description`や`tags`等メタデータを付与するメソッドもあり、ドキュメント生成やクライアントUI表示に役立てられます。

**定義時の注意点:** MCPのプロトコル仕様上、各ToolやResourceには**ユニークな名前/URI**と**簡潔な説明文**が必要です ([Model Context Protocol (MCP) an overview](https://www.philschmid.de/mcp-introduction#:~:text=which%20exchange%20information%20about%20capabilities,based%20on))。SDKはこの情報をホスト側へ提供する**初期化ハンドシェイク**を自動処理します。したがって、**関数名やdocstringはなるべく分かりやすく記述**することが推奨されます。また、Promptsはユーザーや開発者が選択して使うものなので、想定用途が伝わる名称・内容にするのが望ましいでしょう。

## ライブラリの開発元とメンテナンス状況

最後に、主要なMCP関連ライブラリの開発主体や更新状況をまとめます。以下の表にPython/TypeScriptを中心としたSDK・ツールを示します。

| ライブラリ／ツール名            | 対応言語     | インストール方法                           | 主な用途                  | 開発元・メンテナー                   | 最新版（2025年時点）           |
| ------------------------- | ---------- | ------------------------------------ | ------------------------- | --------------------------------- | ------------------------ |
| **FastMCP** (Python公式SDK) | Python     | `pip install fastmcp`                | MCPサーバ＆クライアント実装、CLI提供 | Model Context Protocol公式（Spring AIチーム等） ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=,them%20to%20the%20MCP%20community)) | v2.2.0 ([fastmcp · PyPI](https://pypi.org/project/fastmcp/#:~:text=fastmcp%202))（活発に開発中） |
| **CHUK-MCP** (Pythonクライアント) | Python     | `pip install chuk-mcp`               | MCPクライアント実装（低レベルAPI）   | Chris Hay (chrishayuk)             | v0.1.x（2024～2025年、開発中）   |
| **MCP CLI** (`mcp-cli`)    | Python     | `pip install mcp-cli[cli]`           | 対話型CLIクライアント、開発用ユーティリティ | Chris Hay (chrishayuk)             | v0.1.0（2024年公開）         |
| **MCP TypeScript SDK** (`@modelcontextprotocol/sdk`) | TypeScript/Node | `npm install @modelcontextprotocol/sdk` | MCPサーバ＆クライアント実装（公式） | Model Context Protocol公式（コミュニティ） ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Java%20SDK%20released)) | v1.7.0 ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Typescript%20SDK%20release))（活発に開発中） |
| **MCP NPX Fetch** (`@tokenizin/mcp-npx-fetch`)     | Node.js     | `npm install -g @tokenizin/mcp-npx-fetch`<br>または`npx @tokenizin/mcp-npx-fetch` | MCPサーバ実装（Web情報取得ツール群） | Tokenizin Agency（OSS）        | v1.0.0（2024年末リリース）      |
| **MCP Inspector**          | Node.js     | `npx @modelcontextprotocol/inspector` | 開発用GUIクライアント（検証・デバッグ） | Model Context Protocol公式        | v1.x（2024年公開）          |

※この他、Java用公式SDK ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=Java%20SDK%20released))やKotlin SDK ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=2024))、Microsoftが貢献したC# SDK ([What's New - Model Context Protocol](https://modelcontextprotocol.io/development/updates#:~:text=2025))なども登場しており、エコシステムが急速に拡大しています。Python・TypeScript以外の言語でもMCPを扱えるようになってきている点は注目に値します。

## おわりに

MCP（Model Context Protocol）は、LLMと外部ツール・データの橋渡しを標準化する**画期的なプロトコル**です。その実装を支えるSDKやライブラリもPythonやTypeScriptをはじめ多数登場しており、開発者は用途に応じて選択できます。PythonのFastMCPを使えば数行のコードで強力なMCPサーバを構築でき、TypeScript SDKを使えばWebアプリケーションとLLMのシームレスな連携が可能です。STDIOやSSE/HTTPといった通信方式の違いもSDKが抽象化してくれるため、複雑なプロトコル処理を意識する必要はほとんどありません ([FastMCP: Simplifying AI Context Management with the Model Context Protocol - DEV Community](https://dev.to/mayankcse/fastmcp-simplifying-ai-context-management-with-the-model-context-protocol-37l9#:~:text=,messages%20and%20lifecycle%20events%20seamlessly))。今後も公式SDKの改良やコミュニティによるツール開発が続いていく見込みであり、MCP対応のエコシステムはさらに充実していくでしょう。ぜひ本ガイドを参考に、適切なライブラリを選んでMCPを活用した**次世代のLLMアプリケーション開発**に挑戦してみてください。

