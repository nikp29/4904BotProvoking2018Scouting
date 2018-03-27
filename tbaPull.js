function reqListener () {
  var requestResponse = this.responseText;
  var json = JSON.parse(requestResponse);
  var nextMatch = null; //This is the object we'll push data from
  var matchList = []
  var i;
  for (i = 0; i < json.length; i++){
	  if (json[i]['comp_level'] == "qm"){
	  	matchList.push(json[i]);
	  }
  }
  matchList.sort(function(a, b) {
    return parseInt(a['match_number']) - parseInt(b['match_number']);
});
  var i2;
  for (i2 = 0; i2 < matchList.length; i2++){
	  //json[i]['match_number'] = json[i2]['match_number'].parseInt();
	  console.log(matchList[i2]['match_number']);
	  if (nextMatch == null){
		  if (matchList[i2]['actual_time'] == "None"){
		  	  nextMatch = matchList[i2];
		  } else if (parseInt(matchList[i2]['match_number']) == matchList.length){
			  nextMatch = matchList[i2];
		  }
	  }
	  
  }

  console.log(nextMatch);
}
var XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;
var oReq = new XMLHttpRequest();
oReq.addEventListener("load", reqListener);
oReq.open("GET", "https://www.thebluealliance.com/api/v3/event/2018cada/matches");
oReq.setRequestHeader('X-TBA-Auth-Key', 'LMeBTtUalhpU7umirIfYv73sWmfSojG5HHRh9cjR7df1JSiLVGOxc5fUx18c6Stp');
oReq.send();
//console.log("hi");
//console.log(oReq.status);
//console.log(oReq.statusText);
