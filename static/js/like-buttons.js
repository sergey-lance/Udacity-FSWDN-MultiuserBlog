/**
 * AJAX code for Like/Dislike buttons.
 * 
 */
$(function(){
	// init
	$(".like-score").each(function(){
		var initial_value = parseInt(this.innerText)
		var up_btn = $(this).siblings(".like-button-up")[0]
		var down_btn = $(this).siblings(".like-button-down")[0]
		
		// find out the value without our vote
		initial_value -= ($(up_btn).hasClass('voted'))?1:0
		initial_value += ($(down_btn).hasClass('voted'))?1:0
		
		this.up_btn = up_btn
		this.down_btn = down_btn
		this.initial_value = initial_value
		console.log(this.initial_value)
		
		var self = this
		
		this.up = function() {
			self.innerText = self.initial_value + 1
			$(self.up_btn).addClass('voted')
			$(self.down_btn).removeClass('voted')
			history.replaceState(null, document.title, $(self).href_initial)
		};
		
		this.down = function() {
			self.innerText = self.initial_value - 1
			$(self.down_btn).addClass('voted')
			$(self.up_btn).removeClass('voted')
			history.replaceState(null, document.title, $(self).href_initial)
		};
		
		this.clear = function () {
			self.innerText = self.initial_value;
			$(self.up_btn).removeClass('voted')
			$(self.down_btn).removeClass('voted')
			history.replaceState(null, document.title, $(self).href_initial)
		};
		
		
	});
	
	$(".like-button").each(function(){
		this.elm_score = $(this).siblings(".like-score")[0]
		this.href_initial = this.href.replace(/&?vote=[^&]+/, '')
	})
	
	$(".like-button").click(function() {
		var disabled = $(this).hasClass('disabled')
		if (disabled) {
			return false; 
		}
		
		var voted = $(this).hasClass('voted')
		var is_up = $(this).hasClass('like-button-up') // true for '+', false for '-'
		
		
		var href = this.href_initial + '&vote=clear'
		var callback = this.elm_score.clear
		
		if (is_up) {
			if (!voted) {
				callback = this.elm_score.up
				href = this.href_initial + '&vote=up'
			}
		} else {
			if (!voted) {
				callback = this.elm_score.down
				href = this.href_initial + '&vote=down'
			}
		}
		
		$.ajax({
			type: "GET",
			url: href,
			dataType: 'text',
			cache: false,
			timeout: 1000,
			success: callback,
			error: function(xhr, status, err){
				if (status == 'timeout') {
					//~ console.log('redirect')
					location.href = that.href //fallback
				}
			}
		});
		
		return false; //prevent onclick
		});
});
