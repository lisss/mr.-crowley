import React, { useState, useEffect, useCallback, useRef } from 'react';
import StatusBar from './components/StatusBar';
import CrawlForm from './components/CrawlForm';
import Logs from './components/Logs';
import VisitedUrls from './components/VisitedUrls';

interface CrawlFormData {
    url: string;
    user_agent?: string;
    allowed_domain?: string;
    level?: number;
    use_storage?: boolean;
}

interface LogsResponse {
    logs: string;
    status: 'idle' | 'running' | 'error';
}

function App(): JSX.Element {
    const [logs, setLogs] = useState<string>('No logs yet. Start a crawl to see output.');
    const [status, setStatus] = useState<'idle' | 'running' | 'error'>('idle');
    const [isRunning, setIsRunning] = useState<boolean>(false);
    const [redisUiUrl, setRedisUiUrl] = useState<string | null>(null);
    const logIntervalRef = useRef<number | null>(null);

    useEffect(() => {
        fetch('/api/redis-ui-url')
            .then(r => r.json())
            .then(data => {
                if (data.url) {
                    setRedisUiUrl(data.url);
                }
            })
            .catch(() => {});
    }, []);

    const fetchLogs = useCallback(async (): Promise<void> => {
        try {
            const response = await fetch('/api/logs');
            const data: LogsResponse = await response.json();
            setLogs(data.logs || 'No logs yet.');
            
            if (data.status === 'idle' && isRunning) {
                setIsRunning(false);
                setStatus('idle');
                if (logIntervalRef.current) {
                    clearInterval(logIntervalRef.current);
                    logIntervalRef.current = null;
                }
            } else if (data.status === 'error') {
                setIsRunning(false);
                setStatus('error');
                if (logIntervalRef.current) {
                    clearInterval(logIntervalRef.current);
                    logIntervalRef.current = null;
                }
            } else if (data.status === 'running') {
                setStatus('running');
            }
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    }, [isRunning]);

    useEffect(() => {
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, [fetchLogs]);

    const handleStartCrawl = async (formData: CrawlFormData): Promise<void> => {
        setIsRunning(true);
        setStatus('running');
        setLogs('Starting crawl...\n');

        try {
            const response = await fetch('/api/crawl', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to start crawl');
            }

            logIntervalRef.current = setInterval(fetchLogs, 500);
        } catch (error) {
            console.error('Error starting crawl:', error);
            setStatus('error');
            setLogs(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setIsRunning(false);
        }
    };

    const handleStopCrawl = async (): Promise<void> => {
        try {
            const response = await fetch('/api/stop-crawl', {
                method: 'POST',
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to stop crawl');
            }

            setIsRunning(false);
            setStatus('idle');
            if (logIntervalRef.current) {
                clearInterval(logIntervalRef.current);
                logIntervalRef.current = null;
            }
            fetchLogs();
        } catch (error) {
            console.error('Error stopping crawl:', error);
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
                    onSubmit={handleStartCrawl} 
                    isRunning={isRunning}
                    onStop={handleStopCrawl}
                />
                <div className="links">
                    <a 
                        href={redisUiUrl || "#visited-urls-section"} 
                        className="link-btn" 
                        target={redisUiUrl ? "_blank" : undefined}
                        rel={redisUiUrl ? "noopener noreferrer" : undefined}
                        onClick={(e) => {
                            if (!redisUiUrl) {
                                e.preventDefault();
                                const visitedUrlsSection = document.getElementById('visited-urls-section');
                                if (visitedUrlsSection) {
                                    visitedUrlsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }
                            }
                        }}
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

export default App;

