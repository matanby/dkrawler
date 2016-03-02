'use strict';

// create the module and name it scotchApp
var app = angular.module('scotchApp', ['ngRoute']);

app.filter('cut', function () {
	return function (value, wordwise, max, tail) {
		if (!value) return '';

		max = parseInt(max, 10);
		if (!max) return value;
		if (value.length <= max) return value;

		value = value.substr(0, max);
		if (wordwise) {
			var lastspace = value.lastIndexOf(' ');
			if (lastspace != -1) {
				value = value.substr(0, lastspace);
			}
		}

		return value + (tail || ' …');
	};
});

// configure our routes
app.config(function($routeProvider) {
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

		// route for the seeds page
		.when('/seeds', {
			templateUrl : 'static/pages/seeds.html',
			controller  : 'seedsController'
		})

		// route for the scans history page
		.when('/scans', {
			templateUrl : 'static/pages/scans.html',
			controller  : 'scansController'
		})

		// route for the DNS Keys page
		.when('/dnskeys', {
			templateUrl : 'static/pages/dnskeys.html',
			controller  : 'dnskeysController'
		})

		// route for the key lengths report page
		.when('/key_lengths', {
			templateUrl : 'static/pages/key_lengths.html',
			controller  : 'keyLengthsController'
		})

		// route for the duplicate moduli report page
		.when('/duplicate_moduli', {
			templateUrl : 'static/pages/duplicate_moduli.html',
			controller  : 'duplicateModuliController'
		})

		// route for the factorable moduli report page
		.when('/factorable_moduli', {
			templateUrl : 'static/pages/factorable_moduli.html',
			controller  : 'factorableModuliController'
		});
});

app.controller('mainController', function($scope, $http) {
	$scope.fetchStatus = function () {
		$http.get('/status')
			.then(function (response) {$scope.status = response.data.data;});
	};

	$scope.fetchStatus();
});

app.controller('aboutController', function($scope, $http) {
});

app.controller('seedsController', function($scope, $http) {
	$scope.searchCriteria = '';

	$scope.fetchSeeds = function () {
		$http.get('/seeds?' + "filter=" + $scope.searchCriteria)
			.then(function (response) {$scope.seeds = response.data.data;});
	};

	$scope.fetchSeeds();
});

app.controller('scansController', function($scope, $http) {
	$scope.fetchScans = function () {
		$http.get('/scans_history')
			.then(function (response) {$scope.scans = response.data.data;});
	};

	if (! $scope.scans)
		$scope.fetchScans();
});

app.controller('dnskeysController', function($scope, $http) {
	$scope.searchCriteria = '';

	$scope.fetchDNSKeys = function () {
		$http.get('/dnskey?' + "filter=" + $scope.searchCriteria)
			.then(function (response) {$scope.dnskeys = response.data.data;});
	};

	$scope.fetchDNSKeys();
});

app.controller('keyLengthsController', function($scope, $http) {
	$scope.fetchKeyLengthsReport = function () {
		$http.get('/reports/key_lengths')
			.then(function (response) {
				$scope.creation_time = response.data.data.creation_time;
				$scope.n_lengths = response.data.data.n_lengths;
			});
	};

	$scope.fetchKeyLengthsReport();
});

app.controller('duplicateModuliController', function($scope, $http) {
	$scope.fetchDuplicateModuli = function () {
		$http.get('/reports/duplicate_moduli')
			.then(function (response) {
				$scope.dnskeys = response.data.data;
				$scope.creation_time = response.data.data.creation_time;
				$scope.duplicates = response.data.data.duplicates;
			});
	};

	$scope.selectN = function(N, domains) {
		$scope.selectedN = N;
		$scope.selectedDomains = domains;
	};

	$scope.fetchDuplicateModuli();
});

app.controller('factorableModuliController', function($scope, $http) {
	$scope.fetchDNSKeys = function () {
		$http.get('/reports/factorable_moduli')
			.then(function (response) {
				$scope.creation_time = response.data.data.creation_time;
				$scope.factorableModuli = response.data.data.results;
			});
	};

	$scope.fetchDNSKeys();
});