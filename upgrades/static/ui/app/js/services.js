'use strict';

/* Services */


// don't forget to declare this service module as a dependency in your main app constructor!
var appServices = angular.module('upgrades.services', []);

appServices.factory('alertService', function($rootScope) {
    var alertService = {};

    // create an array of alerts available globally
    $rootScope.alerts = [];

    alertService.add = function(type, msg, closeothers) {
        if(typeof closeothers === "undefined" || closeothers == true) {
            alertService.closeAllAlerts();
        }
        $rootScope.alerts.push({'type': type, 'msg': msg});
    };

    alertService.closeAlert = function(index) {
        $rootScope.alerts.splice(index, 1);
    };
    
    alertService.closeAllAlerts = function() {
        $rootScope.alerts.splice(0);
    };

    return alertService;
});

// Copied from: http://weblogs.asp.net/dwahlin/archive/2013/08/19/building-an-angularjs-dialog-service.aspx
appServices.service('dialogService', ['$dialog', 
    function ($dialog) {

        var dialogDefaults = {
            backdrop: true,
            keyboard: true,
            backdropClick: true,
            dialogFade: true,
            templateUrl: 'static/ui/app/partials/dialog.html'
        };

        var dialogOptions = {
            closeButtonText: 'Close',
            actionButtonText: 'OK',
            headerText: 'Proceed?',
            bodyText: 'Perform this action?'
        };

        this.showModalDialog = function (customDialogDefaults, customDialogOptions) {
            if (!customDialogDefaults) customDialogDefaults = {};
            customDialogDefaults.backdropClick = false;
            this.showDialog(customDialogDefaults, customDialogOptions);
        };

        this.showDialog = function (customDialogDefaults, customDialogOptions) {
            //Create temp objects to work with since we're in a singleton service
            var tempDialogDefaults = {};
            var tempDialogOptions = {};

            //Map angular-ui dialog custom defaults to dialog defaults defined in this service
            angular.extend(tempDialogDefaults, dialogDefaults, customDialogDefaults);

            //Map dialog.html $scope custom properties to defaults defined in this service
            angular.extend(tempDialogOptions, dialogOptions, customDialogOptions);

            if (!tempDialogDefaults.controller) {
                tempDialogDefaults.controller = function ($scope, dialog) {
                    $scope.dialogOptions = tempDialogOptions;
                    $scope.dialogOptions.close = function (result) {
                        dialog.close(result);
                    };
                    $scope.dialogOptions.callback = function () {
                        dialog.close();
                        customDialogOptions.callback();
                    };
                }
            }

            var d = $dialog.dialog(tempDialogDefaults);
            d.open();
        };

        this.showMessage = function (title, message, buttons) {
            var defaultButtons = [{result:'ok', label: 'OK', cssClass: 'btn-primary'}];
            var msgBox = new $dialog.dialog({
                dialogFade: true,
                templateUrl: 'template/dialog/message.html',
                controller: 'MessageBoxController',
                resolve:
                        {
                            model: function () {
                                return {
                                    title: title,
                                    message: message,
                                    buttons: buttons == null ? defaultButtons : buttons
                                };
                            }
                        }
            });
            return msgBox.open();
        };

    }]);


