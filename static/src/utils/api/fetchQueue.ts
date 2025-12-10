import { QueueData } from '../../types/QueueData';

export async function fetchQueue(): Promise<QueueData> {
    const res = await fetch('/api/queue');
    return res.json();
}

