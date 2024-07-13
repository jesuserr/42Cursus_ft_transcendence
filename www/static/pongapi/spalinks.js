/*(function() {
    document.querySelectorAll('#content a').forEach(link => {
        if (link.id !== 'boton2' && link.id !== 'toggleButton' && link.id !== 'displayname' && link.id !== 'mainmenu') {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                
                if (href.includes('/#')) {
                    // Si el enlace contiene /#, simplemente hacer scroll al elemento destino
                    const targetId = href.split('#')[1];
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    // Para todos los otros enlaces, proceder con la lógica normal
                    //console.log('Link clicked: ', href); // Debugging log
                    var baseUrl = window.location.origin; // Obtiene la base URL del sitio
                    var newUrl = baseUrl + '/pongapi/spa?url=' + encodeURIComponent(href);
                    history.pushState({ path: newUrl }, '', newUrl);
                    //console.log('New URL pushed to history: ', newUrl); // Debugging log
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
                            initializeBootstrapComponents();
                        })
                        .catch(error => {
                            console.error('Error loading the page: ', error);
                        });
                }
            });
        }
    });

    function initializeBootstrapComponents() {
        document.querySelectorAll('.dropdown-toggle').forEach(dropdown => {
            dropdown.addEventListener('click', function() {
                const menu = this.nextElementSibling;
                if (menu) {
                    menu.classList.toggle('show');
                }
            });
        });
        document.addEventListener('click', function(event) {
            const isDropdown = event.target.matches('.dropdown-toggle');
            const isInsideMenu = event.target.closest('.dropdown-menu.show') !== null;
            if (!isDropdown && !isInsideMenu) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            } else if (isInsideMenu) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initializeLinks();
            initializeBootstrapComponents();
        });
    } else {
        if (typeof initializeLinks === 'function') {
            initializeLinks();
        }
        initializeBootstrapComponents();
    }
})();*/

(function() {
    document.querySelectorAll('#content a').forEach(link => {
        if (link.id !== 'boton2' && link.id !== 'toggleButton' && link.id !== 'displayname' && link.id !== 'mainmenu') {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');

                if (href.includes('/#')) {
                    // Si el enlace contiene /#, simplemente hacer scroll al elemento destino
                    const targetId = href.split('#')[1];
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    // Para todos los otros enlaces, proceder con la lógica normal
                    var baseUrl = window.location.origin; // Obtiene la base URL del sitio
                    var newUrl = baseUrl + '/pongapi/spa?url=' + encodeURIComponent(href);
                    history.pushState({ path: newUrl }, '', newUrl);
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
                            initializeBootstrapComponents();
                        })
                        .catch(error => {
                            console.error('Error loading the page: ', error);
                        });
                }
            });
        }
    });

    function initializeBootstrapComponents() {
        document.querySelectorAll('.dropdown-toggle').forEach(dropdown => {
            dropdown.addEventListener('click', function() {
                const menu = this.nextElementSibling;
                if (menu) {
                    menu.classList.toggle('show');
                }
            });
        });
        document.addEventListener('click', function(event) {
            const isDropdown = event.target.matches('.dropdown-toggle');
            const isInsideMenu = event.target.closest('.dropdown-menu.show') !== null;
            if (!isDropdown && !isInsideMenu) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            } else if (isInsideMenu) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initializeBootstrapComponents();
        });
    } else {
        initializeBootstrapComponents();
    }
})();

