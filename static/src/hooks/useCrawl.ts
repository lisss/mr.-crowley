import { useState, useEffect, useRef } from 'react';
import { CrawlFormData } from '../types/CrawlFormData';
import { CrawlStatus } from '../types/CrawlStatus';
import { startCrawl } from '../utils/api/startCrawl';
import { stopCrawl } from '../utils/api/stopCrawl';
import { fetchLogs } from '../utils/api/fetchLogs';

export function useCrawl() {
    const [logs, setLogs] = useState('No logs yet. Start a crawl to see output.');
    const [status, setStatus] = useState<CrawlStatus>('idle');
    const [isRunning, setIsRunning] = useState(false);
    const intervalRef = useRef<number | null>(null);

    const updateLogs = async () => {
        try {
            const data = await fetchLogs();
            setLogs(data.logs || 'No logs yet.');
            
            if (data.status === 'idle' && isRunning) {
                setIsRunning(false);
                setStatus('idle');
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }
            } else if (data.status === 'error') {
                setIsRunning(false);
                setStatus('error');
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }
            } else if (data.status === 'running') {
                setStatus('running');
            }
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    };

    useEffect(() => {
        const interval = setInterval(updateLogs, 5000);
        return () => clearInterval(interval);
    }, [isRunning]);

    const handleStart = async (formData: CrawlFormData) => {
        setIsRunning(true);
        setStatus('running');
        setLogs('Starting crawl...\n');

        try {
            await startCrawl(formData);
            intervalRef.current = setInterval(updateLogs, 500);
        } catch (error) {
            setStatus('error');
            setLogs(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setIsRunning(false);
        }
    };

    const handleStop = async () => {
        try {
            await stopCrawl();
            setIsRunning(false);
            setStatus('idle');
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            updateLogs();
        } catch (error) {
            console.error('Error stopping crawl:', error);
        }
    };

    return { logs, status, isRunning, startCrawl: handleStart, stopCrawl: handleStop };
}
