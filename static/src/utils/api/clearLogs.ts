export async function clearLogs() {
    await fetch('/api/clear-logs', { method: 'POST' });
}

