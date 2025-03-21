# start project with python mcp server uv

## 创建python mcp服务
```shell
mkdir python-mcp-server
cd python-mcp-server
uv venv
source .venv/bin/activate
uv init
```
## 添加依赖包
```shell
uv add "mcp[cli]" httpx  -i https://pypi.tuna.tsinghua.edu.cn/simple
```
## 创建function tool 逻辑
```shell
from mcp.server.fastmcp import FastMCP
# Initialize FastMCP server
mcp = FastMCP("YOUR-APP-NAME", log_level="DEBUG")
@mcp.tool()
async def get_alerts(state: str) -> str:

    ##todo

    return "\n-todo-\n"

```
## 本地验证调试工具
```shell
mcp dev weather.py 
```
### 浏览器打开调试工具 http://localhost:5173/#tools

查看所有对ai暴露的方法
提供参数， run tool 测试
  
## 将工具添加到cursor

```shell
## add scripts to cursor/ run code in wsl

{
    "mcpServers": {
        "weather": {
            "command": "wsl.exe",
            "args": [
				"/home/renky/.local/bin/uv",
				"--directory",
				"/mnt/c/workspaces/MCPCommand/python-mcp-server",
				"run",
				"weather.py"
			]
        },
		"fruitprice": {
			"command": "wsl.exe",
			"args": [
				"/home/renky/.local/bin/uv",
				"--directory",
				"/mnt/c/workspaces/MCPCommand/python-mcp-server",
				"run",
				"fruit_price_server.py"
			]
		}
    }
}

```
