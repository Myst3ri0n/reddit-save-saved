$.ajax({url: "/json/subreddits", success: function(result){
ret = result['response'];

if (ret !=undefined){
for (i=0; i<ret.length; i++){
	sub   = ret[i][0];
	menuItem    = '<a class="dropdown-item" href="http://127.0.0.1:5005/r/'+sub+'">'+sub+'</a>';

	$("#sub_drop").append(menuItem);
}}
	
}	
});





function loadModalContent(id) {
	
	$('#imagemodal').show();

	$.ajax({url: "/json/image/"+id, success: function(result)
	{
	ret = result['response'];

	if (ret !=undefined){
	for (i=0; i<ret.length; i++)
	{
		title     = ret[i][0];
		sub       = ret[i][1];
		url       = ret[i][2];
		file_name = ret[i][3];
		perm      = ret[i][4];
		user      = ret[i][5];

		$('#modal_title').html('<a href="'+perm+'" target="_blank">'+title+'</a>');
		$('#posted_by').html('User: <a href="https://reddit.com/u/'+user+'" target="_blank">'+user+'</a>');
		$('#img_body').html('<img src="http://127.0.0.1:5005/static/saved/'+sub+'/'+file_name+'" alt="'+title+'" width="90%" height="90%">');
		$('#sub_reddit').html('Sub: <a href="https://reddit.com/r/'+sub+'" target="_blank">'+sub+'</a>');
		$('#download_link').html('<a href="http://127.0.0.1:5005/static/saved/'+sub+'/'+file_name+'" download>Download Image</a>');




			}
		}
	}	
});




	};

$(function() {

	$('#close').click(function() {
		$('#imagemodal').hide();

		});
		
	});



