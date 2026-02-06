function getCookie(name: string) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}
export function getCSRFToken() {
    // Try production cookie name first, then fallback to development
    let token = getCookie('__Secure-csrftoken') || getCookie('csrftoken');
    
    if (!token) {
        console.debug('CSRF token not found in cookies.');
    }

    return token || '';
}

// Track CSRF initialization to prevent infinite loops
let csrfInitializing = false;
let csrfInitializePromise: Promise<string> | null = null;

// Initialize CSRF token when the app starts - call this once on app load
export async function initializeCSRFTokenOnStartup(): Promise<void> {
    // Don't initialize if we already have a token
    if (getCSRFToken()) {
        return;
    }
    
    try {
        await initializeCSRFToken();
    } catch (error) {
        console.warn('Failed to initialize CSRF token on startup:', error);
    }
}

// Function to initialize CSRF token by making a request to Django
export async function initializeCSRFToken(): Promise<string> {
    // Prevent multiple simultaneous initialization attempts
    if (csrfInitializing && csrfInitializePromise) {
        return csrfInitializePromise;
    }
    
    csrfInitializing = true;
    
    csrfInitializePromise = (async () => {
        try {
            const response = await fetch('/api/csrf/', {
                method: 'GET',
                credentials: 'include',  // Include cookies in the request
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'  // Helps identify AJAX requests
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Debug: Log the actual response to understand the format
                console.log('CSRF endpoint response:', data);
                
                // More flexible validation - check if we have a csrfToken
                if (!data.csrfToken && data.status !== 'ok') {
                    console.warn('Unexpected CSRF response format:', data);
                    // Don't throw error - try to continue anyway
                }
                
                // After the request, the cookie should be set, so try to get it again
                const token = getCookie('__Secure-csrftoken') || getCookie('csrftoken');
                return token || data.csrfToken || '';
            } else {
                const errorText = await response.text().catch(() => 'Unknown error');
                throw new Error(`CSRF initialization failed: ${response.status} - ${errorText}`);
            }
        } catch (error) {
            console.error('Failed to initialize CSRF token:', error);
            // Don't throw the error - return empty string to fail gracefully
            return '';
        } finally {
            csrfInitializing = false;
            csrfInitializePromise = null;
        }
    })();
    
    return csrfInitializePromise;
}
