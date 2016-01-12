function ControlButton(displayId, action) {
  this.displayId = displayId;
  this.action = action;
  $('#'+displayId).mousedown(function() {
     $(this).fadeTo(0, 0.7);
  });
  $('#'+displayId).mouseup(function() {
     $(this).fadeTo(0, 1.0);
  });
  $('#'+displayId).mouseout(function() {
     $(this).fadeTo(0, 1.0);
  });
};