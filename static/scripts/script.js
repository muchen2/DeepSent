var upload_div_on = true;
var analysis_div_on = false;
var contact_div_on = false;

function onLoad () {
	$(document).ready (function () {
		setHeaderOnClickEvents ();
		if (!file_uploaded) {
			$(".analysis-header").css ("color", "lightgray");
		} else {
			$(".analysis-body").slideDown ("slow");
			$(".waveform-img").attr ("src", "/waveform_image?" + (new Date()).getTime());
		}
		$(".alert-bar").hide();
	});
}

function setHeaderOnClickEvents () {
	$(document).on ("click", ".upload-header", function () {
			$(".upload-body").slideToggle ("slow", function() {
				upload_div_on = !upload_div_on;
				if (upload_div_on) {
					$(".upload-header").text ("Start with uploading a file  \u25b2");
				} else {
					$(".upload-header").text ("Start with uploading a file  \u25bc");
				}
			});
		}
	);

	$(document).on ("click", ".analysis-header", function () {
			if (file_uploaded) {
				$(".analysis-body").slideToggle ("slow", function() {
					analysis_div_on = !analysis_div_on;
					if (analysis_div_on) {
						$(".analysis-header").text ("Analysis Result  \u25b2");
					} else {
						$(".analysis-header").text ("Analysis Result  \u25bc");
					}
				});
			}
		}
	);

	$(document).on ("click", ".contact-header", function () {
		$(".contact-body").slideToggle ("slow", function () {
			contact_div_on = !contact_div_on;
			if (contact_div_on) {
				$(".contact-header").text ("Contact Info  \u25b2");
			} else {
				$(".contact-header").text ("Contact Info  \u25bc");
			}
		});
	});

	$(document).on ("submit", ".upload-form", function () {
		$(".alert-bar").show ();
		$(".alert-bar").text ("Analyzing...");
		$(".messages").hide ();
		return true;
	});

}