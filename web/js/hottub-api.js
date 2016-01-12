var HotTubAPI = Class.extend({
    init: function() {
        // Open a web socket with the server
        console.log("Starting Up");
    },
    startUp: function(endpoint, updateLedCallback,
        callOnOpen, callOnClose) {
        this.callOnOpen = callOnOpen;
        this.callOnClose = callOnClose;
        this.connect();
        this.updateLedCallback = updateLedCallback;
        // Bind all the incoming events
        ourCallback = this.updateLeds;
        this.socket.bind('updateLeds', function(led_data) {
            ourCallback(updateLedCallback, led_data);
        });
        this.socket.bind('close', this.close).bind('close', callOnClose);
        this.socket.bind('open', this.open).bind('open', callOnOpen);
    },
    connect: function() {
        this.socket = new FancyWebSocket(endpoint);
    },
    open: function() {
        // Say something about open
        console.log("Socket Opened");
    },
    close: function() {
        // Say something about closing up
        console.log("Socket Closed");
    },
    // Incoming events
    updateLeds: function(updateLedCallback, led_data) {
        updateLedCallback(led_data.temperature, led_data.pump_led, led_data.light_led,
            led_data.heater_led, led_data.heat_led, led_data.temp_led);
    },
    // Outgoing events
    pressLightButton: function() {
        console.log("Light Button Pressed");
        this.socket.send('pressLightButton');
    },
    refresh: function() {
        console.log("Refresh Data");
        this.socket.send('refresh');
    },
    pressPumpButton: function() {
        console.log("Pump Button Pressed");
        this.socket.send('pressPumpButton');
    },
    pressTempUpButton: function() {
        console.log("Temp Up Button Pressed");
        this.socket.send('pressTempUpButton');
    },
    pressTempDownButton: function() {
        console.log("Temp Down Button Pressed");
        this.socket.send('pressTempDownButton');
    }
});
    