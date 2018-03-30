(function($) {
  "use strict"; // Start of use strict
	
  // Closes the sidebar menu
  $(".menu-toggle").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
	$(".masthead").toggleClass("active");
	$(".footer").toggleClass("active");
    $(".menu-toggle > .fa-bars, .menu-toggle > .fa-times").toggleClass("fa-bars fa-times");
    $(this).toggleClass("active");
  });

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: target.offset().top
        }, 1000, "easeInOutExpo");
        return false;
      }
    }
  });
	
	
  $('#data-reload').click(function(){
	  var oReq = new XMLHttpRequest();
  
	  oReq.addEventListener("load", function(){
		  var requestResponse = this.responseText;
		  var json = JSON.parse(requestResponse);
		  var nextMatch = undefined; //This is the object we'll push data from
		  var matchList = [];
		  var i;
		  for (i = 0; i < json.length; i++){
			  if (json[i]['comp_level'] === "qm"){
				matchList.push(json[i]);
			  }
		  }
		  matchList.sort(function(a, b) {
			return parseInt(a['match_number']) - parseInt(b['match_number']);
		  });
		  var i2;
		  for (i2 = 0; i2 < matchList.length; i2++){
			  //json[i]['match_number'] = json[i2]['match_number'].parseInt();
			  if (nextMatch === undefined){
				  console.log(matchList[i2]['actual_time'])
				  if (matchList[i2]['actual_time'] === "None" || matchList[i2]['actual_time'] === null){
					  nextMatch = matchList[i2];
				  } else if (parseInt(matchList[i2]['match_number']) === matchList.length){
					  nextMatch = matchList[i2];
				  }
			  }

		  }
		  if (nextMatch === undefined){
			  nextMatch=matchList[matchList.length - 1];
		  }
		  
		  $('#red1').text(nextMatch['alliances']['red']['team_keys'][0].substring(3));
		  $('#red2').text(nextMatch['alliances']['red']['team_keys'][1].substring(3));
		  $('#red3').text(nextMatch['alliances']['red']['team_keys'][2].substring(3));
		  $('#blue1').text(nextMatch['alliances']['blue']['team_keys'][0].substring(3));
		  $('#blue2').text(nextMatch['alliances']['blue']['team_keys'][1].substring(3));
		  $('#blue3').text(nextMatch['alliances']['blue']['team_keys'][2].substring(3));
		  $('#match-number').text("Match Number: " + nextMatch['match_number']);
	  });
	  oReq.open("GET", "https://www.thebluealliance.com/api/v3/event/2018casj/matches");
	  oReq.setRequestHeader('X-TBA-Auth-Key', 'LMeBTtUalhpU7umirIfYv73sWmfSojG5HHRh9cjR7df1JSiLVGOxc5fUx18c6Stp');
	  oReq.send();
  });
  // Closes responsive menu when a scroll trigger link is clicked
  $('#sidebar-wrapper .js-scroll-trigger').click(function() {
    $("#sidebar-wrapper").removeClass("active");
	$(".footer").removeClass("active");
	$(".masthead").removeClass("active");
    $(".menu-toggle").removeClass("active");
    $(".menu-toggle > .fa-bars, .menu-toggle > .fa-times").toggleClass("fa-bars fa-times");
  });
	
  
  // Scroll to top button appear
  $(document).scroll(function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });
  

})(jQuery); // End of use strict

// Disable Google Maps scrolling
// See http://stackoverflow.com/a/25904582/1607849
// Disable scroll zooming and bind back the click event
var onMapMouseleaveHandler = function(event) {
  var that = $(this);
  that.on('click', onMapClickHandler);
  that.off('mouseleave', onMapMouseleaveHandler);
  that.find('iframe').css("pointer-events", "none");
}
var onMapClickHandler = function(event) {
  var that = $(this);
  // Disable the click handler until the user leaves the map area
  that.off('click', onMapClickHandler);
  // Enable scrolling zoom
  that.find('iframe').css("pointer-events", "auto");
  // Handle the mouse leave event
  that.on('mouseleave', onMapMouseleaveHandler);
}
// Enable map zooming with mouse scroll when the user clicks the map
$('.map').on('click', onMapClickHandler);
