var ws = new WebSocket("ws://" + document.domain + ':' + location.port + "/email/ws");
ws.onmessage = function(event) {
    console.log(event.data);
};