$(document).ready(function(){

    var colorOn         = "#e91b0f";
    var colorOff        = "#733334";
    var ledRadius = 8;

    var display = new SegmentDisplay("display");
    display.pattern         = "###";
    display.displayAngle    = 6;
    display.digitHeight     = 20;
    display.digitWidth      = 14;
    display.digitDistance   = 2.5;
    display.segmentWidth    = 2;
    display.segmentDistance = 0.3;
    display.segmentCount    = 7;
    display.cornerType      = 3;
    display.colorOn         = colorOn
    display.colorOff        = colorOff
    
    value = '---';
    display.setValue(value);
    
    display.draw();
    
    var pump_led = new LedDisplay("pump_led");
    pump_led.displayRadius = ledRadius
    pump_led.value = 0;
    pump_led.colorOn         = colorOn
    pump_led.colorOff        = colorOff
    pump_led.draw();
    
    var light_led = new LedDisplay("light_led");
    light_led.displayRadius = ledRadius
    light_led.value = 0;
    light_led.colorOn         = colorOn
    light_led.colorOff        = colorOff
    light_led.draw();
    
    var heater_led = new LedDisplay("heater_led");
    heater_led.displayRadius = ledRadius
    heater_led.value = 0;
    heater_led.colorOn         = colorOn
    heater_led.colorOff        = colorOff
    heater_led.draw();
    
    var heat_led = new LedDisplay("heat_led");
    heat_led.displayRadius = ledRadius
    heat_led.value = 0;
    heat_led.colorOn         = colorOn
    heat_led.colorOff        = colorOff
    heat_led.draw();
    
    var temp_led = new LedDisplay("temp_led");
    temp_led.displayRadius = ledRadius
    temp_led.value = 0;
    temp_led.colorOn         = colorOn
    temp_led.colorOff        = colorOff
    temp_led.draw();
    
    // Define the functions that will run!
    var pump_button = new ControlButton("pump_button");
    var light_button = new ControlButton("light_button");
    var tempup_button = new ControlButton("tempup_button");
    var tempdown_button = new ControlButton("tempdown_button");
    
    // Callback led
    var updateLedCallback = function(temp, pump_led_val, light_led_val,
        heater_led_val, heat_led_val, temp_led_val) {
         // This JSON contains led for both the seven segment and lights
        display.setValue(temp);
        pump_led.setValue(pump_led_val);
        light_led.setValue(light_led_val);
        heater_led.setValue(heater_led_val);
        heat_led.setValue(heat_led_val);
        temp_led.setValue(temp_led_val);
    };

    // Create a hot tub client
    endpoint = 'ws://'+window.location.host+'/ws'
    var api = new HotTubAPI();
    
    var callOnOpen = function() {
        $("#status_text").html("Status: Connected");
        api.refresh();
    }
    
    var callOnClose = function() {
        $("#status_text").html("Status: Disconnected");
    }
    
    api.startUp(endpoint, updateLedCallback, callOnOpen, callOnClose);
    
    // Set up the on clicks
    $("#pump_button").click(function() {
        api.pressPumpButton();
    });
    $("#light_button").click(function() {
        api.pressLightButton();
    });
    $("#tempup_button").click(function() {
        api.pressTempUpButton();
    });
    $("#tempdown_button").click(function() {
        api.pressTempDownButton();
    });
});