import { GitContext } from '../git-context';

export async function createBranchCommand(context: GitContext, params: any) {
  const { owner, repo, branch, sourceBranch } = params;
  return await context.createBranch(owner, repo, branch, sourceBranch);
}

export async function deleteBranchCommand(context: GitContext, params: any) {
  const { owner, repo, branch } = params;
  return await context.deleteBranch(owner, repo, branch);
}

export async function listBranchesCommand(context: GitContext, params: any) {
  const { owner, repo } = params;
  return await context.listBranches(owner, repo);
}