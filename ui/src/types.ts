export interface ResizeOption {
  mode: 'ratio' | 'fixed';
  ratio?: number;
  long_side_length?: number;
}

export interface Zone {
  id: string;
  label: string;
  description?: string;
  quality: number;
  color?: string;
  resize?: ResizeOption;
}

export interface FileResult {
  file: string;
  status: 'converted' | 'skipped' | 'failed';
  output?: string;
  error?: string;
}

export interface Job {
  job_id: string;
  zone_id: string;
  quality: number;
  resize?: ResizeOption;
  total: number;
  done: number;
  state: 'pending' | 'running' | 'done';
  results: FileResult[];
}

export interface JobUpdate {
  job_id: string;
  done: number;
  total: number;
  state: string;
  latest?: FileResult;
  results?: FileResult[];  // 작업 완료 시 전체 결과
}
