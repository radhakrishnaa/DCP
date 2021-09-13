'use strict';

var upgradesmodule = angular.module('upgrades', [ 'tlmsAPI', 'restApi', 'ui.bootstrap', 'fileuploader', 'pathAPI', 
	                                              'upgrades.controllers', 'upgrades.directives', 'upgrades.services', 'ui.utils', 'ui.directives', 'StatsService',
                                                  'PublishedPathService', 'googlechart', 'PathDiffService','PollingIntervalService'])
 		.config(function($routeProvider) {
			$routeProvider.when('/paths', {
				controller : 'HomeController',
				templateUrl : 'static/ui/app/partials/home.html',
				activetab : 'paths'
			}).when('/path/edit/:id', {
				controller : 'ListController',
				templateUrl : 'static/ui/app/partials/editpath.html',
				activetab : 'paths'
			}).when('/events', {
				controller : 'DeviceEventsController',
				templateUrl : 'static/ui/app/partials/deviceevents.html',
				activetab : 'events'
			}).when('/mapreports', {
				controller : 'MapReportsController',
				templateUrl : 'static/ui/app/partials/mapreports.html',
				activetab : 'mapreports'
			}).when('/admin', {
				controller : 'AdminController',
				templateUrl : 'static/ui/app/partials/admin.html',
				activetab : 'admin'
			}).when('/lists', {
				controller : 'DeviceListsController',
				templateUrl : 'static/ui/app/partials/devicelists.html',
				activetab : 'lists'
			}).when('/deviceinfo', {
				controller : 'DeviceInfoController',
				templateUrl : 'static/ui/app/partials/deviceinfo.html',
				activetab : 'deviceinfo'
			}).otherwise({
				redirectTo : '/paths' // for labs
				// redirectTo : '/lists' // for production 
			});
		});


