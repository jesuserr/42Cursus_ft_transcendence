
(function() {
    function initializeLinks() {
        document.querySelectorAll('#content a').forEach(link => {
            if (link.id !== 'boton2' && link.id !== 'toggleButton' && link.id !== 'displayname') { 
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const href = this.getAttribute('href');
                    fetch(href)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Network response was not ok');
                            }
                            return response.text();
                        })
                        .then(html => {
                            const content = document.getElementById('content');
                            content.innerHTML = html;
                            const scripts = Array.from(content.querySelectorAll('script'));
                            scripts.forEach(script => {
                                const newScript = document.createElement('script');
                                if (script.src) {
                                    newScript.src = script.src;
                                } else {
                                    newScript.textContent = script.textContent;
                                }
                                script.parentNode.replaceChild(newScript, script);
                            });
                        })
                        .catch(error => {
                            console.error('Error loading the page: ', error);
                        });
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeLinks);
    } else {
        initializeLinks();
    }
})();