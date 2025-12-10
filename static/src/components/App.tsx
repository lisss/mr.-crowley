import React, { useState, useEffect } from 'react';
import StatusBar from './StatusBar';
import CrawlForm from './CrawlForm';
import Logs from './Logs';
import VisitedUrls from './VisitedUrls';
import { useCrawl } from '../hooks/useCrawl';
import { getRedisUiUrl } from '../utils/api/getRedisUiUrl';

export default function App() {
    const { logs, status, isRunning, startCrawl, stopCrawl } = useCrawl();
    const [redisUiUrl, setRedisUiUrl] = useState<string | null>(null);

    useEffect(() => {
        getRedisUiUrl().then(setRedisUiUrl).catch(() => {});
    }, []);

    const handleRedisClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (!redisUiUrl) {
            e.preventDefault();
            document.getElementById('visited-urls-section')?.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h1>🕷️ Crawley</h1>
                <p>Run web crawls with a simple interface</p>
            </div>

            <div className="card">
                <StatusBar status={status} />
                <CrawlForm onSubmit={startCrawl} isRunning={isRunning} onStop={stopCrawl} />
                <div className="links">
                    <a
                        href={redisUiUrl || "#visited-urls-section"}
                        className="link-btn"
                        target={redisUiUrl ? "_blank" : undefined}
                        rel={redisUiUrl ? "noopener noreferrer" : undefined}
                        onClick={handleRedisClick}
                    >
                        View Redis Data
                    </a>
                </div>
            </div>

            <Logs logs={logs} />
            <div id="visited-urls-section">
                <VisitedUrls isRunning={isRunning} />
            </div>
        </div>
    );
}
