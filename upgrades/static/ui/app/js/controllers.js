'use strict';

/* Controllers */


var upgradescontrollers = angular.module('upgrades.controllers', []);
// //////////////////////////////////////////////////////////

var rc = function RootController($rootScope, User, $location, alertService, $route, $http) {
	
    console.log("Loading HomeControllerTethered...");
    
	var getVersion = function() {
		//return "In .... js";
		$http({
        	url: '/static/version',
        	method: 'GET'
        }).
            success(function(data, status) {
                $rootScope.status = status;
                if (data != 'undefined' && data.length == 0) {
                    return "version not found";
                } else {
                	$rootScope.version = data;
                	console.log($rootScope.version);
                }
            }).
            error(function(data, status) {
                console.log(' error in reading version file, status is ' + status);
            })
	}
	getVersion();
	//$rootScope.version = $http.get('/version');
	
	
    function reloadifneeded() {
        $http.get('/version').success(
            function(data) {
                console.log('Comparing new: ' + data + ' to current: ' + $rootScope.version);
                if (data != $rootScope.version) {
                    console.log('Version changed, reloading...');
                    $rootScope.text = "New code has been deployed in server. Click OK to reload and get latest deployed code. " +
                    		"If you are on edit mode, then you will loose any changes that you have not saved."
                    $rootScope.newCodeDeploymentModal($rootScope.text);
                    // Reload on clicking OK
                    //location.reload();
                };
            }
        )
    };

    // https://github.com/angular/angular.js/issues/2348 prevents Angular from calling $http until next digest.
    // Following code is the workaround
    var rootScopeApply = function(someFunc) {
        return function() { $rootScope.$apply(someFunc) }
    }

    // Should stop the version check when tab in not active
    //setInterval(rootScopeApply(reloadifneeded), 20000);
    
    var autopager;
    function startAutopager() {
    	console.log("Starting version check at every 20 seconds ...")
        autopager = window.setInterval(rootScopeApply(reloadifneeded), 20000);
    }
    function stopAutopager() {
    	console.log('Cancelling version check timer ...')
        window.clearInterval(autopager);
    }

    window.addEventListener('focus', startAutopager);    
    window.addEventListener('blur', stopAutopager);
    //focus does not start the timer unless tab is inactive and then active again
    // - so start manually
    startAutopager();
    
    $rootScope.newCodeDeploymentModal = function (text) {
        $rootScope.shouldBeOpen = true;
        $rootScope.reloadString = text;
    };

    $rootScope.closeModal = function () {
        $rootScope.shouldBeOpen = false;
    };

    $rootScope.ok = function () {
        location.reload();
    };
    
    $rootScope.options = {
    	backdropFade: true,
    	dialogFade:true
    };
	
	$rootScope.user = User.get();
	var editorroles = ["S", "A", "C"];
	$rootScope.userCanEdit = function() {
		return editorroles.indexOf($rootScope.user.role) != -1;
	};
	var approverroles = [ "S", "A" ];
	$rootScope.userCanApprove = function() {
		return approverroles.indexOf($rootScope.user.role) != -1;
	};
	
	$rootScope.isSuperuser = function() {
		return $rootScope.user.role == "S";
	};

	$rootScope.isReadonly = function() {
		return $rootScope.user.role == "R";
	};

	$rootScope.closeAlert = alertService.closeAlert; 
	
	$rootScope.isActive = function(tabName) {
		if ($route.current) {
			return $route.current.activetab == tabName;
		} else {
			return false;
		}
	};
    
    $rootScope.showTab = function(tabName) {
        if (tabName == 'lists' || tabName == 'admin') {
            return true;
        } else {
            return true; // return false for production
        }
	};
	
    // timezoneJS.timezone.zoneFileBasePath = 'static/ui/app/tz';
    // timezoneJS.timezone.defaultZoneFile = 'northamerica';
    // timezoneJS.timezone.init();
    // console.log(new timezoneJS.Date(1371837901, 'America/Los_Angeles'));
	
}
//rc.$inject = ['$scope', 'User', '$location', 'alertService'];

// //////////////////////////////////////////////////////////
var hc = function HomeController($scope, $rootScope, Paths, User, $http, $filter, $location, $dialog, alertService) {
    $scope.waitingAnim = true;
    $scope.usecds4jenkins = true;
    $scope.usecds4local = true;
    
    $scope.matchCriteriaList =['hwType',
  	                     	 'androidHwType',
  	                    	 'carrier',
  	                    	 'androidCarrier',
  	                    	 'region',
  	                    	 'androidBuildType',
  	                    	 'androidModel',
  	                    	 'softwareVersion',
  	                    	 'userLanguage'];
  	 
  	
	$scope.paths = Paths.query(
        function () {
            $scope.waitingAnim = false;
        },
        function () {
            $scope.waitingAnim = false;
        }
    );
    $scope.opts = {
        backdrop: true,
        keyboard: true,
        backdropClick: true,
        templateUrl: 'static/ui/app/partials/JenkinsProgress.html',  // OR: template:  t,
        controller: 'JenkinsDialogController'
    };
 
    $scope.upload_pkg = function() {
        var params = {'zipFileUrl': $scope.zipFileUrl, 'userName': $scope.userName, 'apitoken': btoa($scope.apitoken), 'usecds': $scope.usecds4jenkins};
       
        	  params['FingerPrint'] = $scope.fingerPrintJenkinsUrl;
	          angular.forEach($scope.requiredFields,function(object,index){
	                if(object.label!="" && object.value!=""){
	              	params[object.label] = object.value;
	                 }
	          });
        	
           
              angular.forEach($scope.matchCriteria,function(object,index){
                  if(object.label!="" && object.value!=""){
                	  params[object.label] = object.value;
                   }
              });
              
            
	        $http({
	        	url: '/getpackagewithoutxmlfromjenkins/',
	        	data: $.param(params),
	        	headers: {'Content-Type': 'application/x-www-form-urlencoded'},
	        	method: 'POST'
	        }).
	            success(function(data, status) {
	                $scope.status = status;
	                $scope.guid = data.guid;
	                $scope.closeJenkinsDialog();
	                $location.path('/path/edit/' + $scope.guid).replace();
	            }).
	            error(function(data, status) {
	                $scope.closeJenkinsDialog();
	                alertService.add( 'error', data );
	            });
      
	    
        $dialog.dialog($scope.opts).open();
    };
 
    $scope.validateJenkinsParseXmlData=function(){
    	 if($scope.ParseXmlClicked){
	    	if( angular.isUndefined($scope.zipFileUrl) || angular.isUndefined($scope.userName) ||  angular.isUndefined($scope.apitoken)) {
	    		$scope.parseXMLCheckBox=false;
	    		return false;
	    	}
    	 }
    	 return true;
   	}
   
     
     $scope.parsexmlfromJenkinsURL=function(){
     	 $scope.ParseXmlClicked=true;

     	 if( angular.isUndefined($scope.zipFileUrl) || angular.isUndefined($scope.userName) ||  angular.isUndefined($scope.apitoken)) {
    		return false;
    	}
     	var url=$scope.zipFileUrl;
     	var lastThreeLetters=url.slice(url.length - 3,url.length);
     	if (lastThreeLetters=="zip"){
     		 var params = {'zipFileUrl': $scope.zipFileUrl, 'userName': $scope.userName, 'apitoken': btoa($scope.apitoken), 'usecds': $scope.usecds4jenkins};
     	        $http({
     	        	url: '/getxmlfromjenkins/',
     	        	data: $.param(params),
     	        	headers: {'Content-Type': 'application/x-www-form-urlencoded'},
     	        	method: 'POST'
     	        }).
     	            success(function(data, status) {
     	                $scope.status = status;
     	              //  $scope.xml = data;
     	                $scope.closeJenkinsDialog();
     	                console.log('data from jenkins xml: '+data);
     	                $scope.getValue(data);
     	            }).
     	            error(function(data, status) {
     	                $scope.closeJenkinsDialog();
     	                alertService.add( 'error', data);
     	            });
     	        $dialog.dialog($scope.opts).open();
     	      
     	}else{
     		return false;
     	}
     };
     
    
    
    $scope.requiredFields= [
                      {label:'Source',value:''},
                      {label:'Target',value:''},
                    ];
    
	
    $scope.matchCriteria = [
                     {label:'hwType',value:''},
                     {label:'carrier',value:''},
                     {label:'region',value:''}
                   ];

                  
    $scope.AddMatchCriteria = function() {
    	var duplicate=false;
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if(object.label==$scope.myObject.criteria){
    			  duplicate=true;
    		  }
        });	
    	if(!duplicate){
    	  $scope.matchCriteria.push({label:$scope.myObject.criteria,value:""});
    	  $scope.myObject.criteria="";
        }
    };
    
    $scope.ValidateMatchCriteria = function(newCriteriatoAdd) {
    	var duplicate=false;
    	if(newCriteriatoAdd=="" ){
    		return false;
    	}
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if($filter('lowercase')(object.label)==$filter('lowercase')(newCriteriatoAdd)){
    			  duplicate=true;
    			  return false;
    		  }
        });	
    	if(!duplicate){
    	return true;
    	}
    	return false;
    };
    
    
    $scope.isValidCriteria= function(newCriteriatoAdd) {
    	var duplicate=false;
    	
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if($filter('lowercase')(object.label)==$filter('lowercase')(newCriteriatoAdd)){
    			  duplicate=true;
    			  return false;
    		  }
        });	
    	if(!duplicate){
    	return true;
    	}
    	return false;
    };
    
    $scope.deleteMatchCriteria = function(labelToRemove) {
    	  angular.forEach($scope.matchCriteria,function(object,index){
    		  if(object.label==labelToRemove){
    			 $scope.matchCriteria.splice(index,1);
    			  }
          });
    }
    
    
   $scope.validJenkinsUrl = function() {
        
    	if( angular.isUndefined($scope.zipFileUrl) || angular.isUndefined($scope.userName) ||  angular.isUndefined($scope.apitoken)) {
    		return false;
    	}
     
        return true;
    };
    
   $scope.validateJenkisUploadData = function() {
        
    	if( angular.isUndefined($scope.zipFileUrl) || angular.isUndefined($scope.userName) ||  angular.isUndefined($scope.apitoken)) {
    		return false;
    	}
     
        return true;
    };
    
    $scope.ParseXmlClicked=false;
    $scope.ParseXmlForm = function() {
        
    	if( angular.isUndefined($scope.zipFileUrl) || angular.isUndefined($scope.userName) ||  angular.isUndefined($scope.apitoken)) {
    		return false;
    	}
  
	    	///if no value then return false and disable upload button
	        var keepgoing=true;
	        angular.forEach($scope.matchCriteria,function(object,index){
	         if(keepgoing){
	  		  if(object.value==""){
	  			keepgoing=false;
	  		  }
	        }
	  		});
	        
	        if(!keepgoing){
	        	return false;
	        }
	        
	      //if no value then return false and disable upload button
	        angular.forEach($scope.requiredFields,function(object,index){
	    		  if(object.value==""){
	    			  keepgoing=false;
	    		  }
	    		});
	        
	        if(!keepgoing){
	        	return false;
	        }
  
    	return true;
       
    }
    
    

   $scope.getValue=function(Json){
	
	       	  var flex = Json.xmlPath.flex;
	       	 
	       	  var targetVersion=Json.xmlPath.target;
	       	  var hardware=Json.xmlPath.hwType;
	       	  var carrier=Json.xmlPath.carrier;
	       	  var region=Json.xmlPath.region;
	          var fingerprint = Json.xmlPath.fingerprint;
	          $scope.fingerPrintJenkinsUrl=fingerprint;
	          
	       	 if (!angular.isUndefined($scope.requiredFields)) {
	           	  
	       		  $scope.requiredFields[0].value=flex;
	       		  $scope.requiredFields[1].value=targetVersion;
	       		 
	       		  angular.forEach($scope.matchCriteria,function(object,index){
	           		  if(object.label=="hwType"){
	           			  $scope.matchCriteria[index].value=hardware;
	           		  }
	           		  else if(object.label=="carrier"){
	           			  $scope.matchCriteria[index].value=carrier;
	           		  }
	           		  else if(object.label=="region"){
	           			  $scope.matchCriteria[index].value=region;
	           		  }
	       		   
	           	 });
	       	 }
    }
   
}




// the dialog is injected in the specified controller
var tdc = function JenkinsDialogController($rootScope, dialog){
    $rootScope.closeJenkinsDialog = function(){
        dialog.close();
    };
}

// //////////////////////////////////////////////////////////
var dec = function DeviceEventsController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, alertService, $dialog) {
  
    var getCDSurl = function() {
    	console.log(window.location.host);
    	if ((window.location.host).indexOf('localhost') != -1) {
    		// Opening to localhost does not make sense - cannot run two servers on same port
    		// $scope.cdsURL = 'http://localhost:8080/upgrades#/events';
    		$scope.cdsURL = 'https://sup-dev.appspot.com/upgrades#/events';
    	} else if ((window.location.host).indexOf('sdc200.blurdev.com') != -1) {
    		$scope.cdsURL = 'https://sup-staging.appspot.com/upgrades#/events';
    	} else if ((window.location.host).indexOf('qa.blurdev.com') != -1) {
    		$scope.cdsURL = 'https://sup-qa.appspot.com/upgrades#/events';
    	} else if ((window.location.host).indexOf('svcmot.com') != -1) {
    		$scope.cdsURL = 'https://moto-cdsp.appspot.com/upgrades#/events';
    	} else {
    		$scope.cdsURL = 'https://sup-dev.appspot.com/upgrades#/events';
    	}
    }
    
    getCDSurl();
    
}

////////////////////////////////////////////////////////////
var dic = function DeviceInfoController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, alertService, $dialog) {

    $scope.maxSize = 5;
    $scope.deviceIdsPerPage = 10;
    $scope.currentDeviceIds = [];
    
    $scope.getDeviceIDs = function(imei) {
        $http({
        	url: '/deviceevents/?deviceid=' + imei,
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.status = status;
                if (data != 'undefined' && data.length == 0) {
                    alertService.add('error', 'Sorry, devices found for this device');
                    return $scope.deviceIds=null;
                }
                $scope.deviceIds = data;
                $scope.noOfPages = Math.round($scope.deviceIds.length / $scope.deviceIdsPerPage);
                $scope.currentPage = 1;
            }).
            error(function(data, status) {
                console.log(' error gdi call, status is ' + status);
            })
    };
    
    $scope.openDeviceInfoModal = function (deviceId) {
        $scope.shouldBeOpen = true;
        $scope.time=deviceId;
        $scope.deviceInfo = deviceId;
    };

    $scope.closeDeviceInfoModal = function () {
        $scope.shouldBeOpen = false;
    };

    $scope.options = {
    	backdropFade: true,
    	dialogFade:true
    };
    
}

////////////////////////////////////////////////////////////
var map = function MapReportsController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, alertService) {


}

////////////////////////////////////////////////////////////
var adm = function AdminController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, alertService) {


}

// //////////////////////////////////////////////////////////
var dlc = function DeviceListsController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, alertService,TlmsService, $timeout) {
    /*
    $scope.lists = {"lists":[{"created_date":1371489380668,"last_modified_date":1371489380668,"matchtype":"exclusive","param":"serialnumber","context":"blacklist","label":"UPS","listid":"98bdda4b-6bf8-4d71-91d8-030d0c14fd07"},{"created_date":1371252078312,"last_modified_date":1371252078312,"matchtype":"exclusive","param":"serialnumber","context":"blacklist","label":"Chase","listid":"7ba19c18-a424-4b9e-8863-127cb8c131a4"},{"created_date":1371252090093,"last_modified_date":1371252090093,"matchtype":"exclusive","param":"serialnumber","context":"blacklist","label":"Pepsi","listid":"85cad7b6-ecbe-4403-888e-fbb7b74185be"}]};
    */
    
    /*
    $scope.targets = {"targets":[{"created_date":1371489380675,"last_modified_date":1371489380675,"criteria":{"softwareversion":"root","type":"acl"},"context":"blacklist","label":"global blacklist","targetid":"acl.root","lists":["98bdda4b-6bf8-4d71-91d8-030d0c14fd07"]}]};
    */
    
    $scope.tmpLists = {"lists":[]};
    
    $scope.lists = {"lists":[]};
    
    $scope.targets = {"targets":[]};
    
    $scope.preMatchTest = true;
    $scope.match = {};

    $scope.replaceListEntries = function(item){
    	    	
    	TlmsService.clearListEntries(item.listid).    	
	    	success(function(data, status) {
	    		TlmsService.addEntriesToList(item);
	    		$scope.getDeviceLists();
	    	}).
	        error(function(data, status) {
	            alertService.add('warn', 'Error communicating with tlms, status is ' + status + ' refresh your browser and try again');
	            console.log('Error communicating with tlms, status is ' + status);
	        })
    }
    
    $scope.getDeviceLists = function() {
        $http({
        	url: '/tlmslists/',
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.liststatus = status;
                $scope.tmpLists = data;
                // SVCOTA-2727 speedup viewing the lists by updating them right away
                $scope.lists = angular.copy(data);
                $scope.retrievedLists = angular.copy(data);
                $timeout($scope.getDeviceTargets, 1000); // next, get the targets
        }).
            error(function(data, status) {
                $scope.liststatus = status;
                alertService.add('warn', 'Error communicating with tlms, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with tlms, status is ' + status);
        })
    };
    
    $scope.getDeviceTargets = function() {
        $http({
        	url: '/tlmstargets/',
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.targetstatus = status;
                $scope.targets = data;
                $scope.mashListsAndTargets(); // now we have the lists and targets, mash them up
                $scope.lists = angular.copy($scope.tmpLists); // update the display copy in one shot
                // get the list sizes asynchronously to allow immediate user input
                $timeout($scope.updateNextListSize, 1000);
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with tlms, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with tlms, status is ' + status);
        })
    };


    $scope.mapListsInMaster = function(list) {
        var result = list.listid + ':' + list.inMaster;
        return result;
    }

    $scope.removeDeviceList = function(listid) {
        if (!$rootScope.isSuperuser()) {
            alertService.closeAllAlerts();
            alertService.add('error', 'Only a superuser is allowed to delete.');
            console.log('Non-superuser trying to delete a list.');
            return;
        }
        var mapListsInMaster = $scope.lists.lists.map($scope.mapListsInMaster);
        var indexOf = mapListsInMaster.indexOf(listid + ":" + "true");
        var inMaster = false;
        if (indexOf >= 0) {
            inMaster = true;
        }
            
        $http({
        	url: '/tlmsremove/'+listid,
        	method: 'GET'
        }).
            success(function(data, status) {
                // remove from master
                if (inMaster) {
                    $scope.removeDeviceListFromMaster(listid);
                } else {
                    $scope.getDeviceLists(); // refresh
                }
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
        })
    };
    
    $scope.removeDeviceListFromMaster = function(removeListid) {
        // example: '{"criteria":{"softwareversion":"myTarget","type":"acl"},"context":"blacklist","label":"blacklist","lists":["ca11db56-5d40-4008-8ba0-b27349015a54"]}'
        if (!$rootScope.isSuperuser()) {
            alertService.closeAllAlerts();
            alertService.add('error', 'Only a superuser is allowed to manage a master list.');
            console.log('Non-superuser trying to manage a master list.');
            return;
        }
        
        var info = {};
        info.criteria = {};
        info.criteria.softwareversion = 'root';
        info.criteria.type = 'acl';
        
        for (var j=0; j<$scope.targets.targets.length; j++) {
            var targetid = $scope.targets.targets[j].targetid;
            if (targetid == 'acl.root') {
                info.lists = angular.copy($scope.targets.targets[j].lists);
                var index = info.lists.indexOf(removeListid);
                if (index >= 0) {
                    info.lists.splice(index, 1);
                }

                break;
            }
        }
        
        $http({
        	url: '/tlmsupdatetarget/',
        	method: 'POST',
            data: info
        }).
            success(function(data, status) {
                $scope.getDeviceLists(); // refresh
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
        })
    };

    
    $scope.addDeviceListToMaster = function(listid) {
        // example: '{"criteria":{"softwareversion":"myTarget","type":"acl"},"context":"blacklist","label":"blacklist","lists":["ca11db56-5d40-4008-8ba0-b27349015a54"]}'
        if (!$rootScope.isSuperuser()) {
            alertService.closeAllAlerts();
            alertService.add('error', 'Only a superuser is allowed to manage a master list.');
            console.log('Non-superuser trying to manage a master list.');
            return;
        }
        
        var info = {};
        info.criteria = {};
        info.criteria.softwareversion = 'root';
        info.criteria.type = 'acl';
        
        for (var j=0; j<$scope.targets.targets.length; j++) {
            var targetid = $scope.targets.targets[j].targetid;
            // give the acl.root a good label
            if (targetid == 'acl.root') {
                info.lists = angular.copy($scope.targets.targets[j].lists);
                info.lists.push(listid);
                break;
            }
        }
        
        $http({
        	url: '/tlmsupdatetarget/',
        	method: 'POST',
            data: info
        }).
            success(function(data, status) {
                $scope.getDeviceLists(); // refresh
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
        })
    };
    
    $scope.uploadList = function(listid) {
        $http({
        	url: '/tlmsuploadlist/?listid='+listid,
        	method: 'POST',
            data: $scope.devicefile
        }).
            success(function(data, status) {
                alertService.add('info', 'File was uploaded');
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server when uploading file, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server when uploading file, status is ' + status);
        })
    };
    
    
    $scope.showHide = function(lists, currentItem){
    	
    	for (var i=0; i<lists.length; i++) {
    		lists[i].show=false;
        }
    	currentItem.show=true;
    };
    
    $scope.uploadListEntries = function(item) {
    	//var fileName = $scope.$eval('listEntriesFile-'+listId);
        $http({
        	url: '/tlmsuploadlist/?listid='+item.listid,
        	method: 'POST',
            data: item.listEntriesFile
        }).
            success(function(data, status) {
                alertService.add('info', 'Entries of "'+ item.label +'" list were successfully replaced.');
                delete item.listEntriesFile;
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server when uploading file, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server when uploading file, status is ' + status);
        })
    };
    
    $scope.replaceListEntries1 = function(item) {
        alertService.closeAllAlerts();
        var fileName = item.listEntriesFile;
        if (fileName == undefined) {
            alertService.add('error', 'You must select a file to replace');
            return;
        }
        var params = {'listid': $scope.item.listid};
        TlmsFactory.clearListEntries(params);
        
        $http({
            url: '/tlmsclearlistentries/?listid='+item.listid,
            method: 'GET'
            }).
                success(function(data, status) {
                	$scope.uploadListEntries(item);
            }).
                error(function(data, status) {
                    alertService.add('warn', 'Error communicating with tlms, status is ' + status + ' refresh your browser and try again');
                    console.log('Error communicating with tlms, status is ' + status);
            })

    };
    
    
    $scope.addDeviceList = function(name, type, addToMaster) {
 
        alertService.closeAllAlerts();
         
        if ($scope.devicefile == undefined) {
            alertService.add('error', 'You must select a file');
            return;
        }

        if ($scope.devicefile != undefined && $scope.devicefile.size == 0) {
            alertService.add('error', 'You have selected an empty file');
            return;
        }
         
        if (name == undefined || name.length == 0) {
            alertService.add('error', 'Error a name is required');
            return;
         }
                 
        if (type == undefined) {
            type = 'exclusive'; // the check box might appear checked but actually the value is undefined...
        }
        
        // check if name already exists
        for (var i=0; i<$scope.lists.lists.length; i++) {
            if ($scope.tmpLists.lists[i].label == name) {
                alertService.add('error', 'The name \''+name+'\' already exists');
                return;
            }
        }
        
        var info = {};
        info.matchtype = type;
        info.param = 'serialnumber';
        info.context = type;
        info.label = name;
        
        // example: '{"matchtype":"exclusive","param":"serialnumber","context":"blacklist","label":"blacklist"}'
        
         $http({
            url: '/tlmsaddlist/',
            method: 'POST',
            data: info
         }).
             success(function(data, status) {
                $scope.uploadList(data.listid);
                if (addToMaster) {
                    $scope.addDeviceListToMaster(data.listid);
                } else {
                    $scope.getDeviceLists(); // refresh
                 }
         }).
             error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
         })
    };
    ////////
    
    $scope.updateNextListSize = function() {
        for (var i=0; i<$scope.lists.lists.length; i++) {
        	if ($scope.lists.lists[i].size == undefined) {
        		$scope.getListSize($scope.lists.lists[i].listid);
        		break;
        	}
        }
    	
    };
    
    $scope.getListSize = function(listid) {
        $http({
        	url: '/tlmslistsize/?listid='+listid,
        	method: 'GET'
        }).
            success(function(data, status) {
                //alertService.add('info', 'size for list ' + listid + ' is ' + data.size);
                for (var i=0; i<$scope.lists.lists.length; i++) {
                    if (listid == $scope.lists.lists[i].listid) {
                        $scope.lists.lists[i].size = data.size;
                        break;
                    }
                }
                $timeout($scope.updateNextListSize, 1000);
        }).
            error(function(data, status) {
                $scope.targetstatus = status;
                alertService.add('warn', 'Error communicating with list server when getting list size, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server when getting list size, status is ' + status);
                for (var i=0; i<$scope.lists.lists.length; i++) {
                    if (listid == $scope.lists.lists[i].listid) {
                        $scope.lists.lists[i].size = 'unknown';
                        break;
                    }
                }
                
        })
    };
    
    $scope.matchTest = function(serialNumber) {

        alertService.closeAllAlerts();
        
        $scope.match = {};
        $scope.preMatchTest = true;
        
        if (serialNumber == undefined || serialNumber.length == 0) {
            alertService.add('error', 'Error a serial number is required');
            return;
        }
                
        $http({
        	url: '/tlmsmatch/'+serialNumber,
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.match = data;
                $scope.preMatchTest = false;
                $scope.matchFoundInList = "No Targeted List";
                if ($scope.match.reason == 'excluded' && $scope.match.matches == false) {
                    $scope.matchFoundInList = "Master Blacklist";
                } else if ($scope.match.reason == 'included' && $scope.match.matches == true) {
                    $scope.matchFoundInList = "Master Whitelist";
                }
        }).
            error(function(data, status) {
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
        })
    };

    $scope.mashListsAndTargets = function() {
    
        for (var i=0; i<$scope.tmpLists.lists.length; i++) {
            $scope.tmpLists.lists[i].mashupComplete = true;

            $scope.tmpLists.lists[i].iteration = i;
            var listid = $scope.tmpLists.lists[i].listid;
            
            // defaults
            var targets = [];
            var targetNames = '';
            $scope.tmpLists.lists[i].uiAllowRemove = false;
            $scope.tmpLists.lists[i].uiAllowAddToMaster = false;
            $scope.tmpLists.lists[i].uiAllowRemoveFromMaster = false;
            
            if ($scope.tmpLists.lists[i].matchtype == 'exclusive') {
                $scope.tmpLists.lists[i].uiMasterLabel = 'Master Blacklist';
            } else {
                $scope.tmpLists.lists[i].uiMasterLabel = 'Master Whitelist';
            }
            
            var inMaster = false;
            var inTarget = false;
            for (var j=0; j<$scope.targets.targets.length; j++) {
                var targetid = $scope.targets.targets[j].targetid;
                var targetList = $scope.targets.targets[j].lists;
                for (var k=0; k<targetList.length; k++) {
      
                    if (targetList[k] == listid) {
                        // this list is in a tlms target
                        inTarget = true;
                        
                        // default the target label to the label in the tlms target
                        var targetLabel = $scope.targets.targets[j].label;

                        // the root software version, change the label to a global name
                        if (targetid == 'acl.root') {
                            inMaster = true;
                            targetLabel = $scope.tmpLists.lists[i].uiMasterLabel;
                        }
                        
                        // if there is no target label then just use the target software version
                        if (targetLabel == '') {
                            targetLabel = $scope.targets.targets[j].criteria.softwareversion;
                        }
                    
                        targets.push(targetLabel);
                        if (targets.length > 1) {
                            targetNames = targetNames + ', ';
                        }
                        targetNames = targetNames + targetLabel;
                    }

                }
            }

            // SVCOTA-2700 - only allow adding to master blacklist for now
            if ($scope.tmpLists.lists[i].matchtype == 'exclusive') {
	            if (inMaster) {
	                $scope.tmpLists.lists[i].uiAllowRemoveFromMaster = true;
	            } else {
	                $scope.tmpLists.lists[i].uiAllowAddToMaster = true;
	            }
            }
            
            if (!inTarget) {
                // not in any target - safe to remove the list
                $scope.tmpLists.lists[i].uiAllowRemove = true;
            }
            
            $scope.tmpLists.lists[i].inMaster = inMaster;
            
            $scope.tmpLists.lists[i].targets = targets;
            $scope.tmpLists.lists[i].targetNames = targetNames;
            
        }
    
    };

    
    $scope.getDeviceLists();


}


// //////////////////////////////////////////////////////////
var lc = function ListController($scope, $rootScope, Paths, $routeParams, $http, $location, $filter, $route, PathCRUDService, $dialog, alertService, Stats, $timeout,pollInterval,PublishedPath) {
	
	$scope.defaultPollingInterval=1;
	$scope.DefaultPollInterval=pollInterval.get(
        function () {
        	if ($scope.DefaultPollInterval.di==86400){
        		$scope.defaultPollingIntervalText="Once a day";
        	}
        	else if ($scope.DefaultPollInterval.di==3601){
        		$scope.defaultPollingIntervalText="Once every hour";
        	}
        	else if($scope.DefaultPollInterval.di==360){
        		$scope.defaultPollingIntervalText="Once every six minutes";
        	}else {
        		$scope.defaultPollingIntervalText=$scope.DefaultPollInterval.di +" seconds";
        	}
        	$scope.defaultPollingInterval=$scope.DefaultPollInterval.di;
	    console.log('DefaultPolling Interval from python config: '+ $scope.DefaultPollInterval.di);
		$scope.pollingIntervalOptions =['4 Times a day',
		                          '2 Times a day', 
		                          'Once a day', 
		                          'Once every 2 days', 
		                          'Once every 3 days', 
		                          'Once every 4 days', 
		                          'Once every 5 days', 
		                          'Once every 6 days',
		                          'Once every 7 days',
		                          'default "'+$scope.defaultPollingIntervalText+'"' ];
	   }
    );
    
	 $scope.matchCriteriaList =['hwType',
	  	                     	 'androidHwType',
	  	                    	 'carrier',
	  	                    	 'androidCarrier',
	  	                    	 'region',
	  	                    	 'androidBuildType',
	  	                    	 'androidModel',
	  	                    	 'softwareVersion',
	  	                    	 'userLanguage'];
	 
	
	
	 $scope.SECS_IN_DAY='86400';
    
	$scope.templateOptions =[
	                         'Custom',
	                         'Verizon post-paid, mandatory, Wi-Fi+Cellular package',
	                         'Verizon post-paid, mandatory, WiFi Only package',
	                         'Verizon post-paid, optional, Wi-Fi+Cellular package',
	                         'Verizon post-paid, optional, WiFi Only package',
	                         'Verizon pre-paid, mandatory, WiFi Only package',
	                         'Verizon pre-paid, optional, WiFi Only package',
	                         'ROW, mandatory, Wi-Fi Only package',
	                         'ROW, mandatory, Wi-Fi+Cellular package',
	                         'ROW, optional, Wi-Fi Only package',
	                         'ROW, optional, Wi-Fi+Cellular package'];
	
	
    $scope.pollingIntervalUpdate = function(pollingInterval){
    
    	switch (pollingInterval) {
    	case $scope.pollingIntervalOptions[0]:
    			$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY/4;
    		    break;
        case $scope.pollingIntervalOptions[1]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY/2;
	            break;
        case $scope.pollingIntervalOptions[2]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY;
	            break;
        case $scope.pollingIntervalOptions[3]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*2;
                break;
        case $scope.pollingIntervalOptions[4]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*3;
                break;
        case $scope.pollingIntervalOptions[5]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*4;
                break;
        case $scope.pollingIntervalOptions[6]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*5;
                break;
        case $scope.pollingIntervalOptions[7]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*6;
                break;
        case $scope.pollingIntervalOptions[8]:
            	$scope.path.upgradePath.pollingInterval=$scope.SECS_IN_DAY*7;
                break;
        case $scope.pollingIntervalOptions[9]:
        		$scope.path.upgradePath.pollingInterval=$scope.defaultPollingInterval;
        		break;        
       }
    };
	
	
	$scope.sourceUpdate=function(){		
		$scope.path.metaData.minVersion=$scope.path.upgradePath.sourceVersion;    		
    };
    
    $scope.setUiWorkflow=function(triggeredby,forced,wifionly,showPreDownloadDialog,showDownloadOptions,preDownloadNotificationExpiryMins,preInstallNotificationExpiryMins){
    	$scope.path.metaData.uiWorkflowControl[triggeredby].wifionly= String(wifionly)=='true';
    	$scope.path.metaData.uiWorkflowControl[triggeredby].forced=String(forced)=='true';
    	$scope.path.metaData.uiWorkflowControl[triggeredby].showPreDownloadDialog=String(showPreDownloadDialog)=='true';
    	$scope.path.metaData.uiWorkflowControl[triggeredby].showDownloadOptions=String(showDownloadOptions)=='true';    	
    	$scope.path.metaData.uiWorkflowControl[triggeredby].preDownloadNotificationExpiryMins=preDownloadNotificationExpiryMins;
    	$scope.path.metaData.uiWorkflowControl[triggeredby].preInstallNotificationExpiryMins=preInstallNotificationExpiryMins;
    };
    
   
    $scope.copyDefaultToTemplate=function(){    	
    	for (var i in $scope.path.metaData.uiWorkflowControl){
    		$scope.setUiWorkflow(
    				i,
    				$scope.path.metaData.forced,
    				$scope.path.metaData.wifionly,
    				$scope.path.metaData.showPreDownloadDialog,
    				$scope.path.metaData.showDownloadOptions,
    				$scope.path.metaData.preDownloadNotificationExpiryMins,
    				$scope.path.metaData.preInstallNotificationExpiryMins
    		);  
    	}
    };
    
    $scope.uiworkflowUpdate = function(){
    	
    	
    	switch ($scope.path.uploadInfo.templatename) {
    	case $scope.templateOptions[0]:
    		if($scope.orig_templatename=="Custom"){
    			$scope.path.metaData.uiWorkflowControl= angular.copy($scope.path.metaData_orig.uiWorkflowControl);  	
    		} else {
    			$scope.copyDefaultToTemplate();
    		}    		
    		break;
        case $scope.templateOptions[1]:
        	$scope.setUiWorkflow("polling",true,false,false,false,1440,1440);  
        	$scope.setUiWorkflow("setup",true,false,false,false,1440,1440);  
        	$scope.setUiWorkflow("notification",true,false,false,false,1440,1440);  
        	$scope.setUiWorkflow("user",false,false,true,false,1440,1440);  
        	break;
        case $scope.templateOptions[2]:
        	$scope.setUiWorkflow("polling",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,false,true,false,1440,1440);  
        	break;
        case $scope.templateOptions[3]:
        	$scope.setUiWorkflow("polling",false,false,true,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",false,false,true,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",false,false,true,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,false,true,false,1440,1440); 
        	break;
        case $scope.templateOptions[4]:
        	$scope.setUiWorkflow("polling",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,false,true,false,1440,1440);    
        	break;
        case $scope.templateOptions[5]:
        	$scope.setUiWorkflow("polling",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",true,true,false,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,true,true,false,1440,1440);    
        	break;
        case $scope.templateOptions[6]:
        	$scope.setUiWorkflow("polling",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,true,true,false,1440,1440); 
        	break;
        case $scope.templateOptions[7]:
        	$scope.setUiWorkflow("polling",true,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",true,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",true,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("user",true,true,true,false,1440,1440);  
        	break;
        case $scope.templateOptions[8]:
        	$scope.setUiWorkflow("polling",true,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("setup",true,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("notification",true,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("user",true,false,true,true,1440,1440);   
        	break;
        case $scope.templateOptions[9]:
        	$scope.setUiWorkflow("polling",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("setup",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("notification",false,true,true,false,1440,1440);  
	    	$scope.setUiWorkflow("user",false,true,true,false,1440,1440);    
        	break;
        case $scope.templateOptions[10]:
        	$scope.setUiWorkflow("polling",false,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("setup",false,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("notification",false,false,true,true,1440,1440);  
	    	$scope.setUiWorkflow("user",false,false,true,true,1440,1440); 
        	break;
    }
    	
    }
    
    $scope.autoRefreshStats = false; // Refresh stats automatically?
    $scope.statsRefreshInterval = 60; // Refresh stats every so many minutes
    $scope.autoRefresh = function() { 
        $scope.refreshTimer = $timeout($scope.autoRefresh, $scope.statsRefreshInterval * 60 * 1000);
        $scope.stats = Stats.get({id : $scope.path.guid});
        $scope.statsLastMod = new Date();
    };

    $scope.toggleStatsAutoRefresh = function() {
        if ($scope.autoRefreshStats == true) {
            $scope.autoRefresh();
        } else {
            $timeout.cancel($scope.refreshTimer);
        };
    };

	$scope.path = Paths.get({
		id : $routeParams.id
	}, function() {
	
	    function epoch2utc(epoch) {
	        // Convert Unix epoch to GMT date string
	        if (typeof(epoch) == 'string') {
	            epoch = parseInt(epoch);
	        }
	        if (epoch > 0) {
	            var d = new Date(epoch);
	            return d ?  '"' + d.toUTCString() + '"' : '';  // use quotes to escape the embedded comma
	        }
	        return '';
	    }
	    
        $scope.getListOfNotifiedDevice = function() {
			
		 $scope.opts = {
			        backdrop: true,
			        keyboard: true,
			        backdropClick: true,
			        templateUrl: 'static/ui/app/partials/ExportListProgress.html',  // OR: template:  t,
			        controller: 'JenkinsDialogController'
		};
			
	    var params = {'guid' : $scope.path.guid ,'state':'Notified'};
       	var contenttest="";
       	$http({
                url: '/getdeviceeligibleforupgrade/',
	             method: 'GET',
           	 params: params
	         }).
           success(function(data, status) {
               $scope.status = status;
               console.log("in success of getdeviceeligibleforupgrade ");
               if(data==""){
            	   alertService.add( 'error', "No data found for Notified device list" );
               }else {
	               var blobdata = new Blob([data],{type : 'text/csv'});
	               var link = document.createElement("a");
	               link.setAttribute("href", window.URL.createObjectURL(blobdata));
	               link.setAttribute("download", "Data.csv");
	               link.click();
               }
              
               $scope.closeJenkinsDialog();
           }).
           error(function(data, status) {
               console.log(' error in osm eligible device call, status is ' + status);
               $scope.closeJenkinsDialog();
               alertService.add( 'error', "No data found for Notified device list" );
           })
           $dialog.dialog($scope.opts).open();
      };
      
      $scope.getListOfFailureDevice = function() {
	    	
	     $scope.opts = {
		        backdrop: true,
		        keyboard: true,
		        backdropClick: true,
		        templateUrl: 'static/ui/app/partials/ExportListProgress.html',  // OR: template:  t,
		        controller: 'JenkinsDialogController'
		 };   
   	   
	    var params = {'guid' : $scope.path.guid ,'state':'Result_FAILED','type':'current'};
      	var contenttest="";
      
      	$http({
               url: '/getdeviceeligibleforupgrade/',
	             method: 'GET',
          	 params: params
	        }).
           success(function(data, status) {
               $scope.status = status;
               console.log("in success of getdeviceeligibleforupgrade ");
               if(data==""){
            	   alertService.add( 'error', "No data found for Result_FAILED device list" );
               }else {
	               var blobdata = new Blob([data],{type : 'text/csv'});
	               var link = document.createElement("a");
	               link.setAttribute("href", window.URL.createObjectURL(blobdata));
	               link.setAttribute("download", "Data.csv");
	               link.click();
               }
               $scope.closeJenkinsDialog();
               
           }).
           error(function(data, status) {
               console.log(' error in osm eligible device call, status is ' + status);
               $scope.closeJenkinsDialog();
               alertService.add( 'error', "No data found for Result_FAILED device list" );
           })
           $dialog.dialog($scope.opts).open();
     };
     
      
       
		if ($scope.path.metaData.uiWorkflowControl == undefined) {
	    	$scope.path.metaData.uiWorkflowControl = {};
	    	$scope.path.metaData.uiWorkflowControl.polling = {};
	    	$scope.path.metaData.uiWorkflowControl.user = {};
	    	$scope.path.metaData.uiWorkflowControl.notification = {};
	    	$scope.path.metaData.uiWorkflowControl.setup = {};	
	    }
		var triggeredByOptions = ['polling','user', 'notification', 'setup'];
		for(var i=0; i<triggeredByOptions.length; i++ ){
			if($scope.path.metaData.uiWorkflowControl[triggeredByOptions[i]] == undefined){
				$scope.path.metaData.uiWorkflowControl[triggeredByOptions[i]]={};
			}
		}
		
		if($scope.path.uploadInfo == undefined){
			$scope.path.uploadInfo = {};
			$scope.path.uploadInfo.templatename="Custom";
		} else {
			$scope.orig_templatename= $scope.path.uploadInfo.templatename;
		}

		if(!angular.isUndefined($scope.path.upgradePath)) {
			if(angular.isUndefined($scope.path.upgradePath.pollingInterval) || $scope.path.upgradePath.pollingInterval==""){
				$scope.path.upgradePath.pollingInterval=$scope.DefaultPollInterval.di;
			}
		}
		
		if(angular.isUndefined($scope.pollingInterval) && angular.isDefined($scope.pollingIntervalOptions)){

			var secondsInaDay=$scope.SECS_IN_DAY;
				switch ($scope.path.upgradePath.pollingInterval) {
				
		    	case secondsInaDay/4:
		    	        $scope.pollingInterval=$scope.pollingIntervalOptions[0];
		    		    break;
		        case secondsInaDay/2:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[1];
		        		break;
		        case $scope.defaultPollingInterval*1:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[9];
		        		break;
		        case secondsInaDay*1:
		                $scope.pollingInterval=$scope.pollingIntervalOptions[2];
			            break;
		        case secondsInaDay*2:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[3];
		                break;
		        case secondsInaDay*3:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[4];
		                break;
		        case secondsInaDay*4:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[5];
		                break;
		        case secondsInaDay*5:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[6];
		                break;
		        case secondsInaDay*6:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[7];
		                break;
		        case secondsInaDay*7:
		        		$scope.pollingInterval=$scope.pollingIntervalOptions[8];
		                break;
		       }
			
		}
		
		
		
        $scope.newCriteria = "";
		$scope.deleteCriteria = function(labelToDelete) {
			delete $scope.path.upgradePath.match[labelToDelete];
            return;
		};
	    $scope.isCriteriaValid = function() {
            return !($scope.newCriteria in $scope.path.upgradePath.match)
	    };
	    
	    $scope.validateCriteria = function() {
            return !(angular.isUndefined($scope.newCriteria) || ($scope.newCriteria == "") || ($scope.newCriteria in $scope.path.upgradePath.match))
	    };
		
	    $scope.addCriteria = function() {
            if (!$scope.validateCriteria()) {
                return;
            }
            $scope.path.upgradePath.match[$scope.newCriteria] = "";
            $scope.newCriteria = "";
            return;
	    };
	    
	    if(!angular.isUndefined($scope.path.guid))  {
	    	 
	    	$scope.pathdiff = PublishedPath.get({
	           id: $scope.path.guid
	       }, function(data, status, headers, config) {
	          $rootScope.isPublishedPackage=true;
	           return;
	       }, function(data, status, headers, config) {
	           if (data.status == 404) {
	              $rootScope.isPublishedPackage=false;
	           }
	           return;
	       }); 
	   	
	   	}


		  
        $rootScope.editAllowed = $scope.path.upgradePath.approval_state == 'NEWVERSION';
		// store the original version of the metadata SVCOTA-2728
		$scope.path.metaData_orig = angular.copy($scope.path.metaData);
		
        $scope.stats = Stats.get({id : $scope.path.guid});
        $scope.toggleStatsAutoRefresh();
        $scope.statsLastMod = new Date();
       // $scope.copyDefaultToTemplate();
        $scope.chart = {
            "type": "ColumnChart",
            "displayed": true,
            "data": {
                "cols": [
                    {"id": "date", "label": "Date", "type": "number"},
                    {"id": "upgraded", "label": "Upgraded", "type": "number"},
                    {"id": "At Source", "label": "At Source", "type": "number"},
                    {"id": "", "role": "tooltip", "type": "string", "p": {"role": "tooltip", "html": true}}
                ],
                "rows": [
                    {
                        "c": [
                            {"v": "January"},
                            {"v": 19, "f": "42 items"},
                            {"v": 12, "f": "Ony 12 items"},
                            {"v": " <b>Shipping 4</b><br /><img src=\"http://icons.iconarchive.com/icons/antrepo/container-4-cargo-vans/512/Google-Shipping-Box-icon.png\" style=\"height:85px\" />", "p": {}}
                        ]
                    },
                    {
                        "c": [
                            {"v": "February"},
                            {"v": 13},
                            {"v": 1, "f": "1 unit (Out of stock this month)"},
                            {"v": " <b>Shipping 2</b><br /><img src=\"http://icons.iconarchive.com/icons/antrepo/container-4-cargo-vans/512/Google-Shipping-Box-icon.png\" style=\"height:85px\" />", "p": {}}
                        ]
                    },
                    {
                        "c": [
                            {"v": "March"},
                            {"v": 24},
                            {"v": 5},
                            {"v": " <b>Shipping 6</b><br /><img src=\"http://icons.iconarchive.com/icons/antrepo/container-4-cargo-vans/512/Google-Shipping-Box-icon.png\" style=\"height:85px\" />", "p": {}}
                        ]
                    }
                ]
            },
            "options": {
                "title": "Progress Tracker",
                "isStacked": "true",
                "fill": 20,
                "displayExactValues": true,
                "vAxis": {
                    "title": "Devices",
                    "gridlines": {
                        "count": 10
                    }
                },
                "hAxis": {
                    "title": "Date"
                },
                "tooltip": {
                    "isHtml": true
                }
            },
            "formatters": {}
        }

    }, function(data, status, headers, config) {
		alertService.add('error', data.data);
		return;
    });


	$scope.isAllowedAction = function(action) {
	    var nextActions = $scope.path['next_actions']
	    if (typeof nextActions !== 'undefined') {
	        return nextActions.indexOf(action) != -1;
	    } else {
	        return false
	    }
	};
	
	
	$scope.save = function() {
		if(!$scope.path.upgradePath.sourceVersion || $scope.path.upgradePath.sourceVersion==""){
			alertService.add('error', "ERROR: Source cann't be empty!");
			return;
		}
       var noValue=false;
   	   angular.forEach($scope.path.upgradePath.match, function(value, key){
   		 if(angular.isUndefined(value) || (value == "")) {
			  noValue=true;
			  alertService.closeAllAlerts();
   			  alertService.add('error', "ERROR: Match criteria value can't be empty!");
				 return;
			 }
	     });
   	     if(noValue){
   	    	 return;
   	     }
        // update the metadata version if any metadata changed (SVCOTA-2728)\\following code has changed
      	if (angular.toJson($scope.path.metaData_orig) != angular.toJson($scope.path.metaData)) {
        		
        		var ts = Math.floor( new Date().getTime()/1000 );
        		alertService.add('warn', 'metadata has changed, new metaData version is '+ts);
        		$scope.path.metaData['metaVersion'] = ts;
        	}
        delete $scope.path.metaData_orig;
        
	    var params = {'pathjson': $filter('json')($scope.path)};
        PathCRUDService.save(params);
        $scope.post_next_action('EDITSAVE');
	}
	
	$scope.post_next_action = function(action) {
        if (action == 'PUBLISH') {
            $scope.path['upgradePath']['state'] = 'RUNNING';
        }
	    var params = {'action': action, 'guid': $routeParams.id, 'user': $rootScope.user.username, 'role': $rootScope.user.role, 'pathjson': $filter('json')($scope.path)};
        PathCRUDService.post_next_action(params);
	}
	$scope.enable_upgradepath = function() {
	    $scope.path['upgradePath']['state'] = 'RUNNING';
	    var params = {'pathjson': $filter('json')($scope.path)};
        PathCRUDService.publish(params);
	}
	$scope.disable_upgradepath = function() {
	    $scope.path['upgradePath']['state'] = 'STOPPED';
	    var params = {'pathjson': $filter('json')($scope.path)};
        PathCRUDService.publish(params);
	}
	$scope.setPublicAccessOn = function() {
	    $scope.path.upgradePath.privateAccessOnly = false;
	    alertService.add('error', 'WARNING: UPGRADE IS NOW ACCESSIBLE TO PUBLIC DEVICES!');
	}
	$scope.setPublicAccessOff = function() {
	    $scope.path.upgradePath.privateAccessOnly = true;
	    $scope.path.upgradePath.userStartTime = 0;
	    $scope.path.upgradePath.setupStartTime = 0;
	    $scope.path.upgradePath.controls = [];
	    alertService.closeAllAlerts();
	}
	$scope.openMessageBox = function(){
		var title = 'Delete Upgrade path?';
		var msg = 'Click OK to delete the upgrade path and the package binary from OTA system';
		var btns = [{result:'cancel', label: 'Cancel'}, {result:'ok', label: 'OK', cssClass: 'btn-primary'}];

		$dialog.messageBox(title, msg, btns)
			.open()
		    .then(function(result){
		        //alert('dialog closed with result: ' + result);
		        if (result == 'ok') {
		        	$scope.deletepath();
		        } else {
		        	return;
		        }
		     });
		  };
		
	$scope.deletepath = function() {
		var guid = $scope.path.guid;
		var packageId = $scope.path.upgradePath.packageId;
		var packagestore = $scope.path.upgradePath.packageStore;
		console.log('Deleting path : ' + guid + ' and pkg ' + packageId + ' from store ' + packagestore);
		//alert('delete called : Put a Are you Sure dialog here ' + guid + ' for pkg id ' + packageId + ' from store ' + packagestore);
		//return;
	    var params = {'pathguid': guid, 'packageguid': packageId, 'packagestore': packagestore};
        PathCRUDService.deletepath(params);
	}
	
}

// //////////////////////////////////////////////////////////
var uoc = function UpgradeOptionsController($scope) {

	$scope.onPickerClick = function() {
  	  $scope.path.pickerClicked = new Date().getTime();
	};

	$scope.timeEnabledCheck = function(ngModel, lower, upper) {
		var beginTime = new Date().getTime();
		if (ngModel != undefined) {
			var lastBeginTime = ngModel;	
			if (lastBeginTime > 0 && lastBeginTime < beginTime) {
				var lastDate = new Date(lastBeginTime);
				// the datetimepicker displays in utc...
				beginTime = lastDate.getTime() - (lastDate.getTimezoneOffset() * 60000); 
			}	
			else{
				var beginTimeNow = new Date();
				beginTime = beginTimeNow.getTime() - (beginTimeNow.getTimezoneOffset() * 60000); 
			}
					
		}

		// allow any date after the last setting or now
		//console.log("timeEnabledCheck unixDate " + new Date(unixDate).getTime() + " beginTime " + new Date(beginTime).getTime() + " enabled " + (unixDate > beginTime));
		return upper > beginTime;
	}
	
	$scope.getDateTimePickerDefaults = function() {
		var defaults = {
		    startView: 'day',
		    minView: 'minute',
		    minuteStep: 5,
		    dropdownSelector: null,
		    timeEnabled: $scope.timeEnabledCheck
		}
		return defaults;
	}

	$scope.getDateTimePickerLinkText = function(startDate) {
		
		var date = new Date();
		if (startDate != undefined) {
			date = new Date(startDate);
		}
		
		var offsetMinutes = new Date().getTimezoneOffset();
		
    	var offsetDirection = "-";
    	if (offsetMinutes < 0) {
    		offsetDirection = "+";
    	}
    	var gmtOffset = "(GMT " + offsetDirection + (offsetMinutes / 60) + " hr)";
		
    	return "starting on " + date.toLocaleDateString() + " " + date.toLocaleTimeString() +" " + gmtOffset;
	}
	var previousUserStartTime = 0;
	$scope.userStartTimeChange = function (allowUserRequestChecked, currentUserStartTime) {
		if (allowUserRequestChecked == false) {
			$scope.path.upgradePath.userStartTime = 0;
			previousUserStartTime = currentUserStartTime;
		} else {
			if ($scope.path.upgradePath.userStartTime <= 0) {
		        if (previousUserStartTime != 0) {
		        	$scope.path.upgradePath.userStartTime = previousUserStartTime;
		        } else {
		            var now = new Date();
		            var datenow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		        	$scope.path.upgradePath.userStartTime = datenow.getTime();
		        }
			}
		}
	}
	
	var previousSetupStartTime = 0;
	$scope.setupStartTimeChange = function (allowUserRequestChecked, currentSetupStartTime) {
		if (allowUserRequestChecked == false) {
			$scope.path.upgradePath.setupStartTime = 0;
			previousSetupStartTime = currentSetupStartTime;
		} else {
			if ($scope.path.upgradePath.setupStartTime <= 0) {
		        if (previousSetupStartTime != 0) {
		        	$scope.path.upgradePath.setupStartTime = previousSetupStartTime;
		        } else {
		            var now = new Date();
		            var datenow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		        	$scope.path.upgradePath.setupStartTime = datenow.getTime();

		        }
			}
		}
	}

    $scope.dateOptions3 = {
            //appendText: ' (MM/dd/yyyy) ',
            //showOn: 'both',
            showAnim: 'fadeIn',
            //yearRange: '1900:-0',
            defaultDate: 'null',
            beforeShowDay: function (date) {
                  var epochToday = new Date().getTime();
                  var epochTodayMinusOneDay = epochToday - 86400000;
                  if (date.valueOf() <= epochTodayMinusOneDay) {
                    return [false, '', 'Date before today is not allowed'];
                  }
                  return [true, '', 'Start'];
            }
        };
}

// //////////////////////////////////////////////////////////
var tc = function ListTargetsController($scope, $rootScope, alertService, Paths, $routeParams, $http, $location, $filter, $route, PathCRUDService) {

    
	$scope.names = ["john", "bill", "charlie", "robert", "alban", "oscar", "marie", "celine", "brad", "drew", "rebecca", "michel", "francis", "jean", "paul", "pierre", "nicolas", "alfred", "gerard", "louis", "albert", "edouard", "benoit", "guillaume", "nicolas", "joseph"];
	
    $scope.allLists = {}; // map of list guid to list label name (for displaying individual names)
    $scope.listArray = []; // list of name/guid pairs (for displaying the list selection dropdown)
    $scope.allListNames = [];
    $scope.allListGuids = [];
    
	$scope.listTimeEnabledCheck = function(ngModel, lower, upper) {
		var beginTime = new Date().getTime();
		if (ngModel != undefined) {
			var lastBeginTime = ngModel;	
			if (lastBeginTime > 0 && lastBeginTime < beginTime) {
				var lastDate = new Date(lastBeginTime);
				// the datetimepicker displays in utc...
				beginTime = lastDate.getTime() - (lastDate.getTimezoneOffset() * 60000); 
			}			
		}

		// allow any date after the last setting or now
		//console.log("timeEnabledCheck unixDate " + new Date(unixDate).getTime() + " beginTime " + new Date(beginTime).getTime() + " enabled " + (unixDate > beginTime));
		return upper > beginTime;
	}
	
	$scope.getListDateTimePickerDefaults = function(selectorId) {
		var defaults = {
		    startView: 'day',
		    minView: 'minute',
		    minuteStep: 5,
		    dropdownSelector: null,
		    timeEnabled: $scope.listTimeEnabledCheck
		}
		return defaults;
	}
	
	$scope.getListDateTimePickerLinkText = function(startDate) {
		
		var date = new Date();
		if (startDate != undefined) {
			date = new Date(startDate);
		}
		
		var offsetMinutes = new Date().getTimezoneOffset();
		
    	var offsetDirection = "-";
    	if (offsetMinutes < 0) {
    		offsetDirection = "+";
    	}
    	var gmtOffset = "(GMT " + offsetDirection + (offsetMinutes / 60) + " hr)";
		
    	return date.toLocaleDateString() + " " + date.toLocaleTimeString() +" " + gmtOffset;
	}

	
    $scope.getDeviceLists = function() {
        $http({
        	url: '/tlmslists/',
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.allLists = {};
                $scope.listArray = [];
                for (var i = 0; i < data.lists.length; i++) {
                    $scope.allLists[data.lists[i].listid] = data.lists[i].label;
                    var list = { name: data.lists[i].label, guid: data.lists[i].listid };
                    $scope.listArray.push(list);
                    $scope.allListNames.push(data.lists[i].label);
                    $scope.allListGuids.push(data.lists[i].listid);

                }
        }).
            error(function(data, status) {
                $scope.liststatus = status;
                alertService.add('warn', 'Error communicating with tlms, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with tlms, status is ' + status);
        })
    };
    
    // initialize the lists
    $scope.getDeviceLists();
    
    $scope.getListIdFromName = function(listName) {
    	var index = $scope.allListNames.indexOf(listName);
    	return $scope.allListGuids[index];
    };

	$scope.addListTarget = function() {
        // get the start of date for browser locale
        var now = new Date();
        var datenow = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        if ($scope.path.upgradePath.listTargets == undefined) {
            $scope.path.upgradePath.listTargets = [];
        }
        var target = {
            startDate: datenow.getTime(),
            listIds: []
        };
		$scope.path.upgradePath.listTargets.push(target);
	};
    
    $scope.deleteListTarget = function(item) {
		$scope.path.upgradePath.listTargets.splice($scope.path.upgradePath.listTargets.indexOf(item),1);
	};

    $scope.formatTargetList = function(item) {
		var listNames = '';
        if (item.listIds == undefined) {
            item.listIds = [];
        }
        for (var i = 0; i<item.listIds.length; i++) {
            if (i > 0) {
                listNames = listNames + ', ';
            }
            
            var listName = item.listIds[i];
            if ($scope.allLists != undefined && $scope.allLists[item.listIds[i]] != undefined) {
                listName = $scope.allLists[item.listIds[i]];
            }
            
            listNames = listNames + listName;
            
        }
        return listNames;
	};
   
    $scope.formatDate = function(epoch, tz) {
        var yyyy,
            mm,
            dd,
            datestr;
        var d = new Date(0);
        switch (tz) {
            case 'PST':
                d.setUTCSeconds(epoch/1000 - 7*3600);
                yyyy = d.getUTCFullYear();
                mm = ('0' + (d.getUTCMonth()+1)).slice(-2);     // add leading zero if needed: '01' for Jan
                dd = ('0' + d.getUTCDate()).slice(-2);
                break;
            case 'UTC':
                d.setUTCSeconds(epoch/1000);
                yyyy = d.getUTCFullYear();
                mm = ('0' + (d.getUTCMonth()+1)).slice(-2);
                dd = ('0' + d.getUTCDate()).slice(-2);
                break;
            default:
                console.warn("Unsupported timezone " + tz + ".. using PST instead");
                return formatDate(epoch, 'PST');
        }
        return yyyy + '-' + mm + '-' + dd;
    };

}

// //////////////////////////////////////////////////////////
var sc = function SchedulerController($scope, Paths, $routeParams, $route, $rootScope,$filter, Stats) {
	

/*	$scope.path = Paths.get({
		id : $routeParams.id
	}, function() {*/
		
/*		console.log('Starting in scheduler contoller %%%%%%%%%%%%%%%');
	    $scope.startDateOptions = [];
	    $scope.endDateOptions = [];
	    console.log('Starting in scheduler contoller ??????????????');
	    for (var i = 0; i < $scope.path.upgradePath.controls.length; i++) { //$scope.path.upgradePath.controls
	    	console.log('Starting in scheduler contoller ?????????????');
	    	
	        $scope.startDateOptions[i] = {
	            appendText: ' (MM/dd/yyyy) ',
	            showOn: 'both',
	            showAnim: 'fadeIn',
	            yearRange: '1900:-0',
	            beforeShowDay: function (date) {
	                var epochToday = new Date().getTime();
	                
	                console.log('Starting in scheduler contoller ?????????????' + i);
	                // Get all start and end dates from previous schedules
	                // and black out dates that user is not allowed to start
	                for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
	                	var stDate = $scope.path.upgradePath.controls[j].startDate;
	                	var enDate = $scope.path.upgradePath.controls[j].endDate;
	                	//console.log('startDate: ' + stDate);
	                	//console.log('endDate: ' + enDate);
	                	if (date.valueOf() >= stDate && date.valueOf() <= enDate) {
	                		return [false, '', 'Schedule Exists'];
	                	}
	                }

	                if (date.valueOf() <= epochToday) {
	                    return [false, '', 'Not Allowed'];
	                }
	                return [true, '', 'Create'];
	            }
	        };
	    }
	    for (var x = 0; x < $scope.path.upgradePath.controls.length; x++) { //$scope.path.upgradePath.controls
	    	console.log('Starting in end date contoller ?????????????');
	        console.log('Current interation !!!!!!! ' + x);
	        $scope.endDateOptions[x] = {
	                appendText: ' (MM/dd/yyyy) ',
	                showOn: 'both',
	                showAnim: 'fadeIn',
	                yearRange: '1900:-0',           
	                beforeShowDay: function (date) {
	                      console.log('Hello Date' + date.valueOf());
	                      var epochToday = new Date().getTime();
	                     
	                      // Get all start and end dates from previous schedules
	                      // and black out dates that user is not allowed to start
	                      // - Grey out anything before start date and before today
	                      // - Show valid dates from start date till we hit another start date
	                      
	                    
	                      var startDateArray = [];
	                      var endDateArray = [];
	                      for (var y = 0; y < $scope.path.upgradePath.controls.length; y++) {
	                    	  startDateArray[y] = $scope.path.upgradePath.controls[y].startDate;
	                    	  endDateArray[y] = $scope.path.upgradePath.controls[y].endDate;
	                      }
	                      startDateArray.sort(function(a,b){return a-b});
	                      endDateArray.sort(function(a,b){return a-b});
	                      var isThereANextStartDate = false;
	                      
	                      var currentStartDate = $scope.path.upgradePath.controls[x - 1].startDate;
	                      console.log('Current end iteration .............. ' + currentStartDate);
	                      
	                      var nextStartDate;
	                	  var startDayIndex = startDateArray.indexOf(currentStartDate);
	                	  var nextStartDateIndex = startDayIndex + 1;
	                	  if (nextStartDateIndex <= startDateArray.length) {
	                		  nextStartDate = startDateArray[nextStartDateIndex];
	                	  } else {
	                		  isThereANextStartDate = false;
	                	  }
	                      
	                	  if(!isThereANextStartDate) {
	                		  if (date.valueOf() >= currentStartDate) {
	                			  return [true, '', 'Create allowed'];
	                		  }
	                		  if (date.valueOf() <= epochToday) {
		                    	  return [false, '', 'Create allowed'];
		                      }                		  
	                	  }
	                      if (date.valueOf() >= epochToday) {
	                    	  return [true, '', 'Create allowed'];
	                      
	                      }    
	                      return [false, '', 'Create allowed'];
	                      	                      
	                }
	        
	            };
	        
	    } // end of for loop */
 //   }); 
	
    $scope.dateOptions = {
        appendText: ' (MM/dd/yyyy) ',
        showOn: 'both',
        showAnim: 'fadeIn',
        yearRange: '1900:-0',
        beforeShowDay: function (date) {
              //console.log('Hello Date' + date.valueOf());
              var epochToday = new Date().getTime();
             
              // Get all start and end dates from previous schedules
              // and black out dates that user is not allowed to start
              for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
            	  var stDate = $scope.path.upgradePath.controls[j].startDate;
            	  var numDays = $scope.path.upgradePath.controls[j].numDays;
            	  var enDate = stDate + (numDays - 1) * 24*3600*1000;
            	  //var enDate = $scope.path.upgradePath.controls[j].endDate;
            	  console.log('startDate: ' + stDate);
            	  console.log('endDate: ' + enDate);
            	  if (date.valueOf() >= stDate && date.valueOf() <= enDate) {
            		  return [false, '', 'Schedule Exists'];
            	  }
              }
              
              if (date.valueOf() <= epochToday) {
                return [false, '', 'Not Allowed'];
              }
              return [true, '', 'Create'];
        }
    };
    
    
    $scope.dateOptions2 = {
            appendText: ' (MM/dd/yyyy) ',
            showOn: 'both',
            showAnim: 'fadeIn',
            yearRange: '1900:-0',
            
            beforeShowDay: function (date) {
                  console.log('Hello Date' + date.valueOf());
                  var epochToday = new Date().getTime();
                  
                  // Get all start and end dates from previous schedules
                  // and black out dates that user is not allowed to start
                  // - Grey out anything before start date and before today
                  // - Show valid dates from start date till we hit another start date
                  
                  var startDateArray = [];
                  var endDateArray = [];
                  for (var i = 0; i < $scope.path.upgradePath.controls.length; i++) {
                	  startDateArray[i] = $scope.path.upgradePath.controls[i].startDate;
                	  endDateArray[i] = $scope.path.upgradePath.controls[i].endDate;
                  }
                  startDateArray.sort(function(a,b){return a-b});
                  endDateArray.sort(function(a,b){return a-b});
                  var isThereANextStartDate = true;
                  //console.log(control.startDate);
                  if (date.valueOf() >= epochToday) {
                	  return [true, '', 'Create allowed'];
                  
                  }    
                  return [false, '', 'Create allowed'];
            }
                  
/*                  for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
                	  var stDate = $scope.path.upgradePath.controls[j].startDate;
                	  var enDate = $scope.path.upgradePath.controls[j].endDate;
                	  
                	  var nextStartDate;
                	  var startDayIndex = startDateArray.indexOf(stDate);
                	  var nextStartDateIndex = startDayIndex + 1;
                	  if (nextStartDateIndex <= startDateArray.length) {
                		  nextStartDate = startDateArray[nextStartDateIndex];
                	  } else {
                		  // Current day plus three months
                		  nextStartDate = startDateArray(startDayIndex) + ((24 * 60 * 60 * 1000) * 90);
                	  }
                	  console.log('startDate: ' + stDate);
                	  console.log('endDate: ' + enDate);
                	  console.log('nextStartDate' + nextStartDate);

                	  //if (date.valueOf() >= stDate && date.valueOf() <= enDate) {
                		  //return [false, '', 'Schedule Exists'];
                	  //}
                	  if (date.valueOf() >= enDate && date.valueOf() <= nextStartDate) {
                		  return [true, '', 'Create allowed'];
                	  } 
                	  if (date.valueOf() <= epochToday) {
                          return [false, '', 'End date before today is not Allowed'];
                      }
                	 
                  }
                  
                  return [false, '', 'Schedule Exists'];
            }*/
    
        };
    
 /*   $scope.dateOptionsPollingSchedule = {
            appendText: ' (MM/dd/yyyy) ',
            showOn: 'focus',
            showAnim: '',
            yearRange: '1900:-0',
            beforeShowDay: function (date) {
                  //console.log('Hello Date' + date.valueOf());
                  //var epochToday = new Date().getTime();
                  
                  var currentControlIndex = $scope.path.upgradePath.lastSelectedControlIndex;
                  if (currentControlIndex == undefined) {
                      return [false, '', 'Not Allowed '+currentControlIndex];
                  }

                  // SVCOTA-2694: SUP Polling schedule - Disallow selecting the day before current date
                  if (currentControlIndex == 0) {
                      // get the start of date for browser locale
                      var now = new Date();
                      var datenow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                      
                      // get the current start date
                	  var stDate = $scope.path.upgradePath.controls[currentControlIndex].startDate;
                	  
                	  // disallow a date before the earliest of today or the current start date for this control
                	  var earliestPossibleDate = datenow.getTime();
                	  if (stDate < datenow.getTime()) {
                		  earliestPossibleDate = stDate;
                	  }

                	  if (date.valueOf() < earliestPossibleDate) {
                		  return [false, '', 'Before today and current control '+currentControlIndex];
                	  }
                  }

                  // Get the last element
                  if (currentControlIndex != 0) {
                	  var lastControlIndex = currentControlIndex - 1;
                	  var stDate = $scope.path.upgradePath.controls[lastControlIndex].startDate;
                	  var numDays = $scope.path.upgradePath.controls[lastControlIndex].numDays;
                	  if (numDays == undefined || numDays < 0) {
                		  numDays = 1;
                		  $scope.path.upgradePath.controls[lastControlIndex].numDays = 1;
                	  }
                	  var enDate = stDate + (numDays * 24*3600*1000);
                	  if (date.valueOf() < enDate) {
                		  return [false, '', 'Prior Schedule Exists '+currentControlIndex];
                	  }
                  }
                  
                  // Get the next element
                  if (currentControlIndex != ($scope.path.upgradePath.controls.length - 1)) {
                	  var nextControlIndex = currentControlIndex + 1;
                	  var stDate = $scope.path.upgradePath.controls[nextControlIndex].startDate;
                	  var numDays = $scope.path.upgradePath.controls[currentControlIndex].numDays;
                	  if (numDays == undefined || numDays < 0) {
                		  numDays = 1;
                		  $scope.path.upgradePath.controls[currentControlIndex].numDays = 1;
                	  }
                	  var lastPossibleDate = stDate - (numDays * 24*3600*1000);
                	  
                	  if (date.valueOf() > lastPossibleDate) {
                		  return [false, '', 'Next Schedule Exists '+currentControlIndex];
                	  }
                  }

                  return [true, '', 'Create '+currentControlIndex];
            },
		    onClose: function (dateText, inst) {
		        console.log('onClose' + dateText);
		        $scope.fixupControls();
		    },
		    onSelect: function (dateText, inst) {
		        console.log('onSelect' + dateText);
		        $scope.fixupControls();
		    }
		    
    };*/
    
    $scope.pollingScheduledTimeEnabledCheck = function(ngModel, date, upper,dateformat) {
    	
      	 
    	var currentControlIndex = $scope.path.upgradePath.lastSelectedControlIndex;
        if (currentControlIndex == undefined) {
            return false;
        }

        var stDateTime = new Date($scope.path.upgradePath.controls[currentControlIndex].startDate);
        var stDate=new Date(stDateTime.getFullYear(), stDateTime.getMonth(), stDateTime.getDate());
         
        	
        var now = new Date();
        var dateNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        var nowUTC= now.getTime() - (now.getTimezoneOffset() * 60000);
        var dateNowUTC= dateNow.getTime() - (dateNow.getTimezoneOffset() * 60000);

        //if startDate is in past disable calander
        if(dateformat=="day" && stDate<dateNow){
        	return false;
        }
        
        var stDateUTC= stDate.getTime() - (stDate.getTimezoneOffset() * 60000);
		var stDateTimeUTC= stDateTime.getTime() - (stDateTime.getTimezoneOffset() * 60000);
		var stDateTimeHour=new Date(stDate.getFullYear(), stDate.getMonth(), stDate.getDate(),(stDateTime.getHours()));
		var stDateTimeHourUTC= stDateTimeHour.getTime() - (stDateTimeHour.getTimezoneOffset() * 60000);
		stDateTimeHour=new Date(stDate.getFullYear(), stDate.getMonth(), stDate.getDate(),(stDateTime.getHours()));
		stDateTimeHourUTC= stDateTimeHour.getTime() - (stDateTimeHour.getTimezoneOffset() * 60000);
		
	      
		 //if date is startdate then return true
    	if ( dateformat=="day" && (date - stDateUTC) == 0) {
    		return true;
    	}
    	
    	//if time is starttime then return true
		if ( dateformat=="hour" && (date - stDateTimeHourUTC) == 0 ) {
    		return true;      
    	}
		
		//if time is in past return false
    	if(dateformat=="hour" &&  upper<nowUTC){
    		return false;
    	}
    	
    	//if time is in past return false
    	if( dateformat=="minute" &&  date<nowUTC){
    		return false;
    	}
    	
    	 //earliest possible startdate
    	if(currentControlIndex==0){
    		var numdays=stDateTime.getDate()-now.getDate();
    		var numhours=stDateTime.getHours()-now.getHours();
    		stDateTimeHour=new Date(stDateTime.getFullYear(), stDateTime.getMonth(), stDateTime.getDate()-numdays,(stDateTime.getHours())-numhours);
    		stDateTimeHourUTC= stDateTimeHour.getTime() - (stDateTimeHour.getTimezoneOffset() * 60000);
    		var numMinutes=stDateTime.getMinutes()-now.getMinutes();
    		
    		var	stDateTimeHourMinutes=new Date(stDateTime.getFullYear(), stDateTime.getMonth(), stDateTime.getDate()-numdays,stDateTime.getHours()-numhours,stDateTime.getMinutes()-numMinutes);
    		var	stDateTimeHourMinutesUTC= stDateTimeHourMinutes.getTime() - (stDateTimeHourMinutes.getTimezoneOffset() * 60000);
    	}
    	
    	var pickerDateTime=new Date(upper);
    	var pickerDate = new Date(pickerDateTime.getFullYear(), pickerDateTime.getMonth(), pickerDateTime.getDate());
    	
      
        //if date is in past then return false
    	if(dateformat=="day" && pickerDate<dateNowUTC){
    		return false;
    	}
    	
        // Get the last element
        if (currentControlIndex != 0) {
	      	  var lastControlIndex = currentControlIndex - 1;
	      	  var stDate = $scope.path.upgradePath.controls[lastControlIndex].startDate;
	      	
	     	 
	      	  var numDays = $scope.path.upgradePath.controls[lastControlIndex].numDays;
	      	  if (numDays == undefined || numDays < 0) {
	      		  numDays = 1;
	      		  $scope.path.upgradePath.controls[lastControlIndex].numDays = 1;
	      	  }
	      	  
	       	  var enDate = stDate + (numDays * 24*3600*1000);
	       	  var enDateUTC= (new Date(enDate)).getTime() - ((new Date(enDate)).getTimezoneOffset() * 60000);
	       	  
	       	  //earliest possible startdate
	          var startDate=new Date(stDate);
	       	  stDateTimeHour=new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()-numDays,(startDate.getHours()));
	       	  stDateTimeHourUTC= stDateTimeHour.getTime() - (stDateTimeHour.getTimezoneOffset() * 60000);
	       	
	         var stDateTimeHourMinutes=new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()-numDays,startDate.getHours(),stDateTime.getMinutes());
	     	 var stDateTimeHourMinutesUTC= stDateTimeHourMinutes.getTime() - (stDateTimeHourMinutes.getTimezoneOffset() * 60000);
	     	
	       	 
	       	  if ((dateformat=="day" || dateformat=="hour") && upper < enDateUTC) {
	      		  return false;
	      	  }
	       	  
	      	  if (dateformat=="minute"  && date < enDateUTC) { 
	    		  return false;
	      	  }
        }
        
       
        
        // Get the next element
        if (currentControlIndex != ($scope.path.upgradePath.controls.length - 1)) {
	      	  var nextControlIndex = currentControlIndex + 1;
	      	  var stDate = $scope.path.upgradePath.controls[nextControlIndex].startDate;
	      	  var numDays = $scope.path.upgradePath.controls[currentControlIndex].numDays;
	      	  if (numDays == undefined || numDays < 0) {
	      		  numDays = 1;
	      		  $scope.path.upgradePath.controls[currentControlIndex].numDays = 1;
	      	  }
	      	
	          var lastPossibleDate = stDate - (numDays * 24*3600*1000);
	          var lastPossibleDateUTC= (new Date(lastPossibleDate)).getTime() - ((new Date(lastPossibleDate)).getTimezoneOffset() * 60000);
	    	
	      	
	      	  if (date.valueOf() > lastPossibleDateUTC) {
	      		  return false;
	      	  }
        }
        if(dateformat=="hour"  && upper<stDateTime){	
    			return upper>stDateTimeHourUTC;
    	}
        
        if(dateformat=="minute" && upper<stDateTime){   
        		return upper>stDateTimeHourMinutesUTC;
        }
        return true;
	};
	
	
	
	$scope.pollingScheduleDeviceEligibleCheck=function(control){
		
			 var currentControlIndex  = $scope.path.upgradePath.controls.indexOf(control);
		      
		     	if($rootScope.isPublishedPackage){
		
				     var sourceVersion='_system.CHECK.'+$scope.path.upgradePath.sourceVersion;
			         var stDateTime = $scope.path.upgradePath.controls[currentControlIndex].startDate;
			         var numDays =$scope.path.upgradePath.controls[currentControlIndex].numDays;
			      	  
			       	 var enDate = stDateTime+ (numDays * 24*3600*1000);
			       	 var now = new Date();
			       	 if(enDate>=(now.getTime())) {
			       		
			       		 var stats = Stats.get({id : $scope.path.guid},
						   function(data){
			       			 	
								 var totalDeviceCameIn= data[sourceVersion];
								 var totalEligibleNow=data['_system.CHECK.ELIGIBLE_NOW'];
								 
								 if(totalEligibleNow>0){
									var totalComeBackLater=totalDeviceCameIn-totalEligibleNow;
								 }else{
									var totalComeBackLater=totalDeviceCameIn;
								 }
								 var provisionTimeinSeconds=$scope.path.upgradePath.controls[currentControlIndex].provisionTimeDelta;
	
								 if(angular.isDefined(provisionTimeinSeconds) && provisionTimeinSeconds!=0){

									 var provisionTime=parseInt(provisionTimeinSeconds) / 86400;
									 var timenow = new Date().setHours(0,0,0,0);
									 timenow=timenow-25200000;
									 var counter=0;
									 for (var i=1;i<=provisionTime;i++)
									{ 
										var provisionedTimeStatsText='_system.CHECK.provisionedTime:'+(timenow);
										timenow=timenow-86400000;
										var provisionedTimeStatsCounter=(data[provisionedTimeStatsText]);
										
										if(provisionedTimeStatsCounter!=undefined)
										counter=counter+provisionedTimeStatsCounter;
									}
									 var totalEligibleAfterProvisionedTimeCounter=totalComeBackLater-counter;
								 }else{
									 var totalEligibleAfterProvisionedTimeCounter=totalComeBackLater;
								 }
								
								 var totalEligibleAfterPercentageCount= Math.round((totalEligibleAfterProvisionedTimeCounter*($scope.path.upgradePath.controls[currentControlIndex].timeSlots[0].percentDownloads))/100);
								
								// var totalEligibleAfterHoursCalculation=Math.round((totalEligibleAfterPercentageCount*($scope.path.upgradePath.controls[currentControlIndex].timeSlots[0].duration/3600))/24);
								 if(totalEligibleAfterPercentageCount>0){
								     if(control.algorithm=="FLAT_PERCENTAGE"){
										 var totaleligibleText="During this polling schedule,  we will allow roughly "+ totalEligibleAfterPercentageCount +" devices to upgrade daily";
									 }else if(control.algorithm=="INCREMENTING_PERCENTAGE"){
										 var totaleligibleText="During this polling schedule,  we will allow roughly "+ totalEligibleAfterPercentageCount +" devices to upgrade by end of schedule";
									 }
									 $scope.path.upgradePath.controls[currentControlIndex].deviceEligible=totaleligibleText;
				 
								 }else{
									 $scope.path.upgradePath.controls[currentControlIndex].deviceEligible= "Unfortunately, there isn't enough data to determine the number of devices eligible to upgrade during this polling schedule. Come back after 24 hrs";
								 }
								 
							}, function(err){
							    console.log('request failed');
							    return false;
							});
			       		
			       	 }else{
			       	     $scope.path.upgradePath.controls[currentControlIndex].deviceEligible="This schedule is done";
			       	 }
			  }else{
				        $scope.path.upgradePath.controls[currentControlIndex].deviceEligible="This SUP is not published and running yet, so we can't tell you how many devices will be eligible for an upgrade";
				   }
		   	   
	}
	
	
	 $scope.provisionTimeDisable=function(control){
	
		 var currentControlIndex  = $scope.path.upgradePath.controls.indexOf(control);
         if (currentControlIndex == undefined) {
             return true;
         }
         var now = new Date();
         var stDateTime = new Date($scope.path.upgradePath.controls[currentControlIndex].startDate);
         if(stDateTime<now){
         	return true;
         }
         return false;
     }
    
    $scope.getPollingScheduleDateTimePickerDefaults = function(control,selectorId) {
		
    	   var index = $scope.path.upgradePath.controls.indexOf(control);
    	 
    	   $scope.path.upgradePath.lastSelectedControlIndex = index;
        	
    	   var defaults = {
		    startView: 'day',
		    minView: 'minute',
		    minuteStep: 5,
		    dropdownSelector: null,
		    timeEnabled: $scope.pollingScheduledTimeEnabledCheck,

		    onClose: function (dateText, inst) {
		        console.log('onClose' + dateText);
		        $scope.fixupControls();
		    },
		    onSelect: function (dateText, inst) {
		        console.log('onSelect' + dateText);
		        $scope.fixupControls();
		    }
		};
		return defaults;
	};
	

	$scope.onPickerClick = function() {
  	  $scope.path.pickerClicked = new Date().getTime();
	};
	
	

        
    $scope.fixupControls = function() {
        console.log('fixupControls');
    	
        // first sort the controls
        $scope.path.upgradePath.controls.sort( function ( a, b ) {return a.startDate - b.startDate;} );
        
        var lastEndDate = 0;
        
        // now fix them
        for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
      	  var stDate = $scope.path.upgradePath.controls[j].startDate;
      	  if (stDate < lastEndDate) {
      		$scope.path.upgradePath.controls[j].startDate = lastEndDate;
      		stDate = lastEndDate;
      	  }
      	  var numDays = $scope.path.upgradePath.controls[j].numDays;
    	  if (numDays == undefined || numDays < 0) {
    		  numDays = 1;
    		  $scope.path.upgradePath.controls[j].numDays = 1;
    	  }
    	  var algorithm = $scope.path.upgradePath.controls[j].algorithm;
    	  if (algorithm == undefined) {
    		  $scope.path.upgradePath.controls[j].algorithm = 'FLAT_PERCENTAGE';
    	  }
    	  
      	  lastEndDate = stDate + (numDays * 24*3600*1000);
        }
    };

	$scope.deleteSchedule = function(item) {
		$scope.path.upgradePath.controls.splice($scope.path.upgradePath.controls.indexOf(item),1);
	};
    $scope.onNumDaysChange = function(item) {
		// sort just in case...
        $scope.path.upgradePath.controls.sort( function ( a, b ) {return a.startDate - b.startDate;} );
        var lastEndDate = 0;
        for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
        	  var stDate = $scope.path.upgradePath.controls[j].startDate;
        	  
        	  if (lastEndDate != 0) {
        		  if (stDate < lastEndDate) {
        			  $scope.path.upgradePath.controls[j].startDate = lastEndDate;
        			  stDate = lastEndDate;
        		  }
        	  }
        	  var numDays = $scope.path.upgradePath.controls[j].numDays;
        	  var lastEndDate = numDays * 1440*60*1000 + stDate;
          }
        
      
	};
	$scope.onDatePickerSelected = function(control) {
  	  var index = $scope.path.upgradePath.controls.indexOf(control);
  	  console.log('onDatePickerChange control index: '+index);
  	  $scope.path.upgradePath.lastSelectedControlIndex = index;
  	 $rootScope.currentControlIndex = index;
	};
	
	
	$scope.onDateChanged = function(control) {
  	  var index = $scope.path.upgradePath.controls.indexOf(control);
  	  console.log('onDateChanged control index: '+index);
  	  $scope.path.upgradePath.lastSelectedControlIndex = index;
  	  console.log('onDateChanged control value: '+$scope.path.upgradePath.controls[index].startDate);

	};

	$scope.addSchedule = function() {
        // get the start of date for browser locale
        var now = new Date();
        var datenow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        var lastEndDate = now.getTime();
        var reportingTagsValue = $scope.path.upgradePath.match.hwType + '_' + now.getTime();
        
        for (var j = 0; j < $scope.path.upgradePath.controls.length; j++) {
      	  var stDate = $scope.path.upgradePath.controls[j].startDate;
      	  var numDays = $scope.path.upgradePath.controls[j].numDays;
      	  var enDate = numDays * 1440*60*1000 + stDate;
      	  if (lastEndDate < enDate) {
      		  lastEndDate = enDate;
      	  }
      	
      	  //var enDate = $scope.path.upgradePath.controls[j].endDate;
      	  console.log('addSchedule startDate: ' + stDate);
      	  console.log('addSchedule endDate: ' + enDate);
      	  console.log('addSchedule lastEndDate: ' + lastEndDate);
      	  console.log('addSchedule default reporting tag: ' + reportingTagsValue)
        }
        
         var startTime = (-1)*((new Date(lastEndDate).getTimezoneOffset())*60);
        if (startTime < 0) {
            startTime += (1440*60);
        }
        

        
		var newSchedule = { 
			startDate: lastEndDate,   // save as epoch
			endDate: now.getTime(),
			numDays: 1,
			algorithm: 'FLAT_PERCENTAGE',
			reportingTags: reportingTagsValue,
			timeSlots: [
	          	{
	            	duration: 86400,
	            	start: startTime,
	            	percentDownloads: 10
	          	}
        	],
			allowTargetedLists: false,
        	requestTypesAllowed: ["user"]
      	}
		console.log("newschedule: "+newSchedule);
		$scope.path.upgradePath.controls.push(newSchedule);
	};
	
	
	
	$scope.togglePollState = function($index, $type) {
		var existsIndex = $scope.path.upgradePath.controls[$index].requestTypesAllowed.indexOf($type);
		if (existsIndex == -1) {
			$scope.path.upgradePath.controls[$index].requestTypesAllowed.push($type);
		} else {
			$scope.path.upgradePath.controls[$index].requestTypesAllowed.splice(existsIndex,1);
		}
	};
    
    $scope.formatDate = function(epoch, tz) {    	
        var yyyy,
            mm,
            dd,
            datestr;
        var d = new Date(0);
        switch (tz) {
            case 'PST':
                d.setUTCSeconds(epoch/1000 - 7*3600);
                yyyy = d.getUTCFullYear();
                mm = ('0' + (d.getUTCMonth()+1)).slice(-2);     // add leading zero if needed: '01' for Jan
                dd = ('0' + d.getUTCDate()).slice(-2);
                break;
            case 'UTC':
                d.setUTCSeconds(epoch/1000);
                yyyy = d.getUTCFullYear();
                mm = ('0' + (d.getUTCMonth()+1)).slice(-2);
                dd = ('0' + d.getUTCDate()).slice(-2);
                break;
            default:
                console.warn("Unsupported timezone " + tz + ".. using PST instead");
                return formatDate(epoch, 'PST');
        }
        return yyyy + '-' + mm + '-' + dd;
    };
    
    $scope.setMinValue= function(control){
        
    	var now=new Date();
    	
    	var today = $filter('date')(now, 'short');
        var stdate=$filter('date')(control.startDate, 'short');
       
        var endDate = control.startDate + ((control.numDays) * 24*3600*1000);
        var days=1;
       
        //if polling schedule is done then then current control value is min
        if(endDate<(now.getTime())){
        		
        	return control.numDays;	
        }
        
        endDate=$filter('date')(endDate, 'short');
     
        //if polling schedule is running then numdays can not go past
        if(endDate>today){
        	
        		if(stdate<today){
        		    	var newStartDate=new Date(control.startDate);
        	    	    
        		        days=now.getDate()-(newStartDate).getDate();
        		    	var hours=now.getHours()-(newStartDate).getHours();
        		    	var minutes=now.getMinutes()-(newStartDate).getMinutes();
        		    
        		    	//when schedule already finished for today's date and time and still running then can't go back so days=days+1
        	    	    if(hours>0){      
        	    	        days=days+1;
        	    	    }else
        	    	    if(hours==0 && minutes>0){     
       	    	        	days=days+1;
       	    	        }
        	    	
        				return days;
        	
    	        }
         }
       
        return days;
    };
    
     
     $scope.setMaxValue= function(control){
    	    
     	var now=new Date();
      	var endDate = control.startDate + ((control.numDays) * 24*3600*1000);
        var days=1000;
        
        //if polling schedule is done then then current control value is max
         if(endDate<(now.getTime())){     	
         	return control.numDays;	
         }
     
         return days;
     };
     
     $scope.perPollingCheck = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 console.log('First Reporting tag: ' + tag);
    	 
    	 //var pollingCheckTag = '_system.CHECK.polling.' + tag;
    	 var pollingCheckTag = 'CHECK.polling.' + tag;
    	 var pollingCheck = $scope.stats[pollingCheckTag];
    	 console.log('pollingCheck: ' + pollingCheck);
    	 return pollingCheck;
     };
     
     $scope.perPollingEligibleNow = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var eligibleNowTag = 'CHECK.ELIGIBLE_NOW.' + tag;
    	 return $scope.stats[eligibleNowTag];
     };
     
     $scope.comebacklater = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 
    	 var pollingCheckTag = 'CHECK.polling.' + tag;
    	 $scope.pollingCheck = $scope.stats[pollingCheckTag];
    	 console.log('pollingCheck: ' + $scope.pollingCheck);
    	 
    	 var eligibleNowTag = 'CHECK.ELIGIBLE_NOW.' + tag;
    	 $scope.eligibleNow = $scope.stats[eligibleNowTag];
    	 
    	 //var comebacklaterTag = 'CHECK.COME_BACK_LATER.' + tag;
    	 //$scope.comebacklater = $scope.stats[comebacklaterTag];
    	 var pollingCounter = $scope.stats[pollingCheckTag];
    	 var eligibleNowCounter =  $scope.stats[eligibleNowTag];
    	 var comelater = null;
    	 // Avoid NaN and display of null
    	 if (pollingCounter != undefined && eligibleNowCounter != undefined) {
    		 comelater = pollingCounter - eligibleNowCounter;
    	 }
    	 return comelater;
     };
     
     $scope.notified = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var notifiedTag = 'REPORT.Notified.' + tag;
    	 return $scope.stats[notifiedTag];
     };
     
     $scope.requestPermission = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var requestPermissionTag = 'REPORT.RequestPermission.' + tag;
    	 return $scope.stats[requestPermissionTag];
     };
     
     $scope.gettingDescriptor = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var gettingDescriptorTag = 'REPORT.GettingDescriptor.' + tag;
    	 return $scope.stats[gettingDescriptorTag];
     };
     
     $scope.gettingPackage = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var gettingPackageTag = 'REPORT.GettingPackage.' + tag;
    	 return $scope.stats[gettingPackageTag];
     };
     
     $scope.querying = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var queryingTag = 'REPORT.Querying.' + tag;
    	 return $scope.stats[queryingTag];
     };
     
     $scope.upgrading = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var upgradingTag = 'REPORT.Upgrading.' + tag;
    	 return $scope.stats[upgradingTag];
     };
     
     $scope.done = function(control) {
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 var doneTag = 'REPORT.Result.DONE.' + tag;
    	 return $scope.stats[doneTag];
     };
     
/*     $scope.populatePerPollingStats = function(control) {
    	
    	 //$scope.perPollingStats = Stats.get({id : $scope.path.guid}); $scope.stats is already available
    	 //get one tag from comma separated tags
    	 var tags = control.reportingTags;
    	 if (tags == undefined || tags == '') {
    		 var tag = '';
    	 } else {
    		 var tagsArray = tags.split(",");
    		 var tag = tagsArray[0];
    	 }
    	 console.log('First Reporting tag: ' + tag);
    	 
    	 //var pollingCheckTag = '_system.CHECK.polling.' + tag;
    	 var pollingCheckTag = 'CHECK.polling.' + tag;
    	 $scope.pollingCheck = $scope.stats[pollingCheckTag];
    	 console.log('pollingCheck: ' + $scope.pollingCheck);
    	 
    	 var eligibleNowTag = 'CHECK.ELIGIBLE_NOW.' + tag;
    	 $scope.eligibleNow = $scope.stats[eligibleNowTag];
    	 
    	 //var comebacklaterTag = 'CHECK.COME_BACK_LATER.' + tag;
    	 //$scope.comebacklater = $scope.stats[comebacklaterTag];
    	 var pollingCounter = $scope.stats[pollingCheckTag];
    	 var eligibleNowCounter =  $scope.stats[eligibleNowTag];
    	 var comelater = null;
    	 // Avoid NaN and display of null
    	 if (pollingCounter != undefined && eligibleNowCounter != undefined) {
    		 comelater = pollingCounter - eligibleNowCounter;
    	 }
    	 $scope.comebacklater = comelater;
    	 
    	 var notifiedTag = 'REPORT.Notified.' + tag;
    	 $scope.notified = $scope.stats[notifiedTag];
    	 
    	 var requestPermissionTag = 'REPORT.RequestPermission.' + tag;
    	 $scope.requestPermission = $scope.stats[requestPermissionTag];
    	 
    	 var gettingDescriptorTag = 'REPORT.GettingDescriptor.' + tag;
    	 $scope.gettingDescriptor = $scope.stats[gettingDescriptorTag];
    	 
    	 var gettingPackageTag = 'REPORT.GettingPackage.' + tag;
    	 $scope.gettingPackage = $scope.stats[gettingPackageTag];
    	 
    	 var queryingTag = 'REPORT.Querying.' + tag;
    	 $scope.querying = $scope.stats[queryingTag];
    	 
    	 var upgradingTag = 'REPORT.Upgrading.' + tag;
    	 $scope.upgrading = $scope.stats[upgradingTag];
    	 
    	 var doneTag = 'REPORT.Result.DONE.' + tag;
    	 $scope.done = $scope.stats[doneTag];
     }; */
    
    $scope.formatData = function(control) {    	
    	var startDate = new Date(control.startDate);
    	
    	var offsetDirection = "-";
    	if (startDate.getTimezoneOffset() < 0) {
    		offsetDirection = "+";
    	}
    	var gmtOffset = "(GMT " + offsetDirection + (startDate.getTimezoneOffset() / 60) + " hr)";
    	
    	var hours=startDate.getHours();
    	var minutes=startDate.getMinutes();
    
    	var localSeconds = (hours  * 3600 ) + (minutes * 60);
    	    
         // change the seconds to UTC seconds
         var utcOffsetMinutes = new Date().getTimezoneOffset();
         var utcSeconds = localSeconds + (utcOffsetMinutes*60);
         if (utcSeconds < 0) {
             utcSeconds += (1440*60);
         }
         utcSeconds = utcSeconds % (1440*60); 
         
    	control.timeSlots[0].start=utcSeconds;
         utcSeconds = parseInt(utcSeconds);
        var utcOffsetMinutes =  new Date().getTimezoneOffset();
        
        
        // convert UTC seconds to local seconds
       /* var seconds = utcSeconds + (-1 * utcOffsetMinutes * 60);
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

        var startTimeText = HH + ':' + mm;
        */
        var algorithm = control.algorithm;
        if (algorithm == undefined) {
        	control.algorithm = 'FLAT_PERCENTAGE';
        }
        var algorithmString = 'each day';
        if (control.algorithm != 'FLAT_PERCENTAGE') {
        	algorithmString = 'by end of schedule';
        }
        
        if(angular.isDefined(control.provisionTimeDelta) && control.provisionTimeDelta>0){
        	
        	var provisionTimeDelta=Math.round((control.provisionTimeDelta)/86400);
         	
	    	return "start " + startDate.toLocaleDateString() + " (" + startDate.toLocaleTimeString() +")" + 
	    		" for " + control.numDays + " day(s) upgrading "+control.timeSlots[0].percentDownloads+"% "+algorithmString+
	    		" and daily duration " + ((control.timeSlots[0].duration)/3600) + " hours " +
	    		gmtOffset + " and allow devices provisioned more than "+ provisionTimeDelta +" day(s) ago";
        }else
        	{
        	return "start " + startDate.toLocaleDateString() + " (" + startDate.toLocaleTimeString() +")" + 
	    		" for " + control.numDays + " day(s) upgrading "+control.timeSlots[0].percentDownloads+"% "+algorithmString+
	    		" and daily duration " + ((control.timeSlots[0].duration)/3600) + " hours " + gmtOffset
        	}

    };
    
$scope.getPollingScheduleDateTimePickerLinkText = function(control) {    	
        
    	var startDate = new Date(control.startDate);
    	
    	var date = new Date();
		if (startDate != undefined) {
			date = new Date(startDate);
		}
		
		var offsetMinutes = new Date().getTimezoneOffset();
		
    	var offsetDirection = "-";
    	if (offsetMinutes < 0) {
    		offsetDirection = "+";
    	}
    	var gmtOffset = "(GMT " + offsetDirection + (offsetMinutes / 60) + " hr)";
		
    	return "start "+ date.toLocaleDateString() + " " + date.toLocaleTimeString() +" " + gmtOffset;

    };
    
    $scope.autofillEndDate = function(control, tz) {
        // Compute the endDate if needed (because the POJO does not supply it) and display as UTC date
        if (typeof control.endDate === 'undefined') {
            control.endDate = control.startDate + (control.numDays - 1) * 24*3600*1000;
        }
        //return $scope.formatDate(control.endDate, tz);
        return control.endDate;
    };

    $scope.updateStartDate = function(control, startdate, tz) {
        var MSEC_PER_DAY = 24 * 60 * 60 * 1000;
/*        switch (tz) {   // store as epoch, eg: "2013-06-14" -> 1371168000000
            case 'PST':
                control.startDate = Date.parse(startdate + " 00:00 PST");
                break;
            case 'UTC':
                control.startDate = Date.parse(startdate + " 00:00 UTC");
                break;
            default:
                console.warn("Unsupported timezone " + tz + ".. using PST instead");
                control.startDate = Date.parse(startdate + " 00:00 PST");
        }*/
        control.numDays = Math.round((control.endDate - control.startDate)/MSEC_PER_DAY) + 1;
    };
    $scope.updateEndDate = function(control, enddate, tz) {
        var MSEC_PER_DAY = 24 * 60 * 60 * 1000;
/*        switch (tz) {
            case 'PST':
                control.endDate = Date.parse(enddate + " 00:00 PST");
                break;
            case 'UTC':
                control.endDate = Date.parse(enddate + " 00:00 UTC");
                break;
            default:
                console.warn("Unsupported timezone " + tz + ".. using PST instead");
                control.endDate = Date.parse(enddate + " 00:00 PST");
        }*/
        control.endDate = enddate;
        control.numDays = Math.round((control.endDate - control.startDate)/MSEC_PER_DAY) + 1;
    };
    
}

////////////////////////////////////////////////////////////
var vc = function VerifyController($scope, $rootScope, alertService, Paths, $routeParams, $http, $location, $filter, $route, PathCRUDService) {
    
    $scope.checkInTlms = function(imei) {
    	
        alertService.closeAllAlerts();
        $scope.match = {};
        
        if (imei == undefined || imei.length == 0) {
            alertService.add('error', 'Error a serial number is required');
            return;
        }
        
        var inMasterWhiteList = false;
        $scope.resultCounter = 0;
        
        $http({
        	url: '/tlmsmatch/'+imei,
        	method: 'GET'
        }).
            success(function(data, status) {
                $scope.match = data;
                $scope.preMatchTest = false;
                $scope.matchFoundInList = "No Targeted List";
                if ($scope.match.reason == 'excluded' && $scope.match.matches == false) {
                    $scope.matchFoundInList = "Device in Master Blacklist -- will not upgrade";
                    $scope.openModal($scope.matchFoundInList);
                    return;
                } else if ($scope.match.reason == 'included' && $scope.match.matches == true) {
                    inMasterWhiteList = true;
                    console.log("In master white list");
                }
                
                $scope.resultCounter = 1;
        }).
            error(function(data, status) {
                alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                console.log('Error communicating with list server, status is ' + status);
        })
        
        // Not is Master Black List - 
        // Need to iterate through each target date (list) and check for eligibility
        var stDates = new Array();
        var inTargetWhiteList = false;
        var eligibleDates = new Array();
        var supGuid = $scope.path.guid;
        $scope.resultCounter2 = 0;
        
        for (var j = 0; j < $scope.path.upgradePath.listTargets.length; j++) {
        	var stDate = $scope.path.upgradePath.listTargets[j].startDate;
        	var softwareVersion = supGuid + ":" + stDate;
        	console.log(softwareVersion);
        	var params = {'softwareversion': softwareVersion, 'user': 'root', 'serialnumber': imei, 'type': 'acl',};
        	
        	$http({
            	url: '/tlmscheckeligibility/',
            	method: 'GET',
            	params: params
            }).
                success(function(data, status) {
                    $scope.match = data;
                    console.log($scope.match);
                    $scope.inBalckOrWhiteList = "Not in master black or white list";
                    
                    if ($scope.match.reason == 'excluded' && $scope.match.matches == false) {
                        $scope.matchFoundInList = "Device is Blacklisted on a target list on " + stDate + " -- will not upgrade";
                        $scope.openModal($scope.matchFoundInList, $scope.match);
                        return;
                    } else if ($scope.match.reason == 'included' && $scope.match.matches == true) {
                        $scope.matchFoundInList = "Device is eligible to upgrade on " + " " + stDate;
                        console.log($scope.matchFoundInList);
                        console.log($scope.match);
                        inTargetWhiteList = true;
                        eligibleDates.push(stDate);
                    }
                    
                    $scope.resultCounter2 = $scope.resultCounter2 + 1;
            }).
                error(function(data, status) {
                    alertService.add('warn', 'Error communicating with list server, status is ' + status + ' refresh your browser and try again');
                    console.log('Error communicating with list server, status is ' + status);
            })      	
        }
        	      
        $scope.$watch("resultCounter + resultCounter2", function() {
        	
        	if ($scope.resultCounter == 1 && $scope.resultCounter2 == $scope.path.upgradePath.listTargets.length) {
        		// run code
        		if (inMasterWhiteList == true && inTargetWhiteList == true) {
                	var eligibleDatesString;
                	for (var i = 0; i < eligibleDates.length; i++) {
                		var dt = new Date(eligibleDates[i]);
                		eligibleDatesString = " " + dt;
                	}
                	$scope.matchFoundInList = "Device is eligible to upgrade on the following date(s) :\n " + eligibleDatesString;
                	console.log('Matched MasterWhiteList and TargetWhiteList:  ' + $scope.matchFoundInList);
                	$scope.openModal($scope.matchFoundInList);
                } else if (inMasterWhiteList == true && inTargetWhiteList == false) {
                	$scope.matchFoundInList = "Device is present in Master White List but not in any SUP Target List -- will NOT upgrade";
                	console.log('Matched MasterWhiteList and NOT TargetWhiteList: ' + $scope.matchFoundInList);
                	$scope.openModal($scope.matchFoundInList);
                } else if (inMasterWhiteList == false && inTargetWhiteList == true) {
                	var eligibleDatesString;
                	for (var i = 0; i < eligibleDates.length; i++) {
                		var dt = new Date(eligibleDates[i]);
                		eligibleDatesString = " " + dt;
                	}
                	$scope.matchFoundInList = "Device is NOT present in Master Whitle List but is present in SUP Target List -- will NOT upgrade";
                	console.log('Matched NOT MasterWhiteList but TargetWhiteList: ' + $scope.matchFoundInList);
                	$scope.openModal($scope.matchFoundInList);
                } else {
                	// Not found in black white or target lsit
                	$scope.matchFoundInList = "Did not find device in any List (Master Whitle List or SUP Target List) -- will not upgrade";
                	console.log('Matched NOT in MasterWhiteList and NOT in TargetWhiteList ' + $scope.matchFoundInList);
                	$scope.openModal($scope.matchFoundInList);
                }
        
        	}
        
        });
    	
    };
    
    $scope.openModal = function (deviceupgradeEligibityString) {
        $scope.shouldBeOpen = true;
        $scope.eligibityString = deviceupgradeEligibityString;
    };

    $scope.closeModal = function () {
        $scope.shouldBeOpen = false;
    };

    $scope.options = {
    	backdropFade: true,
    	dialogFade:true
    };

}

var uc = function UploadController ($scope, $rootScope, $location, $dialog, $http, alertService, uploadService,$filter) {

    $scope.opts = {
        backdrop: true,
        keyboard: true,
        backdropClick: true,
        templateUrl: 'static/ui/app/partials/JenkinsProgress.html',  // OR: template:  t,
        controller: 'JenkinsDialogController'
    };

	$scope.uploadfromlocal = function() {

	     var payload = new FormData();
	   // populate payload
        angular.forEach($scope.requiredFields,function(object,index){
            if(object.label!="" && object.value!=""){
        		 payload.append(object.label, object.value);
        		
             }
        });
     
        angular.forEach($scope.matchCriteria,function(object,index){
            if(object.label!="" && object.value!=""){
        		 payload.append(object.label, object.value);
             }
        });
        
        // populate payload
        if ($scope.packageandxml[0].type == 'text/xml') {
            payload.append("binary", $scope.packageandxml[1]);
        } else {
            payload.append("binary", $scope.packageandxml[0]);
        }
        
        payload.append("FingerPrint", $scope.fingerPrint);
      
       
        $http.post('/uploadbinary/', 
                   payload, {
                       headers: { 'Content-Type': false
                    	  },
                       transformRequest: function(data) { return data; },
                       params: {'usecds': $scope.usecds4local,}
                    })
            .success(function(data, status, headers, config) {
                $scope.status = status;
                $scope.guid = data.guid;
                $scope.closeJenkinsDialog();
                $location.path('/path/edit/' + $scope.guid).replace();
            }).
            error(function(data, status, headers, config) {
                $scope.closeJenkinsDialog();
                alertService.add( 'error', data );
            });
        $dialog.dialog($scope.opts).open();
    };
    
    
    $scope.requiredFields= [
                      {label:'Source',value:''},
                      {label:'Target',value:''},
                    ];
    
	
    $scope.matchCriteria = [
                     {label:'hwType',value:''},
                     {label:'carrier',value:''},
                     {label:'region',value:''}
                   ];

                  
    $scope.AddMatchCriteria = function() {
    	var duplicate=false;
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if(object.label==$scope.myObject.criteria){
    			  duplicate=true;
    		  }
        });	
    	if(!duplicate){
    	  $scope.matchCriteria.push({label:$scope.myObject.criteria,value:""});
    	  $scope.myObject.criteria="";
        }
    };
    
    $scope.ValidateMatchCriteria = function(newCriteriatoAdd) {
    	var duplicate=false;
    	if(newCriteriatoAdd=="" ){
    		return false;
    	}
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if($filter('lowercase')(object.label)==$filter('lowercase')(newCriteriatoAdd)){
    			  duplicate=true;
    			  return false;
    		  }
        });	
    	if(!duplicate){
    	return true;
    	}
    	return false;
    };
    
    
    $scope.isValidCriteria= function(newCriteriatoAdd) {
    	var duplicate=false;
    	
    	angular.forEach($scope.matchCriteria,function(object,index){
    		  if($filter('lowercase')(object.label)==$filter('lowercase')(newCriteriatoAdd)){
    			  duplicate=true;
    			  return false;
    		  }
        });	
    	if(!duplicate){
    	return true;
    	}
    	return false;
    };
    
    $scope.deleteMatchCriteria = function(labelToRemove) {
    	  angular.forEach($scope.matchCriteria,function(object,index){
    		  if(object.label==labelToRemove){
    			 $scope.matchCriteria.splice(index,1);
    			  }
          });
    };
    
    $scope.validPackageAndXML = function() {
        console.log('UploadController: Do validPackageAndXML, do we have one blob and one XML?');
      
        if (angular.isUndefined($scope.packageandxml)) {
            return false;
        }
        if ($scope.packageandxml.length != 2 && $scope.packageandxml.length != 1 ) {
            return false;
        }
        
        if (($scope.packageandxml.length == 1 && $scope.packageandxml[0].type == 'text/xml')) {
            return false;
        }
       
        //if no value then return false and disable upload button
        var keepgoing=true;
        angular.forEach($scope.matchCriteria,function(object,index){
         if(keepgoing){
  		  if(object.value==""){
  			keepgoing=false;
  		  }
        }
  		});
        
        if(!keepgoing){
        	return false;
        }
        
      //if no value then return false and disable upload button
        angular.forEach($scope.requiredFields,function(object,index){
    		  if(object.value==""){
    			  keepgoing=false;
    		  }
    		});
        
        if(!keepgoing){
        	return false;
        }
        return true;
    };
   
  
    $scope.parseXmlValue=function(){
    	
    	if (angular.isUndefined($scope.packageandxml)) {
            return false;
        }
    	
    	//clear all the value
    	 angular.forEach($scope.matchCriteria,function(object,index){
             if(object.label!=""){ 
             	object.value="";
              }
         });
    	 //clear value
    	 angular.forEach($scope.requiredFields,function(object,index){
             if(object.label!=""){ 
             	object.value="";
              }
         });
    	 //clear value
    	 $scope.fingerPrint="";
    	
        if ($scope.packageandxml.length != 2) {
            return false;
        }
        if (!($scope.packageandxml[0].type == 'text/xml' || $scope.packageandxml[1].type == 'text/xml')) {
            return false;
        }
        
        if ($scope.packageandxml[0].type == 'text/xml') {
	 		var xFile= $scope.packageandxml[0];
	 	} else if  ($scope.packageandxml[1].type == 'text/xml'){
	 		var xFile = $scope.packageandxml[1];
	    }
    	
       
        
    	  var reader = new FileReader();
    	     // Closure to capture the file information.
    	        reader.onload = (function(theFile) {
    	          return function(e) {
    	        	 
    	        	  var parser=new DOMParser();
    	        	  var xmlDoc=parser.parseFromString(e.target.result,"text/xml");
    	        	  //console.log(xmlDoc);
    	        	  var nodes=xmlDoc.evaluate('/build_data/flex', xmlDoc, null, XPathResult.ANY_TYPE,null);
    	        	  var result=nodes.iterateNext();
    	        	  var flex = result.childNodes[0].nodeValue;
    	        	  var splitFlex=flex.split(".");
    	        	 if(splitFlex.length>5) {
    	        	  var hardware=splitFlex[4];
    	        	  var carrier=splitFlex[5];
    	        	  var language=splitFlex[6];
    	        	  var region=splitFlex[7];
    	        	 }
    	        	  
    	        	  var splitXML=(xFile.name).split(".");
    	        	  var flavour=splitXML[0];
    	        	  var tmajor=(splitXML[3].split("-"))[1];
    	        	  var tminor=splitXML[4];
    	        	  var tbuild=splitXML[5];
    	        	  var targetVersion=flavour+"."+tmajor+"."+tminor+"."+tbuild+"."+hardware+"."+carrier+"."+language+"."+region;
    	        	 
    	        //	  if (!angular.isUndefined($scope.requiredFields)) {
    	            	  
    	        		  $scope.requiredFields[0].value=flex;
    	        		  $scope.requiredFields[1].value=targetVersion;
    	        		 
    	        		  angular.forEach($scope.matchCriteria,function(object,index){
    	            		  if(object.label=="hwType"){
    	            			  $scope.matchCriteria[index].value=hardware;
    	            		  }
    	            		  else if(object.label=="carrier"){
    	            			  $scope.matchCriteria[index].value=carrier;
    	            		  }
    	            		  else if(object.label=="region"){
    	            			  $scope.matchCriteria[index].value=region;
    	            		  }
    	            	 });
    	        	  
    	        	  nodes=xmlDoc.evaluate('/build_data/fingerprint', xmlDoc, null, XPathResult.ANY_TYPE,null);
    	        	  result=nodes.iterateNext();
    	        	  var fingerprint = result.childNodes[0].nodeValue;
    	        	     $scope.fingerPrint=fingerprint;
    	        	     $scope.$apply();
    	          };
    	        })(xFile);

    	        // Read in the XML file as a text.
    	        reader.readAsText(xFile);
    	        return true;
    };
    $scope.$watch('packageandxml', function(newValue, oldValue) {
     	$scope.parseXmlValue();
  	});
  

    $rootScope.$on('upload:loadstart', function () {
        console.log('Controller: on `loadstart`');
    });

    $rootScope.$on('upload:error', function () {
        console.log('Controller: on `error`');
    });

    $rootScope.$on('upload:loadend', function () {
        console.log('Controller: on `loadend`');
    });

    $rootScope.$on('upload:abort', function () {
        console.log('Controller: on `abort`');
    });
    $rootScope.$on('upload:progress', function () {
        console.log('Controller: on `progress`');
    });

};

upgradescontrollers.controller('RootController', rc);
upgradescontrollers.controller('HomeController', hc);
upgradescontrollers.controller('DeviceEventsController', dec);
upgradescontrollers.controller('DeviceInfoController', dic);
upgradescontrollers.controller('MapReportsController', map);
upgradescontrollers.controller('AdminController', adm);
upgradescontrollers.controller('DeviceListsController', dlc);
upgradescontrollers.controller('ListController', lc);
upgradescontrollers.controller('SchedulerController', sc);
upgradescontrollers.controller('UpgradeOptionsController', uoc);
upgradescontrollers.controller('UploadController', uc);
upgradescontrollers.controller('JenkinsDialogController', tdc);
upgradescontrollers.controller('ListTargetsController', tc);
upgradescontrollers.controller('VerifyController', vc);

upgradescontrollers.controller('PathCompare', function ($scope, $rootScope, $dialog, $filter, PublishedPath, dialogService) {
	$scope.displayPublishedPath = function(){
	    $scope.pathdiff = PublishedPath.get({
            id: $scope.path.guid
        }, function(data, status, headers, config) {
            var title = 'Running version of this SUP with GUID: ' + $scope.pathdiff.guid;
            var left = $filter('json')($scope.pathdiff);
            var runningpath = angular.copy($scope.pathdiff);
            var right = JSON.stringify(data, null, 4);
            var dialogOptions = {
                closeButtonText: 'Dismiss',
                headerText: title,
                time: new Date(),
                bodyText: left,
                showCloseButton: true,
                showCallbackButton: false,
            };
            dialogService.showModalDialog({}, dialogOptions);
            return;
        }, function(data, status, headers, config) {
            if (data.status == 404) {
                var title = 'No live version!';
                var left = 'This SUP with GUID: ' + $scope.path.guid + ' is not published yet!  Please follow the approval and publish workflow to make this SUP live.';
                var runningpath = angular.copy($scope.path);
                var right = JSON.stringify(data, null, 4);
                var dialogOptions = {
                    closeButtonText: 'Dismiss',
                    headerText: title,
                    time: new Date(),
                    bodyText: left,
                    showCloseButton: true,
                    showCallbackButton: false,
                };
                dialogService.showModalDialog({}, dialogOptions);
            }
            return;
        });
    };
});
