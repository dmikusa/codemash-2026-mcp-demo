# CodeMash 2026 MCP Demo

A demo MCP server using FastMCP for CodeMash 2026.

This demo MCP server serves up data about the CodeMash 2026 Conference so that this data can be made available through MCP to various clients (i.e. Claude, ChatGPT, etc...).

## Prerequisites

The project requires a couple of dependencies.

1. Run `brew install uv just watchexec` (or similar for your OS of choice).

  - `just` is a command runner, like `make` but simpler. Install it with `brew install just`.
  - `uv` is the Python package manager we're using. It is similar to `npm` or `gradle`.
  - `watchexec` is only used when running tests in a loop. It will restart the tests.

    Just and watchexec are technically optional, but it helps make things easier.

2. Install Python run `uv python install`.

3. Run `uv sync --frozen` to install dependencies & dev tools. You should also run `uv sync --sync` after pulling updates on the repo as that will make sure your local dependencies are up-to-date with any changes.

## Usage

### Running Locally

You can run this demo locally. Run `just run`. It'll start up the MCP server. It'll be accessible at [http://localhost:8000/mcp](http://localhost:8000/mcp).

### Hosted Version

For the CodeMash 2026 conference, I'm hosting this at [https://cm2026.mikusa.com/mcp](https://cm2026.mikusa.com/mcp).

## Integrations / Client Help

Using an MCP server can be a little tricky, so here is some help to get you started.

### Testing / Debugging

You can easily test or debug an MCP server by running `npx @modelcontextprotocol/inspector`. This will start a web UI on your machine which can connect to any MCP server and interact with the server.

### Claude

If your account has enough access/if you've paid enough, you can register a remote MCP server. Simply register the URL above, and it'll connect. There is no auth required, so all you need to enter is the MCP URL.

You will need to use the version I'm hosting or you will need to be running the software on a publically available URL. If you're running it locally, something like a CloudFlare Tunnel or ngrok works well for that.

See [this article](https://support.claude.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers) for more details.

### Claude Desktop

If you do not have enough access/if you've not paid enough, you can use Claude Desktop and register a local MCP server that proxies to the remote one. See [mcp-remote](https://github.com/geelen/mcp-remote).

Ex:

```
{
  "mcpServers": {
    "cm2026": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://cm2026.mikusa.com/mcp"
      ]
    }
  }
}
```

### ChatGPT

Again, if you have enough access you can connect a remote MCP server to your ChatGPT account. There is a lot of misleading information about this because ChatGPT only fully started supporting MCP very recently. I [believe this is accurate](https://www.stephenwthomas.com/azure-integration-thoughts/how-to-enable-remote-mcp-servers-in-chatgpt-step-by-step-tutorial/). If you have administrative access, you can also register one for your entire organization, and that does not need to be done through Developer Mode.

### Jan.ai

If you're looking to run your LLM locally, [jan.ai](https://www.jan.ai/) works well. It has both local and remote MCP support, both of which will work with this MCP server.

### Others

MCP is a standard protocol, so other clients should work just fine as well. Again, there's no auth required for this so in most cases, you just need to point it to the hosted URL above and it should just work. You can also run them locally and point them at the local URL.
