#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { PrometheusClient } from "./prometheus.js";
import { loadConfig } from "./config.js";
import 'dotenv/config';

async function createServer() {
  try {
    console.error("Starting server initialization...");
    
    // Create an MCP server instance
    const server = new McpServer({
      name: "prometheus-mcp",
      version: "1.0.0"
    });

    console.error("Loading configuration...");
    const config = loadConfig();
    console.error("Configuration loaded:", config);

    console.error("Creating Prometheus client...");
    const client = new PrometheusClient(config);
    console.error("Prometheus client created successfully");

    // Register the prometheus query tool
    server.tool(
      "prometheus_query",
      "Execute PromQL queries against Prometheus",
      {
        query: z.string(),
        type: z.enum(["instant", "range"]),
        start: z.string().optional(),
        end: z.string().optional(),
        step: z.string().optional()
      },
      async (params) => {
        try {
          const result = await client.query(params);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        } catch (error) {
          console.error('Query error details:', error);
          throw error;
        }
      }
    );

    return server;
  } catch (error) {
    console.error("Server initialization failed:", error);
    throw error;
  }
}

// Start the server using stdio transport
async function main() {
  try {
    const server = await createServer();
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Prometheus MCP Server running on stdio");
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});