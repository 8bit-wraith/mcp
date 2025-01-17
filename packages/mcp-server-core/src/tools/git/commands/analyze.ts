import { GitContext } from '../git-context';

export async function analyzeCommand(context: GitContext, params: any) {
  const { owner, repo } = params;
  return await context.analyzeRepository(owner, repo);
}