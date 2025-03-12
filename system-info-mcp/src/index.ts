#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from 'child_process';
import os from 'os';

// Create an MCP server instance
const server = new McpServer({
  name: "system-info-mcp",
  version: "1.0.0"
});

// 注册系统信息查询工具
server.tool(
  "system_info",
  "获取系统信息",
  {},
  async () => {
    try {
      const systemInfo = {
        platform: os.platform(),
        release: os.release(),
        type: os.type(),
        arch: os.arch(),
        hostname: os.hostname(),
        cpus: os.cpus(),
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime(),
        loadavg: os.loadavg(),
        userInfo: os.userInfo(),
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(systemInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error getting system info:', error);
      throw error;
    }
  }
);

// 注册 CPU 信息查询工具
server.tool(
  "cpu_info",
  "获取 CPU 信息",
  {},
  async () => {
    try {
      const cpus = os.cpus();
      const cpuInfo = {
        count: cpus.length,
        model: cpus[0].model,
        speed: cpus[0].speed,
        times: cpus[0].times,
        loadavg: os.loadavg(),
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(cpuInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error getting CPU info:', error);
      throw error;
    }
  }
);

// 注册内存信息查询工具
server.tool(
  "memory_info",
  "获取内存信息",
  {},
  async () => {
    try {
      const memInfo = {
        total: os.totalmem(),
        free: os.freemem(),
        used: os.totalmem() - os.freemem(),
        usedPercentage: ((os.totalmem() - os.freemem()) / os.totalmem() * 100).toFixed(2)
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(memInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error getting memory info:', error);
      throw error;
    }
  }
);

// Start the server using stdio transport
async function main() {
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("System Info MCP Server running on stdio");
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});