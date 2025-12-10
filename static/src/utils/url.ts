export function getBaseDomain(url: string): string | null {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.split(':')[0];
    } catch {
        return null;
    }
}

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

export function filterTopLevelDomainUrls(urls: { url: string }[]): { url: string }[] {
    if (urls.length === 0) return urls;
    
    const domainCounts: { [key: string]: number } = {};
    urls.forEach(item => {
        const domain = getBaseDomain(item.url);
        if (domain) {
            domainCounts[domain] = (domainCounts[domain] || 0) + 1;
        }
    });
    
    const topDomain = Object.keys(domainCounts).reduce((a, b) => 
        domainCounts[a] > domainCounts[b] ? a : b
    );
    
    return urls.filter(item => getBaseDomain(item.url) === topDomain);
}

