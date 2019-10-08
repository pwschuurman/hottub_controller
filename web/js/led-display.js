function LedDisplay(displayId) {
  this.displayId       = displayId;
  this.value = 0; // Display is off
  this.displayRadius = 10;
  this.colorOn         = 'rgb(233, 93, 15)';
  this.colorOff        = 'rgb(75, 30, 5)';
};

LedDisplay.prototype.draw = function() {
  var display = document.getElementById(this.displayId);
  if (display) {
    var context = display.getContext('2d');
    if (context) {
        context.beginPath();
        context.arc(this.displayRadius, this.displayRadius, this.displayRadius, 0, 2*Math.PI, false);
        
        var grd=context.createRadialGradient(this.displayRadius,this.displayRadius,this.displayRadius*0.4,this.displayRadius,this.displayRadius,this.displayRadius);
        grd.addColorStop(0,this.colorOn);
        grd.addColorStop(1,this.colorOff);
        context.fillStyle = this.value ? grd : this.colorOff;
        context.fill();

      // finish drawing
      context.restore();
    }
  }
};

LedDisplay.prototype.setValue = function(value) {
  this.value = value;
  this.draw();
};




