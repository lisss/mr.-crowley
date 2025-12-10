import { CrawlFormData, LogsResponse, VisitedUrlsData, MetricsData, QueueData } from '../types';

export async function startCrawl(data: CrawlFormData): Promise<void> {
    const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || 'Failed to start crawl');
    }
}

export async function stopCrawl(): Promise<void> {
    const response = await fetch('/api/stop-crawl', { method: 'POST' });
    
    if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || 'Failed to stop crawl');
    }
}

export async function fetchLogs(): Promise<LogsResponse> {
    const response = await fetch('/api/logs');
    return response.json();
}

export async function fetchVisitedUrls(): Promise<VisitedUrlsData> {
    const response = await fetch('/api/visited-urls');
    return response.json();
}

export async function fetchMetrics(): Promise<MetricsData> {
    const response = await fetch('/api/metrics');
    return response.json();
}

export async function fetchQueue(): Promise<QueueData> {
    const response = await fetch('/api/queue');
    return response.json();
}

export async function clearLogs(): Promise<void> {
    await fetch('/api/clear-logs', { method: 'POST' });
}

export async function getRedisUiUrl(): Promise<string | null> {
    try {
        const response = await fetch('/api/redis-ui-url');
        const data = await response.json();
        return data.url || null;
    } catch {
        return null;
    }
}

