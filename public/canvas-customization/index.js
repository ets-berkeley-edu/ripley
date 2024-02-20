(function(window, $) {
  'use strict';

  var loadCanvasCustomization = function() {
    window.RIPLEY = 'https://ripley.ets.berkeley.edu';

    // Ensure the bCourses development and test servers are pointing to the correct
    // Ripley instance when a copy of production is made
    if (window.location.origin === 'https://ucberkeley.beta.instructure.com') {
      window.RIPLEY = 'https://ripley-dev.ets.berkeley.edu';
    } else if (window.location.origin === 'https://ucberkeley.test.instructure.com') {
      window.RIPLEY = 'https://ripley-qa.ets.berkeley.edu';
    }

    // Load the JavaScript customizations
    $.getScript(window.RIPLEY + '/canvas-customization/canvas-customization.js');

    // Load the CSS customizations
    var css = $('<link>', {
      'rel': 'stylesheet',
      'type': 'text/css',
      'href': window.RIPLEY + '/canvas-customization/canvas-customization.css'
    });
    $('head').append(css);
  };

  if (document.readyState === 'complete' || (document.readyState !== 'loading' && !document.documentElement.doScroll)) {
    loadCanvasCustomization();
  } else {
    document.addEventListener('DOMContentLoaded', loadCanvasCustomization);
  }

})(window, window.$);

/**
 * Load Blue Integration
 */
var BLUE_CANVAS_SETUP={
      connectorUrl:"https://surveys.berkeley.edu/berkeleySurveysblueconnector/",
      canvasAPI:"https://bcourses.berkeley.edu",
      domainName:"com.explorance",
      consumerID:"CWN1RxHsa4vY9b2QgVC7jQ==",
      defaultLanguage:"en-us"
    },
    BlueCanvasJS=document.createElement("script");
BlueCanvasJS.setAttribute("type","text/javascript");
BlueCanvasJS.setAttribute("src","https://surveys.berkeley.edu/berkeleySurveysblueconnector//Scripts/Canvas/BlueCanvas.min.js");
document.getElementsByTagName("head")[0].appendChild(BlueCanvasJS);

////////////////////////////////////////////////////
// DESIGN TOOLS CONFIG                            //
////////////////////////////////////////////////////
// Copyright (C) 2017  Utah State University
var DT_variables = {
        iframeID: '',
        // Path to the hosted USU Design Tools
        path: 'https://designtools.ciditools.com/',
        templateCourse: '1492983',
        // OPTIONAL: Button will be hidden from view until launched using shortcut keys
        hideButton: true,
       // OPTIONAL: Limit by course format
       limitByFormat: false, // Change to true to limit by format
       // adjust the formats as needed. Format must be set for the course and in this array for tools to load
       formatArray: [
            'online',
            'on-campus',
            'blended'
        ],
        // OPTIONAL: Limit tools loading by users role
        limitByRole: false, // set to true to limit to roles in the roleArray
        // adjust roles as needed
        roleArray: [
            'student',
            'teacher',
            'admin'
        ],
        // OPTIONAL: Limit tools to an array of Canvas user IDs
        limitByUser: false, // Change to true to limit by user
        // add users to array (Canvas user ID not SIS user ID)
        userArray: [
            '1234',
            '987654'
        ]
};

// Run the necessary code when a page loads
$(document).ready(function () {
    'use strict';
    // This runs code that looks at each page and determines what controls to create
    $.getScript(DT_variables.path + 'js/master_controls.js', function () {
        console.log('master_controls.js loaded');
    });
});
////////////////////////////////////////////////////
// END DESIGN TOOLS CONFIG                        //
////////////////////////////////////////////////////

/* ALLY */

/**
 * Load custom Ally JavaScript
 */

window.ALLY_CFG = {
 'baseUrl': 'https://prod.ally.ac',
 'clientId': 2,
 'lti13Id': '10720000000000611'
};
$.getScript(ALLY_CFG.baseUrl + '/integration/canvas/ally.js');

/* end Ally customization */
