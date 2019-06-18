function openForm() {
  console.log('Button is clicked')
  $("#myForm").show();
}

function closeForm() {
  console.log('Button is clicked')
  $("#myForm").hide();
}
function CheckDecimal(inputtxt) {
  var decimal=  /^[+]?[0-9]+\.[0-9]+$/;
  if(inputtxt.match(decimal)) {
    if (inputtxt<0||inputtxt>10){
      event.preventDefault();
      alert("pls enter a valid no.")
      return false;
    }
    else{
      return true;}
  }
  else{
    event.preventDefault();
    alert("pls enter a valid no.")
    return false;
  }
}
function onButtonClick() {
  let val= $('#rating').val();
  CheckDecimal(val);
}
function init() {
  $('.btncancel').click(closeForm);
  $('.open-button').click(openForm);
  $('#submit').click(onButtonClick);

}


$(document).ready(init);
