import React, { useState, useEffect } from 'react';
import StatusBar from './StatusBar';
import CrawlForm from './CrawlForm';
import Logs from './Logs';
import VisitedUrls from './VisitedUrls';
import { useCrawl } from '../hooks/useCrawl';
import { getRedisUiUrl } from '../utils/api';

export default function App() {
    const { logs, status, isRunning, startCrawl, stopCrawl } = useCrawl();
    const [redisUiUrl, setRedisUiUrl] = useState<string | null>(null);

    useEffect(() => {
        getRedisUiUrl().then(setRedisUiUrl);
    }, []);

    const handleViewRedisData = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (!redisUiUrl) {
            e.preventDefault();
            const section = document.getElementById('visited-urls-section');
            if (section) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
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
                <CrawlForm 
                    onSubmit={startCrawl} 
                    isRunning={isRunning}
                    onStop={stopCrawl}
                />
                <div className="links">
                    <a 
                        href={redisUiUrl || "#visited-urls-section"} 
                        className="link-btn" 
                        target={redisUiUrl ? "_blank" : undefined}
                        rel={redisUiUrl ? "noopener noreferrer" : undefined}
                        onClick={handleViewRedisData}
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

