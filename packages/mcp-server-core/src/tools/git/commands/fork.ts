import { GitContext } from '../git-context';

export async function forkCommand(context: GitContext, params: any) {
  const { owner, repo, organization } = params;
  return await context.forkRepository(owner, repo, organization);
}

export async function listForksCommand(context: GitContext, params: any) {
  const { owner, repo } = params;
  return await context.listForks(owner, repo);
}