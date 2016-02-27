	// create the module and name it scotchApp
	var scotchApp = angular.module('scotchApp', ['ngRoute']);

	// configure our routes
	scotchApp.config(function($routeProvider) {
		$routeProvider

			// route for the home page
			.when('/', {
				templateUrl : 'static/pages/home.html',
				controller  : 'mainController'
			})

			// route for the about page
			.when('/about', {
				templateUrl : 'static/pages/about.html',
				controller  : 'aboutController'
			})

			// route for the contact page
			.when('/contact', {
				templateUrl : 'static/pages/contact.html',
				controller  : 'contactController'
			})

			.when('/seeds', {
				templateUrl : 'static/pages/seeds.html',
				controller  : 'seedsController'
			})

			.when('/scans', {
				templateUrl : 'static/pages/scans.html',
				controller  : 'scansController'
			})

			.when('/dnskeys', {
				templateUrl : 'static/pages/dnskeys.html',
				controller  : 'dnskeysController'
			});
	});

	// create the controller and inject Angular's $scope
	scotchApp.controller('mainController', function($scope) {
		// create a message to display in our view
		$scope.message = 'Everyone come and see how good I look!';
	});

	scotchApp.controller('aboutController', function($scope) {
		$scope.message = 'Look! I am an about page.';
	});

	scotchApp.controller('contactController', function($scope) {
		$scope.message = 'Contact us! JK. This is just a demo.';
	});

	scotchApp.controller('seedsController', function($scope, $http) {
		$scope.searchCriteria = '';

		$scope.fetchSeeds = function () {
            $http.get('/seeds?' + "filter=" + $scope.searchCriteria)
        	.then(function (response) {$scope.seeds = response.data.data;});
        };

		$scope.fetchSeeds();
	});

	scotchApp.controller('scansController', function($scope, $http) {
		$scope.fetchScans = function () {
            $http.get('/scans_history')
        	.then(function (response) {$scope.scans = response.data.data;});
        };

		$scope.fetchScans();
	});

	scotchApp.controller('dnskeysController', function($scope, $http) {
		$scope.searchCriteria = '';

		$scope.fetchDNSKeys = function () {
            $http.get('/dnskey?' + "filter=" + $scope.searchCriteria)
        	.then(function (response) {$scope.dnskeys = response.data.data;});
        };

		$scope.fetchDNSKeys();
	});