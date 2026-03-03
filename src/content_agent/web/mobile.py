"""
Mobile-responsive enhancements for web dashboards.
Progressive Web App (PWA) support and mobile-optimized UI.
"""

# Mobile-optimized CSS to be injected into dashboard HTML
MOBILE_CSS = """
/* Mobile-first responsive design */
@media (max-width: 768px) {
    /* Header adjustments */
    .header {
        padding: 1rem !important;
    }
    .header h1 {
        font-size: 1.5rem !important;
    }
    
    /* Container padding */
    .container {
        padding: 1rem !important;
    }
    
    /* Stats grid - single column on mobile */
    .stats-grid {
        grid-template-columns: 1fr !important;
        gap: 0.75rem !important;
    }
    .stat-card {
        padding: 1rem !important;
    }
    .stat-value {
        font-size: 1.75rem !important;
    }
    
    /* Layers section - stack vertically */
    .layers-section {
        grid-template-columns: 1fr !important;
    }
    .layer-card {
        margin-bottom: 1rem;
    }
    
    /* Actions - stack buttons */
    .actions {
        flex-direction: column !important;
        gap: 0.5rem !important;
    }
    .btn {
        width: 100% !important;
        padding: 0.875rem !important;
        font-size: 1rem !important;
    }
    
    /* Search box */
    .search-box {
        padding: 1rem !important;
    }
    .search-box input {
        font-size: 16px !important; /* Prevents zoom on iOS */
    }
    
    /* Memory list */
    .memory-list {
        max-height: 200px !important;
    }
    .memory-item {
        font-size: 0.8rem !important;
        padding: 0.5rem !important;
    }
    
    /* Log container */
    .log-container {
        height: 200px !important;
        font-size: 0.8rem !important;
    }
    
    /* Tables - make them scrollable */
    table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
    
    /* Touch-friendly tap targets */
    button, .btn, input, select {
        min-height: 44px;
        min-width: 44px;
    }
    
    /* Prevent text zoom on orientation change */
    html {
        -webkit-text-size-adjust: 100%;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
    .layers-section {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    /* Already dark by default, but ensure consistency */
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* PWA standalone mode adjustments */
@media (display-mode: standalone) {
    .header {
        padding-top: env(safe-area-inset-top) !important;
    }
    .container {
        padding-bottom: env(safe-area-inset-bottom) !important;
    }
}
"""

# PWA manifest for Agent Memory Kit
AMK_MANIFEST = {
    "name": "Agent Memory Kit Dashboard",
    "short_name": "AMK Dashboard",
    "description": "Visual memory management for AI agents",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0f172a",
    "theme_color": "#667eea",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/static/icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# PWA manifest for Content Agent
CA_MANIFEST = {
    "name": "Content Agent Dashboard",
    "short_name": "Content Agent",
    "description": "AI-powered content curation and publishing",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#1e1b4b",
    "theme_color": "#3b82f6",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/static/icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# Service Worker for offline support
SERVICE_WORKER = """
const CACHE_NAME = 'agent-app-v1';
const urlsToCache = [
    '/',
    '/static/styles.css',
    '/static/app.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached or fetch new
                return response || fetch(event.request);
            })
    );
});
"""


def get_mobile_meta_tags() -> str:
    """Get HTML meta tags for mobile optimization."""
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0f172a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    """


def inject_mobile_css(dashboard_html: str) -> str:
    """Inject mobile CSS into dashboard HTML."""
    # Insert CSS before closing </style> tag or add new style tag
    if "</style>" in dashboard_html:
        return dashboard_html.replace(
            "</style>",
            f"{MOBILE_CSS}\n</style>"
        )
    else:
        # Add style tag in head
        css_block = f"<style>{MOBILE_CSS}</style>"
        return dashboard_html.replace("</head>", f"{css_block}\n</head>")


def inject_mobile_meta(html: str) -> str:
    """Inject mobile meta tags into HTML head."""
    meta_tags = get_mobile_meta_tags()
    return html.replace("<head>", f"<head>\n    {meta_tags}")


# Touch gesture support JavaScript
TOUCH_JS = """
<script>
// Touch gesture support for mobile
document.addEventListener('DOMContentLoaded', () => {
    let touchStartX = 0;
    let touchEndX = 0;
    
    const minSwipeDistance = 50;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, false);
    
    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, false);
    
    function handleSwipe() {
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > minSwipeDistance) {
            if (swipeDistance > 0) {
                // Swipe right - could go back
                console.log('Swipe right detected');
            } else {
                // Swipe left - could open menu
                console.log('Swipe left detected');
            }
        }
    }
    
    // Pull-to-refresh support
    let touchStartY = 0;
    document.addEventListener('touchstart', (e) => {
        touchStartY = e.changedTouches[0].screenY;
    }, false);
    
    document.addEventListener('touchend', (e) => {
        const touchEndY = e.changedTouches[0].screenY;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // If at top and pulled down
        if (scrollTop === 0 && touchEndY - touchStartY > 100) {
            location.reload();
        }
    }, false);
});

// Service Worker registration
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then((reg) => console.log('Service Worker registered'))
        .catch((err) => console.log('Service Worker failed', err));
}
</script>
"""


def make_pwa_compatible(html: str, app_name: str = "Agent App") -> str:
    """
    Make HTML PWA-compatible with mobile optimizations.
    
    Args:
        html: Original HTML
        app_name: App name for manifest
        
    Returns:
        Enhanced HTML with PWA support
    """
    # Add mobile meta tags
    html = inject_mobile_meta(html)
    
    # Add mobile CSS
    html = inject_mobile_css(html)
    
    # Add touch JS before closing body
    if "</body>" in html:
        html = html.replace("</body>", f"{TOUCH_JS}\n</body>")
    else:
        html += TOUCH_JS
    
    return html
