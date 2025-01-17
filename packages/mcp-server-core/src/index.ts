import { Server } from '@modelcontextprotocol/sdk/server';
import { GitIntegration } from './tools/git/integration';
import { ErrorHandler } from './error-handling';

export class MCPServer {
  private server: Server;
  private gitIntegration: GitIntegration;
  private errorHandler: ErrorHandler;

  constructor(private config: { githubToken: string }) {
    this.server = new Server({
      name: "mcp-server",
      version: "0.1.0"
    });
    this.errorHandler = new ErrorHandler();
    this.gitIntegration = new GitIntegration(this.server, config.githubToken);
  }

  async initialize() {
    try {
      // Initialize git integration
      await this.gitIntegration.initialize();
      
      // Initialize other components here
      
      console.log('MCP Server initialized successfully');
    } catch (error) {
      console.error('Failed to initialize MCP Server:', error);
      throw error;
    }
  }

  async start() {
    try {
      await this.initialize();
      await this.server.start();
      console.log('MCP Server started successfully');
    } catch (error) {
      console.error('Failed to start MCP Server:', error);
      throw error;
    }
  }

  async stop() {
    try {
      await this.server.stop();
      console.log('MCP Server stopped successfully');
    } catch (error) {
      console.error('Failed to stop MCP Server:', error);
      throw error;
    }
  }
}

// Export all components
export * from './tools/git';
export * from './error-handling';
export * from './types';