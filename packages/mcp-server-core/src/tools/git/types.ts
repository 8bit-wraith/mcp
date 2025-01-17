export interface GitHubAuthor {
  name: string;
  email: string;
  date: string;
}

export interface GitHubOwner {
  login: string;
  id: number;
  node_id: string;
  avatar_url: string;
  url: string;
  html_url: string;
  type: string;
}

export interface GitHubRepository {
  id: number;
  node_id: string;
  name: string;
  full_name: string;
  private: boolean;
  owner: GitHubOwner;
  html_url: string;
  description: string | null;
  fork: boolean;
  url: string;
  created_at: string;
  updated_at: string;
  pushed_at: string;
  git_url: string;
  ssh_url: string;
  clone_url: string;
  default_branch: string;
}

export interface GitFile {
  path: string;
  content: string;
}

export interface GitCommit {
  message: string;
  files: GitFile[];
  branch?: string;
}

export interface GitAnalysis {
  commitPatterns: {
    frequency: Record<string, number>;
    authors: Array<{ email: string; count: number }>;
    total: number;
  };
  languages: Record<string, number>;
  issueHealth: {
    total: number;
    open: number;
    closed: number;
    avgResolutionTime: number;
  };
}