import { VisitedUrl } from '../types';
import { getUrlPattern, filterTopLevelDomainUrls } from './url';

export interface UrlPattern {
    pattern: string;
    count: number;
}

export function groupUrlsByPattern(urls: VisitedUrl[]): UrlPattern[] {
    const filtered = filterTopLevelDomainUrls(urls);
    const distribution: { [key: string]: number } = {};
    
    filtered.forEach(item => {
        const pattern = getUrlPattern(item.url);
        distribution[pattern] = (distribution[pattern] || 0) + 1;
    });

    const entries = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    return entries.map(([pattern, count]) => ({ pattern, count }));
}

