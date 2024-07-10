// Obtener la URL actual
baseUrl = window.location.href;

// Crear un objeto URL para facilitar el acceso a los parámetros de la URL
currentUrl = new URL(window.location);

// Intentar obtener el parámetro 'url'
urlParam = currentUrl.searchParams.get("url");

// Determinar la URL del contenido basado en la presencia del parámetro 'url'
contentUrl = urlParam ? decodeURIComponent(urlParam) : baseUrl + "main";

fetch(contentUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        const content = document.getElementById('content');
        content.innerHTML = html;
        const scripts = Array.from(content.querySelectorAll("script"));
        if (scripts.length > 0) {
            scripts.forEach(script => {
                const newScript = document.createElement("script");
                Array.from(script.attributes).forEach(attr => {
                    newScript.setAttribute(attr.name, attr.value);
                });
                if (!script.src) {
                    newScript.appendChild(document.createTextNode(script.innerHTML));
                }
                script.parentNode.replaceChild(newScript, script);
            });
        }
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });