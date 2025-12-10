import { VisitedUrl } from './VisitedUrl';

export interface VisitedUrlsData {
    visited?: VisitedUrl[];
    total?: number;
    level_distribution?: { [key: number]: number };
    error?: string;
}

