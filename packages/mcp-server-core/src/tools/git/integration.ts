import { Server } from '@modelcontextprotocol/sdk/server';
import { GitContext } from './git-context';
import { ErrorHandler } from '../../error-handling';

export class GitIntegration {
  private gitContext: GitContext;
  private errorHandler: ErrorHandler;

  constructor(private server: Server, private token: string) {
    this.errorHandler = new ErrorHandler();
    this.gitContext = new GitContext(server, token);
  }

  async initialize() {
    await this.setupCommands();
    await this.setupWebhooks();
    console.log('Git integration initialized');
  }

  private async setupCommands() {
    const commands = [
      {
        name: 'git.analyze',
        description: 'Analyze a git repository',
        handler: async (params: any) => {
          return await this.errorHandler.validateAndExecute(
            () => this.gitContext.analyzeRepository(params.owner, params.repo),
            params,
            ['owner', 'repo'],
            'git.analyze'
          );
        }
      },
      {
        name: 'git.commit',
        description: 'Create a commit in a repository',
        handler: async (params: any) => {
          return await this.errorHandler.validateAndExecute(
            () => this.gitContext.createCommit(params.owner, params.repo, params.message, params.files),
            params,
            ['owner', 'repo', 'message', 'files'],
            'git.commit'
          );
        }
      }
    ];

    commands.forEach(cmd => this.server.defineCommand(cmd));
  }

  private async setupWebhooks() {
    // Setup webhook handlers for git events
    this.server.on('git.push', async (event: any) => {
      await this.handlePushEvent(event);
    });

    this.server.on('git.pr', async (event: any) => {
      await this.handlePullRequestEvent(event);
    });
  }

  private async handlePushEvent(event: any) {
    console.log('Handling git push event:', event);
    // Implement push event handling
  }

  private async handlePullRequestEvent(event: any) {
    console.log('Handling pull request event:', event);
    // Implement PR event handling
  }
}