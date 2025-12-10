import React, { useEffect, useRef } from 'react';

interface LogsProps {
    logs: string;
}

export default function Logs({ logs }: LogsProps) {
    const logsEndRef = useRef<HTMLDivElement>(null);
    const logsContainerRef = useRef<HTMLDivElement>(null);
    const shouldScrollRef = useRef(true);

    useEffect(() => {
        if (logsContainerRef.current) {
            const container = logsContainerRef.current;
            const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
            shouldScrollRef.current = isNearBottom;
        }
    }, [logs]);

    useEffect(() => {
        if (shouldScrollRef.current && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    return (
        <div className="card">
            <h2 style={{ marginBottom: '15px' }}>Crawl Logs</h2>
            <div className="logs" ref={logsContainerRef}>
                {logs}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
}
