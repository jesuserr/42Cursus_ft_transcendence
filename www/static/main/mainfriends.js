(function() {
    function setupEventListeners() {
        var toggleButton = document.getElementById('toggleButton');
        if (toggleButton) {
            toggleButton.addEventListener('click', function() {
                var iframeContainer = document.getElementById('iframeContainer');
                if (iframeContainer.style.display === 'none' || iframeContainer.style.display === '') {
                    iframeContainer.style.display = 'block';
                } else {
                    iframeContainer.style.display = 'none';
                }
            });
        }

        window.addEventListener('message', function(event) {
            if (event.data === 'closeIframe') {
                var iframeContainer = document.getElementById('iframeContainer');
                if (iframeContainer) {
                    iframeContainer.style.display = 'none';
                }
            }
        }, false);
    }

    if (document.readyState === 'loading') {  // El DOM aún no está completamente cargado.
        document.addEventListener('DOMContentLoaded', setupEventListeners);
    } else {  // `DOMContentLoaded` ya fue disparado
        setupEventListeners();
    }
})();