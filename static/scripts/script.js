/*
Javascript code controlling the animations and displays of the webpage

   Copyright 2017 Mu Chen

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

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
