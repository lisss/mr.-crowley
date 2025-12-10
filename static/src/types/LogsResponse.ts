export interface LogsResponse {
    logs: string;
    status: 'idle' | 'running' | 'error';
}

