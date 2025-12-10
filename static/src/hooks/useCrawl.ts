import { useState, useEffect, useCallback, useRef } from 'react';
import { CrawlFormData, CrawlStatus } from '../types';
import { startCrawl, stopCrawl, fetchLogs } from '../utils/api';

export function useCrawl() {
    const [logs, setLogs] = useState('No logs yet. Start a crawl to see output.');
    const [status, setStatus] = useState<CrawlStatus>('idle');
    const [isRunning, setIsRunning] = useState(false);
    const logIntervalRef = useRef<number | null>(null);

    const updateLogs = useCallback(async () => {
        try {
            const data = await fetchLogs();
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
        const interval = setInterval(updateLogs, 5000);
        return () => clearInterval(interval);
    }, [updateLogs]);

    const handleStart = async (formData: CrawlFormData) => {
        setIsRunning(true);
        setStatus('running');
        setLogs('Starting crawl...\n');

        try {
            await startCrawl(formData);
            logIntervalRef.current = setInterval(updateLogs, 500);
        } catch (error) {
            console.error('Error starting crawl:', error);
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
            if (logIntervalRef.current) {
                clearInterval(logIntervalRef.current);
                logIntervalRef.current = null;
            }
            updateLogs();
        } catch (error) {
            console.error('Error stopping crawl:', error);
        }
    };

    return {
        logs,
        status,
        isRunning,
        startCrawl: handleStart,
        stopCrawl: handleStop,
    };
}

