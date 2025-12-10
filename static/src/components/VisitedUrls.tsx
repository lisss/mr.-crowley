import React, { useState, useEffect } from 'react';
import { VisitedUrlsData } from '../types/VisitedUrlsData';
import { fetchVisitedUrls } from '../utils/api/fetchVisitedUrls';
import { groupUrlsByPattern } from '../utils/urlPatterns';

interface VisitedUrlsProps {
    isRunning: boolean;
}

export default function VisitedUrls({ isRunning }: VisitedUrlsProps) {
    const [patterns, setPatterns] = useState<{ pattern: string; count: number }[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data: VisitedUrlsData = await fetchVisitedUrls();
            if (!data.visited || data.error) {
                setError(data.error || 'Failed to load URLs');
                setTotal(0);
                setPatterns([]);
                return;
            }
            const grouped = groupUrlsByPattern(data.visited);
            setPatterns(grouped);
            setTotal(data.visited.length);
        } catch (err) {
            setError(`Failed to fetch URLs: ${err instanceof Error ? err.message : 'Unknown error'}`);
            setTotal(0);
            setPatterns([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        if (!isRunning) {
            loadData();
        }
    }, [isRunning]);

    const sorted = [...patterns].sort((a, b) => b.count - a.count);

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2>Visited URLs ({total})</h2>
                <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
                    Refresh
                </button>
            </div>

            {loading && <div style={{ padding: '10px', textAlign: 'center', color: '#666' }}>Loading...</div>}

            {error && (
                <div style={{ padding: '15px', marginBottom: '15px', backgroundColor: '#ffebee', color: '#c62828', borderRadius: '4px', border: '1px solid #ef5350' }}>
                    <strong>Error:</strong> {error}
                </div>
            )}

            <div style={{ maxHeight: '500px', overflowY: 'auto', border: '1px solid #e0e0e0', borderRadius: '8px', background: '#ffffff' }}>
                <div style={{ position: 'sticky', top: 0, background: '#f8f9fa', padding: '12px 15px', borderBottom: '2px solid #e0e0e0', zIndex: 10 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '10px', fontWeight: '600', color: '#333', fontSize: '14px' }}>
                        <div>URL pattern</div>
                        <div style={{ textAlign: 'center' }}>Count</div>
                    </div>
                </div>

                {sorted.length === 0 ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>No URLs visited yet</div>
                ) : (
                    <div>
                        {sorted.map((item, i) => (
                            <div
                                key={i}
                                style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '10px', padding: '12px 15px', borderBottom: '1px solid #f0f0f0' }}
                                onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
                                onMouseLeave={(e) => e.currentTarget.style.background = '#ffffff'}
                            >
                                <div style={{ wordBreak: 'break-all', fontSize: '13px', color: '#333', lineHeight: '1.5' }}>
                                    {item.pattern}
                                </div>
                                <div style={{ textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ background: '#e7f3ff', color: '#007bff', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '600' }}>
                                        {item.count}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
