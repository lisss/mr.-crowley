export interface CrawlFormData {
    url: string;
    user_agent?: string;
    allowed_domain?: string;
    level?: number;
    use_storage?: boolean;
    clear_storage?: boolean;
}

