'use strict';

/* Modules */

var tlmsService = angular.module('tlmsAPI',[]);

tlmsService.factory("TlmsService", function($http){	
			var factory = {};
			
			factory.clearListEntries = function(listid, success){
				return $http({
		            url: '/tlmsclearlistentries?listid='+listid,
		            method: 'GET'		           
		        });
			};
			
			factory.addEntriesToList = function(item){
				return $http({
		        	url: '/tlmsuploadlist/?listid='+item.listid,
		        	method: 'POST',
		            data: item.listEntriesFile
		        });
			};
			
	return factory;
	
});

angular.module('restApi', [ 'ngResource' ]).factory('Paths',
		function($resource) {
			var Factory = $resource('umcontroller/:id', {
				id : '@id',
				format : 'json'
			}, {
				update : {
					method : 'PUT'
				}
			});
			return Factory;
		}).factory('User', function($resource) {
	var Factory = $resource('usercontroller/:id', {
		id : '@id',
		format : 'json'
	}, {
		update : {
			method : 'PUT'
		}
	});
	return Factory;
});

// File uploader
var fileuploadermodule = angular.module('fileuploader', [ 'upgrades.controllers' ]);

fileuploadermodule.factory('uploadService', ['$rootScope', '$http', function ($rootScope, $http) {

 return {
     send: function (files) {
         var xhr  = new XMLHttpRequest();

         // When the request starts.
         xhr.onloadstart = function () {
             console.log('Factory: upload started: ', file.name);
             $rootScope.$emit('upload:loadstart', xhr);
         };

         // When the request has failed.
         xhr.onerror = function (e) {
             $rootScope.$emit('upload:error', e);
         };

         // When the request starts.
         xhr.onprogress = function () {
             console.log('Factory: upload progress for ', file.name);
             $rootScope.$emit('upload:progress', xhr);
         };

         // When the request starts.
         xhr.onabort = function () {
             console.log('Factory: upload aborted for ', file.name);
             $rootScope.$emit('upload:abort', xhr);
         };

         // When the request starts.
         xhr.onloadend = function () {
             console.log('Factory: upload finished for ', file.name);
             $rootScope.$emit('upload:loadend', xhr);
         };
         
         var payload = new FormData();
         // populate payload
         if (files[0].type == 'text/xml') {
             payload.append("xml", files[0]);
             payload.append("binary", files[1]);
         } else {
             payload.append("xml", files[1]);
             payload.append("binary", files[0]);
         }
         $http.post('http://' + window.location.host + '/uploadbinary/', 
                    payload, {
                        headers: { 'Content-Type': false },
                        transformRequest: function(data) { return data; }
                    });
         }
 };

}]);

//python config for default polling interval (pollAfter)
angular.module('PollingIntervalService', [ 'ngResource' ]).
    factory('pollInterval',
		    function($resource) {
    	 var Factory = $resource('defaultpollinginterval', {
			    format : 'json'
		    }, {
				update : {
					method : 'GET'
				}
			});
   
         return Factory;
		});
			


// Path CRUD functions along with approval workflow
var pathcrudmodule = angular.module('pathAPI', []);

pathcrudmodule.factory('PathCRUDService', function ($route, $http, $location,alertService) {
    var pcrudservice = {};
    pcrudservice.test = function(param){
		alertService.add('info', "test");

    };
    pcrudservice.save = function(params) {
         this.generic('/savepath/', params);
	 };
	 pcrudservice.post_next_action = function(params) {
         this.generic('/nextaction/', params);
	 };
	 pcrudservice.publish = function(params) {
         this.generic('/publishupgradepath/', params);
	 };
	 pcrudservice.deletepath = function(params) {
		 this.generic('/deletepathandpackage/', params);
	 };
	pcrudservice.generic = function(fragment, params) {
        $http({
            url: fragment,
            data: $.param(params),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            method: 'POST',
        }).success(function(data, status) {
        	if (fragment.indexOf("savepath") >=1) {
        		if(data["error"] == 'DUPLICATE'){
        			alertService.add( 'error', "Save failed! Duplicate upgrade path found." );
        		}
        	} else if (fragment.indexOf("deletepathandpackage") == -1) {
            	$route.reload();
        	} else {
        		$location.path("/upgrades#/paths");
        	}
        });
	};
    return pcrudservice;
});

// Service to grab OTA stats
angular.module('StatsService', [ 'ngResource' ]).
    factory('Stats',
		    function($resource) {
			    var Factory = $resource('stats/guid/:id', {
				    id : '@id',
				    format : 'json'
			    });
                return Factory;
			});


// Service to grab currently published SUP
angular.module('PublishedPathService', [ 'ngResource' ]).
    factory('PublishedPath',
		    function($resource) {
			    var Factory = $resource('publishedpath/:id', {
				    id : '@id',
				    format : 'json'
			    });
                return Factory;
			});


// Path diff functions
var pathdiffmodule = angular.module('PathDiffService', []);

pathdiffmodule.factory('PathDiffService', function ($route, $http, $location, alertService) {
    var service = {};
    service.running = function(params) {
        return $http({
            url: 'diffrunning/',
            data: $.param(params),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            method: 'POST',
        });
	};
    return service;
});

