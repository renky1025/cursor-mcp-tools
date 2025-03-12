# cursor-mcp-tools
develop cursor mcp tools with node + typescripts

# typescript 项目初始化必备 文件
```
./src/index.ts
package.json // 包含了默认mcp依赖包
tsconfig.json
```

# 核心逻辑实现在 index.js, 怎么唤醒cursor使用mcp 
```
server.tool(
  "system_info",
  "获取系统信息",
  {},
```

```
    server.tool(
      "prometheus_query",
      "Execute PromQL queries against Prometheus",
```

# 项目结构
```
# tree /f

│  .gitignore
│  LICENSE
│  README.md
│
├─prometheus-mcp
│  │  .env
│  │  package-lock.json
│  │  package.json
│  │  pnpm-lock.yaml
│  │  tsconfig.json
│  │
│  └─src
│          config.ts
│          index.ts
│          prometheus.ts
│          types.ts
│
└─system-info-mcp
    │  package.json
    │  pnpm-lock.yaml
    │  tsconfig.json
    │
    └─src
            index.ts
```
# 进入目录安装依赖包， build， 加入mcp server
在 Cursor 中重新配置 MCP 服务器，使用以下步骤：
点击 "Add new MCP server"
名字：自定义
选择命令（command）
在命令行中输入：node /xxx/xx.xx/dist/index.js
