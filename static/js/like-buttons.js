/**
 * AJAX code for Like/Dislike buttons.
 * 
 */
$(function(){
	$(".like-button").click(function() {
		disabled = $(this).hasClass('disabled')
		is_up = $(this).hasClass('like-button-up') // true for '+', false for '-'
		
		if (disabled) {
			return false; 
		} 
		
		elm_score = $(this).siblings(".like-score")[0]
		elm_opposite_btn = $(this).siblings(".like-button")[0]
		opposite_disabled = $(elm_opposite_btn).hasClass('disabled')
		
		if (typeof elm_score.initial_value === 'undefined') {
			// remember initial value
			score = parseInt(elm_score.innerText)
			elm_score.initial_value = score
			
			//fix: make correction if user already voted:
			if (disabled) {
				elm_score.initial_value += (is_up) ? -1 : 1
			} 
			else if (opposite_disabled) {
				elm_score.initial_value += (is_up) ? 1 : -1
			}
		}
		
		this.is_up = is_up
		this.elm_score = elm_score
		this.elm_opposite_btn = elm_opposite_btn
		
		var that = this // reference for callbacks
		
		$.ajax({
			type: "GET",
			url: this.href,
			dataType: 'text',
			cache: false,
			timeout: 1000,
			success: function(data){
				$(that).addClass('disabled')
				$(that.elm_opposite_btn).removeClass('disabled')
				
				new_score = that.elm_score.initial_value + ((that.is_up)?1:-1)
				that.elm_score.innerText = new_score
			},
			error: function(xhr, status, err){
				if (status == 'timeout') {
					console.log('redirect')
					//~ location.href = that.href //fallback
				}
			}
		});
		
		return false; //prevent onclick
		});
});
