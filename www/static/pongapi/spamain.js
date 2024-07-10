baseUrl = window.location.href;
currentUrl = new URL(window.location);
urlParam = currentUrl.searchParams.get("url");
contentUrl = urlParam ? decodeURIComponent(urlParam) : baseUrl + "pongapi/main";
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