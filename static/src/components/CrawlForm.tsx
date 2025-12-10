import React, { useState } from 'react';
import { CrawlFormData } from '../types/CrawlFormData';
import { clearLogs } from '../utils/api';

interface CrawlFormProps {
    onSubmit: (data: CrawlFormData) => void;
    isRunning: boolean;
    onStop: () => void;
}

export default function CrawlForm({ onSubmit, isRunning, onStop }: CrawlFormProps) {
    const [url, setUrl] = useState('https://crawlme.monzo.com/');
    const [userAgent, setUserAgent] = useState('');
    const [allowedDomain, setAllowedDomain] = useState('');
    const [level, setLevel] = useState('');
    const [useStorage, setUseStorage] = useState(false);
    const [clearStorage, setClearStorage] = useState(true);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (isRunning) return;

        const data: CrawlFormData = { url };
        if (userAgent.trim()) data.user_agent = userAgent.trim();
        if (allowedDomain.trim()) data.allowed_domain = allowedDomain.trim();
        const levelNum = parseInt(level, 10);
        if (!isNaN(levelNum)) data.level = levelNum;
        if (useStorage) {
            data.use_storage = true;
            if (clearStorage) data.clear_storage = true;
        }
        onSubmit(data);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="form-group">
                <label htmlFor="url">Starting URL *</label>
                <input
                    type="text"
                    id="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://crawlme.monzo.com/"
                    required
                    disabled={isRunning}
                />
            </div>
            <div className="form-group">
                <label htmlFor="user_agent">User Agent</label>
                <input
                    type="text"
                    id="user_agent"
                    value={userAgent}
                    onChange={(e) => setUserAgent(e.target.value)}
                    placeholder="CrawleyBot/1.0"
                    disabled={isRunning}
                />
            </div>
            <div className="form-group">
                <label htmlFor="allowed_domain">Allowed Domain</label>
                <input
                    type="text"
                    id="allowed_domain"
                    value={allowedDomain}
                    onChange={(e) => setAllowedDomain(e.target.value)}
                    placeholder="Leave empty to use URL domain"
                    disabled={isRunning}
                />
            </div>
            <div className="form-group">
                <label htmlFor="level">Max Depth Level</label>
                <input
                    type="number"
                    id="level"
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                    placeholder="Leave empty for unlimited"
                    min="0"
                    disabled={isRunning}
                />
            </div>
            <div className="form-group">
                <div className="checkbox-group">
                    <input
                        type="checkbox"
                        id="use_storage"
                        checked={useStorage}
                        onChange={(e) => {
                            setUseStorage(e.target.checked);
                            if (!e.target.checked) setClearStorage(false);
                        }}
                        disabled={isRunning}
                    />
                    <label htmlFor="use_storage">Use Redis Storage</label>
                </div>
            </div>
            {useStorage && (
                <div className="form-group">
                    <div className="checkbox-group">
                        <input
                            type="checkbox"
                            id="clear_storage"
                            checked={clearStorage}
                            onChange={(e) => setClearStorage(e.target.checked)}
                            disabled={isRunning}
                        />
                        <label htmlFor="clear_storage">Clear Redis Storage Before Crawl</label>
                    </div>
                </div>
            )}
            <div className="button-group">
                <button type="submit" className="btn" disabled={isRunning}>
                    Start Crawl
                </button>
                {isRunning && (
                    <button type="button" className="btn btn-danger" onClick={onStop}>
                        Stop Crawl
                    </button>
                )}
                <button type="button" className="btn btn-secondary" onClick={() => clearLogs()}>
                    Clear Logs
                </button>
            </div>
        </form>
    );
}
