'use strict';

/* Directives */

var upgradesdirectives = angular.module('upgrades.directives', []);
upgradesdirectives.directive('file', function(){
    return {
        scope: {
            file: '='
        },
        link: function(scope, el, attrs){
            el.bind('change', function(event){
                var files = event.target.files;
                var file = files[0];
                scope.file = file ? file : undefined;
                scope.$apply();
            });
        }
    };
});

// Following directive allows user to upload multiple files using HTML File input
upgradesdirectives.directive('files', function(){
    return {
        scope: {
            files: '='
        },
        link: function(scope, el, attrs){
            el.bind('change', function(event){
                var files = event.target.files;
                scope.files = files;
                scope.$apply();
            });
        }
    };
});

upgradesdirectives.directive('filednd', function(){
    return {
        scope: {
            filednd: '='
        },
        link: function(scope, el, attrs){
            el.bind('dragover', function(event){
            	event.stopPropagation();
            	event.preventDefault();
            	event.dataTransfer.dropEffect = 'copy';
            	scope.$apply();
            });
            el.bind('drop', function(event){
            	event.stopPropagation();
            	event.preventDefault();
                var files = event.dataTransfer.files;
                var file = files[0];
                scope.filednd = file ? file : undefined;
                scope.$apply();
            });
        }
    };
});

upgradesdirectives.directive('displayhoursfromseconds', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attr, ngModel) {

            function fromUser(text) {
                var seconds = parseInt(text) * 3600;
                return seconds;
            }

            function toUser(text) {
                var minutes = parseInt(text) / 3600;
                return minutes;
            }
            ngModel.$parsers.push(fromUser);
            ngModel.$formatters.push(toUser);
        }
    };
});


upgradesdirectives.directive('displaydaysinseconds', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attr, ngModel) {

            function fromUser(text) {
                var seconds = parseInt(text) * 86400;
                return seconds;
            }

            function toUser(text) {
                var minutes = parseInt(text) / 86400;
                return minutes;
            }
            ngModel.$parsers.push(fromUser);
            ngModel.$formatters.push(toUser);
        }
    };
});

upgradesdirectives.directive('autoComplete', function($timeout) {
    return function(scope, iElement, iAttrs) {
            iElement.autocomplete({
                source: scope[iAttrs.uiItems],
                select: function() {
                    $timeout(function() {
                      iElement.trigger('input');
                    }, 0);
                }
            });
    };
});

upgradesdirectives.directive('displaytimefromseconds', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attr, ngModel) {

            function fromUser(text) {
                // value from user looks like "09:21"
                var value = new String(text);
                var split = value.split(":");
                var HH = parseInt(split[0]);
                var mm = parseInt(split[1]);
                var localSeconds = (HH * 3600) + (mm * 60);
                
                // change the seconds to UTC seconds
                var utcOffsetMinutes = new Date().getTimezoneOffset();
                var utcSeconds = localSeconds + (utcOffsetMinutes*60);
                if (utcSeconds < 0) {
                    utcSeconds += (1440*60);
                }
                utcSeconds = utcSeconds % (1440*60);
                
                return utcSeconds;
            }

            function toUser(text) {
                // get stored UTC seconds
                var utcSeconds = parseInt(text);
                var utcOffsetMinutes = new Date().getTimezoneOffset();
                
                // convert UTC seconds to local seconds
                var seconds = utcSeconds + (-1 * utcOffsetMinutes * 60);
                if (seconds < 0) {
                    seconds += (1440*60);
                }
                seconds = seconds % (1440*60);
                
                var iHH = parseInt(seconds / 3600);
                var imm = parseInt(seconds / 60) % 60;
                var HH = new String(iHH);
                var mm = new String(imm);
                if (mm.length < 2) {
                    mm = '0' + mm;
                }
                if (HH.length < 2) {
                    HH = '0' + HH;
                }

                return HH + ':' + mm;
            }
            ngModel.$parsers.push(fromUser);
            ngModel.$formatters.push(toUser);
        }
    };
});

upgradesdirectives.directive('autouppercase', function(uppercaseFilter) {
    return {
        require: 'ngModel',
        link: function(scope, element, attrs, modelCtrl) {
            
            var autouppercase = function(inputValue) {
                var allcaps = "";
                if (typeof inputValue !== 'undefined') {
                    allcaps = inputValue.toUpperCase();
                    if (allcaps !== inputValue) {
                        modelCtrl.$setViewValue(allcaps);
                        modelCtrl.$render();
                    }
                }   
                return allcaps;
            }                        
            modelCtrl.$parsers.push(autouppercase);
            autouppercase(scope[attrs.ngModel]);
        }
    };
});

upgradesdirectives
.constant('dateTimePickerConfig', {
    startView: 'day',
    minView: 'minute',
    minuteStep: 5,
    dropdownSelector: null,
    timeEnabled: function(ngModel, lower, upper) { return true; }
  })
  .constant('dateTimePickerConfigValidation', function (configuration) {
    "use strict";

    var validOptions = ['startView', 'minView', 'minuteStep', 'dropdownSelector'];

    for (var prop in configuration) {
      if (configuration.hasOwnProperty(prop)) {
        if (validOptions.indexOf(prop) < 0) {
          throw ("invalid option: " + prop);
        }
      }
    }

    // Order of the elements in the validViews array is significant.
    var validViews = ['minute', 'hour', 'day', 'month', 'year'];

    if (validViews.indexOf(configuration.startView) < 0) {
      throw ("invalid startView value: " + configuration.startView);
    }

    if (validViews.indexOf(configuration.minView) < 0) {
      throw ("invalid minView value: " + configuration.minView);
    }

    if (validViews.indexOf(configuration.minView) > validViews.indexOf(configuration.startView)) {
      throw ("startView must be greater than minView");
    }

    if (!angular.isNumber(configuration.minuteStep)) {
      throw ("minuteStep must be numeric");
    }
    if (configuration.minuteStep <= 0 || configuration.minuteStep >= 60) {
      throw ("minuteStep must be greater than zero and less than 60");
    }
    if (configuration.dropdownSelector !== null && !angular.isString(configuration.dropdownSelector)) {
      throw ("dropdownSelector must be a string");
    }
  }
)

.directive('datetimepicker', ['dateTimePickerConfig', 'dateTimePickerConfigValidation', function (defaultConfig, validateConfigurationFunction) {
    "use strict";

    return {
      restrict: 'E',
      require: 'ngModel',
      template: "<div class='datetimepicker'>" +
        "<table class='table-condensed' data-container='body' >" +
        "   <thead>" +
        "       <tr>" +
        "           <th class='left'" +
        "               data-ng-click=\"changeView(data.currentView, data.leftDate, false, $event)\"" +
        "               ><i class='icon-arrow-left'/></th>" +
        "           <th class='switch' colspan='5'" +
        "               data-ng-click=\"changeView(data.previousView, data.currentDate, false, $event)\"" +
        ">{{ data.title }}</th>" +
        "           <th class='right'" +
        "               data-ng-click=\"changeView(data.currentView, data.rightDate, false, $event)\"" +
        "             ><i class='icon-arrow-right'/></th>" +
        "       </tr>" +
        "       <tr>" +
        "           <th class='dow' data-ng-repeat='day in data.dayNames' >{{ day }}</th>" +
        "       </tr>" +
        "   </thead>" +
        "   <tbody>" +
        '       <tr data-ng-class=\'{ hide: data.currentView == "day" }\' >' +
        "           <td colspan='7' >" +
        "              <span    class='{{ data.currentView }}' " +
        "                       data-ng-repeat='dateValue in data.dates'  " +
        "                       data-ng-class='{active: dateValue.active, past: dateValue.past, future: dateValue.future, disabled: dateValue.disabled}' " +
        "                       data-ng-click=\"changeView(data.nextView, dateValue.date, dateValue.disabled, $event)\">{{ dateValue.display }}</span> " +
        "           </td>" +
        "       </tr>" +
        '       <tr data-ng-show=\'data.currentView == "day"\' data-ng-repeat=\'week in data.weeks\'>' +
        "           <td data-ng-repeat='dateValue in week.dates' " +
        "               data-ng-click=\"changeView(data.nextView, dateValue.date, dateValue.disabled, $event)\"" +
        "               class='day' " +
        "               data-ng-class='{active: dateValue.active, past: dateValue.past, future: dateValue.future, disabled: dateValue.disabled}' >{{ dateValue.display }}</td>" +
        "       </tr>" +
        "   </tbody>" +
        "</table></div>",
      scope: {
        ngModel: "=ngModel",
        method: "&datetimepickerConfig",
        datetimepickerDropdownSelector: "@",
        pickerClick: "=pickerClick"
      },
      replace: true,
      link: function (scope, element, attrs) {

        var directiveConfig = {};

        if (attrs.datetimepickerConfig) {
        	directiveConfig = scope.method();
          //directiveConfig = scope.$eval(attrs.datetimepickerConfig);
        }
        
        if (scope.datetimepickerDropdownSelector) {
        	directiveConfig['dropdownSelector'] = '#' + scope.datetimepickerDropdownSelector;        		
        }

        var configuration = {};

        angular.extend(configuration, defaultConfig, directiveConfig);

        //validateConfigurationFunction(configuration);

        var dataFactory = {
          year: function (unixDate) {
            var selectedDate = moment.utc(unixDate).startOf('year');
            // View starts one year before the decade starts and ends one year after the decade ends
            // i.e. passing in a date of 1/1/2013 will give a range of 2009 to 2020
            // Truncate the last digit from the current year and subtract 1 to get the start of the decade
            var startDecade = (parseInt(selectedDate.year() / 10, 10) * 10);
            var startDate = moment.utc(selectedDate).year(startDecade - 1).startOf('year');
            var activeYear = (scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).year() : 0;

            var result = {
              'currentView': 'year',
              'nextView': configuration.minView === 'year' ? 'setTime' : 'month',
              'title': startDecade + '-' + (startDecade + 9),
              'leftDate': moment.utc(startDate).subtract(9, 'year').valueOf(),
              'rightDate': moment.utc(startDate).add(11, 'year').valueOf(),
              'dates': []
            };

            
            //console.log("display years");
            for (var i = 0; i < 12; i++) {
              var yearMoment = moment.utc(startDate).add(i, 'years');

        	  var enabled = true;
        	  if (configuration.timeEnabled) {
			    var enabledMoment = moment.utc(yearMoment.valueOf());
			    // include the current month for enabled
			    enabled = configuration.timeEnabled(scope.ngModel, yearMoment.valueOf(), enabledMoment.add(1,'years').valueOf(),result.currentView);
        	  }
              
              var dateValue = {
                'date': yearMoment.valueOf(),
                'display': yearMoment.format('YYYY'),
                'past': yearMoment.year() < startDecade,
                'future': yearMoment.year() > startDecade + 9,
                'active': yearMoment.year() === activeYear,
                'disabled': enabled == false
              };

              result.dates.push(dateValue);
            }

            return result;
          },

          month: function (unixDate) {

            var startDate = moment.utc(unixDate).startOf('year');

            var activeDate = (scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).format('YYYY-MMM') : 0;

            var result = {
              'previousView': 'year',
              'currentView': 'month',
              'nextView': configuration.minView === 'month' ? 'setTime' : 'day',
              'currentDate': startDate.valueOf(),
              'title': startDate.format('YYYY'),
              'leftDate': moment.utc(startDate).subtract(1, 'year').valueOf(),
              'rightDate': moment.utc(startDate).add(1, 'year').valueOf(),
              'dates': []
            };

            //console.log("display months");
            for (var i = 0; i < 12; i++) {
              var monthMoment = moment.utc(startDate).add(i, 'months');
          	  var enabled = true;
        	  if (configuration.timeEnabled) {
			    var enabledMoment = moment.utc(monthMoment.valueOf());
			    // include the current month for enabled
			    enabled = configuration.timeEnabled(scope.ngModel, monthMoment.valueOf(), enabledMoment.add(1,'months').valueOf(),result.currentView);
        	  }
              var dateValue = {
                'date': monthMoment.valueOf(),
                'display': monthMoment.format('MMM'),
                'active': monthMoment.format('YYYY-MMM') === activeDate,
                'disabled': enabled == false
              };

              result.dates.push(dateValue);
            }

            return result;
          },

          day: function (unixDate) {


            var selectedDate = moment.utc(unixDate);
            var startOfMonth = moment.utc(selectedDate).startOf('month');
            var endOfMonth = moment.utc(selectedDate).endOf('month');

            // ToDo: Update to account for starting on days other than Sunday.
            var startDate = moment.utc(startOfMonth).subtract(startOfMonth.day(), 'days');

            var activeDate = (scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).format('YYYY-MMM-DD') : '';

            var result = {
              'previousView': 'month',
              'currentView': 'day',
              'nextView': configuration.minView === 'day' ? 'setTime' : 'hour',
              'currentDate': selectedDate.valueOf(),
              'title': selectedDate.format('YYYY-MMM'),
              'leftDate': moment.utc(startOfMonth).subtract(1, 'months').valueOf(),
              'rightDate': moment.utc(startOfMonth).add(1, 'months').valueOf(),
              'dayNames': [],
              'weeks': []
            };

            for (var dayNumber = 0; dayNumber < 7; dayNumber++) {
              result.dayNames.push(moment.utc().day(dayNumber).format('dd'));
            }

            //console.log("display days");
            for (var i = 0; i < 6; i++) {
              var week = { dates: [] };
              for (var j = 0; j < 7; j++) {
                var monthMoment = moment.utc(startDate).add((i * 7) + j, 'days');
            	var enabled = true;
            	if (configuration.timeEnabled) {
				  var enabledMoment = moment.utc(monthMoment.valueOf());
				  // include the current day for enabled
				  enabled = configuration.timeEnabled(scope.ngModel, monthMoment.valueOf(), enabledMoment.add(1,'days').valueOf(),result.currentView);
            	}
            	var dateValue = {
                  'date': monthMoment.valueOf(),
                  'display': monthMoment.format('D'),
                  'active': monthMoment.format('YYYY-MMM-DD') === activeDate,
                  'past': monthMoment.isBefore(startOfMonth),
                  'future': monthMoment.isAfter(endOfMonth),
                  'disabled': enabled == false
                };
                week.dates.push(dateValue);
              }
              result.weeks.push(week);
            }

            return result;
          },

          hour: function (unixDate) {
            var selectedDate = moment.utc(unixDate).hour(0).minute(0).second(0);

            var activeFormat = (scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).format('YYYY-MM-DD H') : '';

            var result = {
              'previousView': 'day',
              'currentView': 'hour',
              'nextView': configuration.minView === 'hour' ? 'setTime' : 'minute',
              'currentDate': selectedDate.valueOf(),
              'title': selectedDate.format('YYYY-MMM-DD'),
              'leftDate': moment.utc(selectedDate).subtract(1, 'days').valueOf(),
              'rightDate': moment.utc(selectedDate).add(1, 'days').valueOf(),
              'dates': []
            };

            //console.log("display hours");
            for (var i = 0; i < 24; i++) {
              var hourMoment = moment.utc(selectedDate).add(i, 'hours');
				var enabled = true;
				if (configuration.timeEnabled) {
					var enabledMoment = moment.utc(hourMoment.valueOf());
					  // include the current hour for enabled
					enabled = configuration.timeEnabled(scope.ngModel, hourMoment.valueOf(), enabledMoment.add(1,'hours').valueOf(),result.currentView);
				}
              var dateValue = {
                'date': hourMoment.valueOf(),
                'display': hourMoment.format('H:00'),
                'active': hourMoment.format('YYYY-MM-DD H') === activeFormat,
                'disabled': enabled == false
              };

              result.dates.push(dateValue);
            }

            return result;
          },

          minute: function (unixDate) {
            var selectedDate = moment.utc(unixDate).minute(0).second(0);

            var activeFormat = (scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).format('YYYY-MM-DD H:mm') : '';

            var result = {
              'previousView': 'hour',
              'currentView': 'minute',
              'nextView': 'setTime',
              'currentDate': selectedDate.valueOf(),
              'title': selectedDate.format('YYYY-MMM-DD H:mm'),
              'leftDate': moment.utc(selectedDate).subtract(1, 'hours').valueOf(),
              'rightDate': moment.utc(selectedDate).add(1, 'hours').valueOf(),
              'dates': []
            };

            var limit = 60 / configuration.minuteStep;

            //console.log("display minutes");
            for (var i = 0; i < limit; i++) {
              var hourMoment = moment.utc(selectedDate).add(i * configuration.minuteStep, 'minute');

				var enabled = true;
				if (configuration.timeEnabled) {
					var enabledMoment = moment.utc(hourMoment.valueOf());
					// include the current minute period for enabled
					enabled = configuration.timeEnabled(scope.ngModel, hourMoment.valueOf(), enabledMoment.add(configuration.minuteStep,'minutes').valueOf(),result.currentView);
				}

              var dateValue = {
                'date': hourMoment.valueOf(),
                'display': hourMoment.format('H:mm'),
                'active': hourMoment.format('YYYY-MM-DD H:mm') === activeFormat,
                'disabled': enabled == false
              };

              result.dates.push(dateValue);
            }

            return result;
          },

          setTime: function (unixDate) {
            var tempDate = new Date(unixDate);
            scope.ngModel = (new Date(tempDate.getTime() + (tempDate.getTimezoneOffset() * 60000))).getTime();
            if (configuration.dropdownSelector) {
              jQuery(configuration.dropdownSelector).dropdown('toggle');
            }
            return dataFactory[scope.data.currentView](unixDate);
          }
        };

        var getUTCTime = function () {
          var tempDate = ((scope.ngModel != undefined && scope.ngModel != 0) ? moment(new Date(scope.ngModel)).toDate() : new Date());
          return tempDate.getTime() - (tempDate.getTimezoneOffset() * 60000);
        };

        scope.changeView = function (viewName, unixDate, disabled, event) {
          if (event) {
            event.stopPropagation();
            event.preventDefault();
          }

          if (!disabled && viewName && (unixDate > -Infinity) && dataFactory[viewName]) {
            scope.data = dataFactory[viewName](unixDate);
          }
        };

        scope.changeView(configuration.startView, getUTCTime());

        scope.$watch('ngModel', function () {
          scope.changeView(scope.data.currentView, getUTCTime());
        });
        
        scope.$watch('pickerClick', function () {
            scope.changeView('day', getUTCTime());
        });
      }
    };
  }]);