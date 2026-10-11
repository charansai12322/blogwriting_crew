export interface HealthStatus {
  status: string;
  message: string;
  model: string;
  agents: string[];
}

export interface BlogStats {
  word_count: number;
  char_count: number;
}

export interface BlogMetadata {
  model: string;
  stats: BlogStats;
}

export interface BlogGenerateResponse {
  success: boolean;
  topic: string;
  blog: string;
  metadata: BlogMetadata;
}

export interface ApiError {
  message: string;
  status?: number;
}
