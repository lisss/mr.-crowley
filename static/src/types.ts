export interface VisitedUrl {
    url: string;
    level: number;
}

export interface VisitedUrlsData {
    visited?: VisitedUrl[];
    total?: number;
    level_distribution?: { [key: number]: number };
    error?: string;
}

export interface CrawlFormData {
    url: string;
    user_agent?: string;
    allowed_domain?: string;
    level?: number;
    use_storage?: boolean;
}

export interface LogsResponse {
    logs: string;
    status: 'idle' | 'running' | 'error';
}

export interface MetricsData {
    crawl_id: number;
    visited: number;
    seen: number;
    queued: number;
    queue_length: number;
}

export interface QueueData {
    queue: string[];
    length: number;
}

export type SortField = 'level' | 'url';
export type SortOrder = 'asc' | 'desc';
export type CrawlStatus = 'idle' | 'running' | 'error';

