var ws = new WebSocket("ws://" + document.domain + ':' + location.port + "/email/ws");
ws.onmessage = function(event) {
    console.log(event.data);
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}