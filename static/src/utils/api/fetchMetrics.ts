import { MetricsData } from '../../types/MetricsData';

export async function fetchMetrics(): Promise<MetricsData> {
    const res = await fetch('/api/metrics');
    return res.json();
}

