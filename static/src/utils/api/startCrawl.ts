import { CrawlFormData } from '../../types/CrawlFormData';

export async function startCrawl(data: CrawlFormData) {
    const res = await fetch('/api/crawl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const result = await res.json();
        throw new Error(result.error || 'Failed to start crawl');
    }
}

