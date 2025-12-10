export function getUrlPattern(url: string): string {
    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname.split(':')[0];
        const pathname = urlObj.pathname;
        const segments = pathname.split('/').filter(s => s !== '');
        
        if (segments.length === 0) {
            return hostname;
        }

        const first = segments[0].replace(/\.html?$/i, '');
        return `${hostname}/${first}`;
    } catch {
        return url;
    }
}

