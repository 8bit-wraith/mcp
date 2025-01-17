import { z } from 'zod';

export const GitHubAuthorSchema = z.object({
  name: z.string(),
  email: z.string(),
  date: z.string()
});

export const GitHubOwnerSchema = z.object({
  login: z.string(),
  id: z.number(),
  node_id: z.string(),
  avatar_url: z.string(),
  url: z.string(),
  html_url: z.string(),
  type: z.string()
});

export const GitHubRepositorySchema = z.object({
  id: z.number(),
  node_id: z.string(),
  name: z.string(),
  full_name: z.string(),
  private: z.boolean(),
  owner: GitHubOwnerSchema,
  html_url: z.string(),
  description: z.string().nullable(),
  fork: z.boolean(),
  url: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  pushed_at: z.string(),
  git_url: z.string(),
  ssh_url: z.string(),
  clone_url: z.string(),
  default_branch: z.string()
});

export const GitHubReferenceSchema = z.object({
  ref: z.string(),
  node_id: z.string(),
  url: z.string(),
  object: z.object({
    sha: z.string(),
    type: z.string(),
    url: z.string()
  })
});

export const GitHubForkSchema = GitHubRepositorySchema.extend({
  parent: GitHubRepositorySchema,
  source: GitHubRepositorySchema
});

export const GitCommandSchema = z.object({
  owner: z.string(),
  repo: z.string(),
  branch: z.string().optional(),
  message: z.string().optional(),
  files: z.array(
    z.object({
      path: z.string(),
      content: z.string()
    })
  ).optional()
});