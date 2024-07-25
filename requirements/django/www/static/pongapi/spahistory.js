window.addEventListener('popstate', function(event) {
    const currentUrl = new URL(window.location.href);
    const targetUrl = currentUrl.searchParams.get('url');
    if (currentUrl.pathname === '/pongapi/spa' && targetUrl) {
        fetch(targetUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                document.getElementById('content').innerHTML = html;
            })
            .catch(error => {
                console.error('Error fetching the page: ', error);
            });
    } else if (currentUrl.pathname === '/') {
        window.location.reload();
    }
});