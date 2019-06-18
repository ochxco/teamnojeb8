function processResponse(json) {
   console.log(json);
   //let syp = json.data[0].attributes.synopsis;
   //console.log(syp);
  //let img_url = json.results[0].image_url;
  //let titles=json.results[0].title;
  //let imageurl = json.data[random].images.original.url;
  //console.log(img_url);
  //console.log(json.data.length);
  if (json.data ==[]){
      $('#images').append('No manga found. Check your spelling.')
  }
  else{
    for (i = 0; i<json.data.length; i++) {
      let img = json.data[i].attributes.posterImage['medium'];
      let titles=json.data[i].attributes.canonicalTitle;
      let synopsis= json.data[i].attributes.synopsis;
      let mangaid=json.data[i].id;
      let mangastring='/manga/'+mangaid;

      $('#images').append('<div class="info"><img src="' + img+' " >'+'<a class= "title" href="'+mangastring+' ">'+titles+'</p></div>');
    }
  //$('#images').append('<img src="' + img_url+' " >'+'<br>'+titles);
  }
}

function onButtonClick() {
  $('.searchresult').empty();
  $('#images').empty();
  console.log("Button is clicked");

  let searchTerm = $('#searchterm').val();
  console.log(searchTerm);


  let endpointURL='https://kitsu.io/api/edge/manga?page[limit]=20&filter[text]='+
    searchTerm;
  console.log(endpointURL);

  $.get(endpointURL,null,processResponse);
}
function init() {
  $('#clicks').click(onButtonClick);
}


$(document).ready(init);
