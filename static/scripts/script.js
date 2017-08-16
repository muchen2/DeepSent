var upload_div_on = true;
var analysis_div_on = false;
var contact_div_on = false;
var analysis_completed = false;

function onLoad () {
	$(document).ready (function () {
		setHeadersOnClickEvents ();
		$(".analysis-header").css ("color", "lightgray");
		$(".alert-bar").hide ();
		if (file_uploaded) {
			$(".alert-bar").text ("Analyzing...");
			$(".alert-bar").show ();
			$.post (url="/analysis", function (data) {
				// post request succeeds
				data_parsed = JSON.parse (data);
				$(".upload-filename").text (data_parsed["filename"]);
				
				$(".tempo-scale").val (data_parsed["pace_score"]);
				$(".tempo-ratio-label").text ("Slow: " + data_parsed["pace_slow_ratio"].toFixed(2) + 
					"%, Mid: " + data_parsed["pace_mid_ratio"].toFixed(2) + "%, Fast: " + data_parsed["pace_fast_ratio"].toFixed(2) + "%");

				$(".arousal-scale").val (data_parsed["arousal_score"]);
				$(".arousal-ratio-label").text ("Relaxing: " + data_parsed["arousal_relaxing_ratio"].toFixed (2) + "% ," + 
					"Neutral: " + data_parsed["arousal_mid_ratio"].toFixed(2) + "% ," + 
					"Intense: " + data_parsed["arousal_intense_ratio"].toFixed(2) + "%");

				$(".valence-scale").val (data_parsed["valence_score"]);
				$(".valence-ratio-label").text ("Sad: " + data_parsed["valence_sad_ratio"].toFixed(2) + "% ," + 
					"Neutral: " + data_parsed["valence_neutral_ratio"].toFixed(2) + "% ," + 
					"Happy: " + data_parsed["valence_happy_ratio"].toFixed(2) + "%");

				$(".best-match").text (data_parsed["best_cand"]);
				$(".sec-best-match").text (data_parsed["sec_best_cand"]);

				$(".analysis-header").css ("color", "#66c2ff");
				setAnalysisHeaderOnClickEvents ();
				$(".analysis-body").slideDown ("slow");
				$(".waveform-img").attr ("src", "/waveform_image?" + (new Date()).getTime());
				$(".alert-bar").hide ()

			}).fail (function () {
				// post request fails
				$(".alert-bar").text ("Unexpected error during analyzing the sound data");
				$(".alert-bar").css ("background", "red");
			});
		}
	});
}

function setHeadersOnClickEvents () {
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
		$(".alert-bar").text ("Uploading...");
		$(".messages").hide ();
		return true;
	});
}

function setAnalysisHeaderOnClickEvents () {
		$(document).on ("click", ".analysis-header", function () {
			$(".analysis-body").slideToggle ("slow", function() {
				analysis_div_on = !analysis_div_on;
				if (analysis_div_on) {
					$(".analysis-header").text ("Analysis Result  \u25b2");
				} else {
					$(".analysis-header").text ("Analysis Result  \u25bc");
				}
			});
		}
	);
}