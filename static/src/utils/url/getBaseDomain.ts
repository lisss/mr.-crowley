export function getBaseDomain(url: string): string | null {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.split(':')[0];
    } catch {
        return null;
    }
}

