export async function getRedisUiUrl(): Promise<string | null> {
    try {
        const res = await fetch('/api/redis-ui-url');
        const data = await res.json();
        return data.url || null;
    } catch {
        return null;
    }
}

