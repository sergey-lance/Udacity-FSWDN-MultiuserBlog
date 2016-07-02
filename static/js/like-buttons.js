$(function(){
	$(".like-button").click(function() {
		
		disabled = $(this).hasClass('disabled')
		this.is_up = $(this).hasClass('like-button-up')
		
		if (disabled) {
			return false;
		} 
		
		elm_score = $(this).siblings(".like-score")[0] //.innerTexts
		elm_opposite_btn = $(this).siblings(".like-button")[0]
		
		if (typeof elm_score.initial_value === 'undefined') {
			score = parseInt(elm_score.innerText)
			elm_score.initial_value = score
			
			//fix: if already voted:
			opposite_disabled = $(elm_opposite_btn).hasClass('disabled')
			if (disabled) {
				elm_score.initial_value += (this.is_up)?-1:1
			} 
			else if (opposite_disabled) {
				elm_score.initial_value += (this.is_up)?1:-1
			}
			//~ console.log('set_initial to %d', elm_score.initial_value)
		}
	
		this.elm_score = elm_score
		this.elm_opposite_btn = elm_opposite_btn
		
		var that = this
		
		$.ajax({
			type: "GET",
			url: this.href,
			cache: false,
			timeout: 1000,
			success: function(data){
				$(that).addClass('disabled')
				$(that.elm_opposite_btn).removeClass('disabled')
				
				initial_score = that.elm_score.initial_value
				new_score = initial_score + ((that.is_up)?1:-1)
				that.elm_score.innerText = new_score
			},
			error: function(xhr, status, err){
				if (status == 'timeout') {
					//~ location.href = that.href //redirect
				}
			}
		});
		
		//~ $(elm_opposite).removeClass('disabled')
		
		
		return false; //prevent onclick
		});
});
