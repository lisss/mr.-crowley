import React from 'react';
import { CrawlStatus } from '../types/CrawlStatus';

interface StatusBarProps {
    status: CrawlStatus;
}

export default function StatusBar({ status }: StatusBarProps) {
    const statusClass = status === 'running' ? 'running' : status === 'error' ? 'error' : 'idle';
    const statusText = status === 'running' ? 'Running...' : status === 'error' ? 'Error' : 'Ready';

    return (
        <div className={`status ${statusClass}`}>
            Status: {statusText}
        </div>
    );
}
