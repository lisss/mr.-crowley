import { VisitedUrlsData } from '../../types/VisitedUrlsData';

export async function fetchVisitedUrls(): Promise<VisitedUrlsData> {
    const res = await fetch('/api/visited-urls');
    return res.json();
}

