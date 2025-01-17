import { Server } from "@modelcontextprotocol/sdk/server";
import { GitHubForkSchema, GitHubReferenceSchema, GitHubRepositorySchema } from './schemas';
import { ContextType } from '../../types';
import { ErrorHandler } from '../../error-handling';

export class GitContext {
  private errorHandler: ErrorHandler;

  constructor(
    private server: Server,
    private token: string
  ) {
    this.errorHandler = new ErrorHandler();
    this.setupGitCommands();
  }

  private async githubRequest(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<any> {
    const url = `https://api.github.com${endpoint}`;
    const defaultOptions = {
      headers: {
        "Authorization": `token ${this.token}`,
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "mcp-server"
      }
    };

    return this.errorHandler.handleAPIOperation(
      async () => {
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (!response.ok) {
          throw new Error(`GitHub API error: ${response.statusText}`);
        }
        return response.json();
      },
      endpoint,
      options
    );
  }

  private setupGitCommands() {
    // Fork repository command
    this.server.defineCommand({
      name: "git.fork",
      description: "Fork a GitHub repository",
      handler: async ({ owner, repo, organization }) => {
        const url = organization
          ? `/repos/${owner}/${repo}/forks?organization=${organization}`
          : `/repos/${owner}/${repo}/forks`;

        const response = await this.githubRequest(url, { method: "POST" });
        return GitHubForkSchema.parse(response);
      }
    });

    // Create branch command
    this.server.defineCommand({
      name: "git.createBranch",
      description: "Create a new branch in a repository",
      handler: async ({ owner, repo, branch, sourceBranch }) => {
        // Get source branch SHA
        const sourceResponse = await this.githubRequest(
          `/repos/${owner}/${repo}/git/refs/heads/${sourceBranch || 'main'}`
        );
        
        const sha = GitHubReferenceSchema.parse(sourceResponse).object.sha;
        
        // Create new branch
        const response = await this.githubRequest(
          `/repos/${owner}/${repo}/git/refs`,
          {
            method: "POST",
            body: JSON.stringify({
              ref: `refs/heads/${branch}`,
              sha
            })
          }
        );

        return GitHubReferenceSchema.parse(response);
      }
    });

    // Push changes command
    this.server.defineCommand({
      name: "git.push",
      description: "Push changes to a repository",
      handler: async ({ owner, repo, branch, files, message }) => {
        // Create tree
        const tree = await this.createTree(owner, repo, files);
        
        // Create commit
        const commit = await this.createCommit(owner, repo, message, tree.sha);
        
        // Update reference
        return this.updateReference(owner, repo, branch, commit.sha);
      }
    });

    // Commit analysis command
    this.server.defineCommand({
      name: "git.analyze",
      description: "Analyze git repository patterns",
      handler: async ({ owner, repo }) => {
        const analysis = await this.analyzeRepository(owner, repo);
        return {
          type: ContextType.GIT,
          data: analysis
        };
      }
    });
  }

  private async createTree(owner: string, repo: string, files: Array<{ path: string, content: string }>) {
    const response = await this.githubRequest(
      `/repos/${owner}/${repo}/git/trees`,
      {
        method: "POST",
        body: JSON.stringify({
          tree: files.map(file => ({
            path: file.path,
            mode: '100644',
            type: 'blob',
            content: file.content
          }))
        })
      }
    );
    return response;
  }

  private async createCommit(owner: string, repo: string, message: string, tree: string) {
    const response = await this.githubRequest(
      `/repos/${owner}/${repo}/git/commits`,
      {
        method: "POST",
        body: JSON.stringify({
          message,
          tree,
          parents: [tree] // Current implementation assumes single parent
        })
      }
    );
    return response;
  }

  private async updateReference(owner: string, repo: string, branch: string, sha: string) {
    const response = await this.githubRequest(
      `/repos/${owner}/${repo}/git/refs/heads/${branch}`,
      {
        method: "PATCH",
        body: JSON.stringify({
          sha,
          force: true
        })
      }
    );
    return response;
  }

  private async analyzeRepository(owner: string, repo: string) {
    // Get repository information
    const repoInfo = await this.githubRequest(`/repos/${owner}/${repo}`);
    
    // Get commit history
    const commits = await this.githubRequest(
      `/repos/${owner}/${repo}/commits`
    );

    // Analyze patterns
    const patterns = {
      commitFrequency: this.analyzeCommitFrequency(commits),
      contributorPatterns: this.analyzeContributors(commits),
      codeHealth: await this.analyzeCodeHealth(owner, repo)
    };

    return {
      repository: GitHubRepositorySchema.parse(repoInfo),
      analysis: patterns
    };
  }

  private analyzeCommitFrequency(commits: any[]) {
    // Group commits by day/week/month
    const groupedByDay = new Map<string, number>();
    commits.forEach(commit => {
      const date = new Date(commit.commit.author.date).toISOString().split('T')[0];
      groupedByDay.set(date, (groupedByDay.get(date) || 0) + 1);
    });

    return {
      daily: Object.fromEntries(groupedByDay),
      total: commits.length,
      averagePerDay: commits.length / groupedByDay.size
    };
  }

  private analyzeContributors(commits: any[]) {
    const contributors = new Map<string, number>();
    commits.forEach(commit => {
      const author = commit.commit.author.email;
      contributors.set(author, (contributors.get(author) || 0) + 1);
    });

    return Array.from(contributors.entries())
      .map(([email, count]) => ({ email, count }))
      .sort((a, b) => b.count - a.count);
  }

  private async analyzeCodeHealth(owner: string, repo: string) {
    // Get repository languages
    const languages = await this.githubRequest(
      `/repos/${owner}/${repo}/languages`
    );

    // Get recent issues
    const issues = await this.githubRequest(
      `/repos/${owner}/${repo}/issues?state=all&per_page=100`
    );

    return {
      languages,
      issueHealth: {
        total: issues.length,
        open: issues.filter((i: any) => i.state === 'open').length,
        closed: issues.filter((i: any) => i.state === 'closed').length
      }
    };
  }
}