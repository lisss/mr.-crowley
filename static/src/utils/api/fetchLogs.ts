import { LogsResponse } from '../../types/LogsResponse';

export async function fetchLogs(): Promise<LogsResponse> {
    const res = await fetch('/api/logs');
    return res.json();
}

