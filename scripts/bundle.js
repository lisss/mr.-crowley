const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '../static/dist');

const sections = {
    utils: [
        path.join(distDir, 'utils/api.js'),
        path.join(distDir, 'utils/url.js'),
        path.join(distDir, 'utils/urlPatterns.js'),
    ],
    hooks: [
        path.join(distDir, 'hooks/useCrawl.js'),
    ],
    components: [
        path.join(distDir, 'components/StatusBar.js'),
        path.join(distDir, 'components/Logs.js'),
        path.join(distDir, 'components/CrawlForm.js'),
        path.join(distDir, 'components/VisitedUrls/useVisitedUrls.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrlsHeader.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrlsError.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrlsListHeader.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrlsListItem.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrlsList.js'),
        path.join(distDir, 'components/VisitedUrls/VisitedUrls.js'),
        path.join(distDir, 'components/Metrics/useMetrics.js'),
        path.join(distDir, 'components/Metrics/MetricsHeader.js'),
        path.join(distDir, 'components/Metrics/MetricsGrid.js'),
        path.join(distDir, 'components/Metrics/MetricsRatio.js'),
        path.join(distDir, 'components/Metrics/MetricsWarnings.js'),
        path.join(distDir, 'components/Metrics/MetricsQueue.js'),
        path.join(distDir, 'components/Metrics/Metrics.js'),
        path.join(distDir, 'components/App.js'),
    ],
};

const stripModuleSyntax = (code) => {
    return code
        .replace(/import\s+.*?from\s+['"].*?['"];?/g, '')
        .replace(/export\s+default\s+/g, '')
        .replace(/export\s+\{.*?\}\s+from\s+['"].*?['"];?/g, '')
        .replace(/exports\.default\s*=\s*\w+;?/g, '')
        .replace(/^export\s+(?=function|class|const|let|var|async)/gm, '');
};

const readFiles = (files) => files
    .filter(fs.existsSync)
    .map(filePath => stripModuleSyntax(fs.readFileSync(filePath, 'utf8')))
    .join('\n');

const utilsCode = readFiles(sections.utils);
const hooksCode = readFiles(sections.hooks);
const componentsCode = readFiles(sections.components);

const bundle = `const React = window.React;
const ReactDOM = window.ReactDOM;
const { useState, useEffect, useCallback, useRef, useMemo, useReducer, useContext } = React;
${utilsCode}
${hooksCode}
${componentsCode}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        const rootEl = document.getElementById('root');
        if (!rootEl) return;
        const root = ReactDOM.createRoot(rootEl);
        root.render(React.createElement(App, null));
    });
} else {
    const rootEl = document.getElementById('root');
    if (rootEl) {
        const root = ReactDOM.createRoot(rootEl);
        root.render(React.createElement(App, null));
    }
}`;

fs.writeFileSync(path.join(distDir, 'bundle.js'), bundle);
console.log('Bundle created successfully');
