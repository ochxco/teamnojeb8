function openForm() {
  console.log('Button is clicked')
  $("#myForm").show();
}

function closeForm() {
  console.log('Button is clicked')
  $("#myForm").hide();
}

function onButtonClick() {
  let val= $('#rating').val();
  if (isNaN(val)==true){
    event.preventDefault();
    alert("pls enter a valid no.");
  }
  else if (val ==''){
    event.preventDefault();
    alert("pls enter a valid no.");
  }
  else if (val<0||val>10){
    event.preventDefault();
    alert("pls enter a valid no.");
  }
}

function init() {
  $('.btncancel').click(closeForm);
  $('.open-button').click(openForm);
  $('#submit').click(onButtonClick);

}


$(document).ready(init);
