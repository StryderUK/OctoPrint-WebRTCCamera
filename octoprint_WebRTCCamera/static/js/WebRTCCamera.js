/*
 * View model for OctoPrint-WebRTCCamera
 *
 * Author: StryderUK
 * License: AGPLv3
 */
$(function() {
    function WebRTCCameraViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
        self.settings = parameters[0];

        // This will hold the URL currently displayed by the ifram
        self.currentUrl = ko.observable();

        // This will hold the URL entered in the text field
        self.newUrl = ko.observable();

        // This will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL
        self.goToUrl = function() {
            self.currentUrl(self.newUrl());
        }

        // This will be called before the WebRTCCameraViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guarabteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.onBeforeBinding = function() {
            self.newUrl(self.settings.settings.plugins.webrtccamera.url());
            self.goToUrl();
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: WebRTCCameraViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel" /* ", loginStateViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_WebRTCCamera, #tab_plugin_WebRTCCamera, ...
        elements: [ "#tab_plugin_webrtccamera" ]
    });
});
