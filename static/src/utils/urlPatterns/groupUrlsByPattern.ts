import { VisitedUrl } from '../../types/VisitedUrl';
import { getUrlPattern, filterTopLevelDomainUrls } from '../url';

export interface UrlPattern {
    pattern: string;
    count: number;
}

export function groupUrlsByPattern(urls: VisitedUrl[]): UrlPattern[] {
    const filtered = filterTopLevelDomainUrls(urls);
    const counts: { [key: string]: number } = {};
    
    filtered.forEach(item => {
        const pattern = getUrlPattern(item.url);
        counts[pattern] = (counts[pattern] || 0) + 1;
    });

    return Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([pattern, count]) => ({ pattern, count }));
}

