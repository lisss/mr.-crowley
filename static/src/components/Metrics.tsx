import React, { useState, useEffect } from 'react';
import { MetricsData } from '../types/MetricsData';
import { QueueData } from '../types/QueueData';
import { fetchMetrics } from '../utils/api/fetchMetrics';
import { fetchQueue } from '../utils/api/fetchQueue';

export default function Metrics() {
    const [metrics, setMetrics] = useState<MetricsData | null>(null);
    const [queue, setQueue] = useState<QueueData | null>(null);
    const [loading, setLoading] = useState(false);
    const [showQueue, setShowQueue] = useState(false);

    const loadData = async () => {
        setLoading(true);
        try {
            const [metricsData, queueData] = await Promise.all([
                fetchMetrics(),
                fetchQueue()
            ]);
            setMetrics(metricsData);
            setQueue(queueData);
        } catch (error) {
            console.error('Error fetching metrics:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (!metrics || !queue) {
        return (
            <div className="card">
                <h2>Redis Metrics</h2>
                <div>{loading ? 'Loading...' : 'No data available'}</div>
            </div>
        );
    }

    const visitedVsSeen = metrics.seen > 0 
        ? ((metrics.visited / metrics.seen) * 100).toFixed(1)
        : '0.0';

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h2>Redis Metrics (Crawl #{metrics.crawl_id})</h2>
                <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
                    Refresh
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
                <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>Visited URLs</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>{metrics.visited}</div>
                </div>
                
                <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>Seen URLs</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>{metrics.seen}</div>
                </div>
                
                <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>Queued (Set)</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>{metrics.queued}</div>
                </div>
                
                <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>Queue Length</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: queue.length > 0 ? '#dc3545' : '#28a745' }}>
                        {queue.length}
                    </div>
                </div>
            </div>

            <div style={{ marginBottom: '15px', padding: '15px', background: '#e7f3ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>Visited / Seen Ratio</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#007bff' }}>
                    {visitedVsSeen}%
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                    {metrics.visited} visited out of {metrics.seen} seen URLs
                </div>
            </div>

            {metrics.seen > metrics.visited && (
                <div style={{ marginBottom: '15px', padding: '15px', background: '#fff3cd', borderRadius: '8px', border: '1px solid #ffc107' }}>
                    <div style={{ fontSize: '14px', color: '#856404', fontWeight: 'bold' }}>
                        ⚠️ {metrics.seen - metrics.visited} URLs were seen but not visited
                    </div>
                </div>
            )}

            {queue.length > 0 && (
                <div style={{ marginBottom: '15px', padding: '15px', background: '#f8d7da', borderRadius: '8px', border: '1px solid #dc3545' }}>
                    <div style={{ fontSize: '14px', color: '#721c24', fontWeight: 'bold' }}>
                        ⚠️ {queue.length} URLs still in queue
                    </div>
                </div>
            )}

            <div style={{ marginTop: '20px' }}>
                <button 
                    className="btn btn-secondary" 
                    onClick={() => setShowQueue(!showQueue)}
                    style={{ marginBottom: '10px' }}
                >
                    {showQueue ? 'Hide' : 'Show'} Queue ({queue.length} items)
                </button>

                {showQueue && (
                    <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #e0e0e0', borderRadius: '8px', padding: '10px' }}>
                        {queue.queue.length === 0 ? (
                            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                                Queue is empty
                            </div>
                        ) : (
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                                        <th style={{ padding: '10px', textAlign: 'left', width: '50px' }}>#</th>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>URL</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {queue.queue.map((url, index) => (
                                        <tr key={index} style={{ borderBottom: '1px solid #f0f0f0' }}>
                                            <td style={{ padding: '10px', color: '#666' }}>{index + 1}</td>
                                            <td style={{ padding: '10px', wordBreak: 'break-all' }}>{url}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
