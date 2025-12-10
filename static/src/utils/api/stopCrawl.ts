export async function stopCrawl() {
    const res = await fetch('/api/stop-crawl', { method: 'POST' });
    if (!res.ok) {
        const result = await res.json();
        throw new Error(result.error || 'Failed to stop crawl');
    }
}

