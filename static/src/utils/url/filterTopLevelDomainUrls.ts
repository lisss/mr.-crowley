import { getBaseDomain } from './getBaseDomain';

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

