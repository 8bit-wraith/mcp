import { GitContext } from '../git-context';

export async function createCommitCommand(context: GitContext, params: any) {
  const { owner, repo, message, files, branch } = params;
  return await context.createCommit(owner, repo, message, files, branch);
}

export async function getCommitCommand(context: GitContext, params: any) {
  const { owner, repo, sha } = params;
  return await context.getCommit(owner, repo, sha);
}

export async function listCommitsCommand(context: GitContext, params: any) {
  const { owner, repo, branch, path } = params;
  return await context.listCommits(owner, repo, branch, path);
}