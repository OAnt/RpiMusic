'use strict';

var baseApp = angular.module('baseApp', ['ngRoute', "ngProgress","uiSlider", "ngResource"]);

baseApp.directive('well', function(){
    return {
        restrict: 'E',
        scope: {
            itemList: '=info',
            callback: '=callback',
            cssClass: '=cssClass'
        },
        templateUrl: 'static/well.html'
    }
});

baseApp.controller("SongSelectionCtrl",['$scope','$http', 'ngProgress', function ($scope, $http, ngProgress) {
    $scope.autoVolumeChangeInProgress = false;

    $scope.artists = [];
    $scope.albums = [];
    $scope.songs = [];
    $scope.lists = [];
    $scope.cssRow = "col-xs-3 col-sm-3 col-md-3";
    $scope.showArtist = true;
    $scope.output = null; 
    $scope.metadata = new Object(null);
    $scope.paused = false;
    $scope.songList = new Object(null);
    $scope.volume = null;
    var baseUrl = document.URL;

    var ws = new WebSocket("ws://" + document.domain + ":5000/api");
    ws.onopen = function() {
        $scope.$watch('volume', function() {
            if (!$scope.autoVolumeChangeInProgress && $scope.volume != "NaN") {
                ws.send("volume:" + parseInt($scope.volume) + "\n");
            }
        });
    }

    $scope.playSong = function(songDetails) {
        var url = baseUrl + 'music/' + songDetails[3] + '/' + songDetails[2] + '/' + songDetails[0];
        $http.post(url, songDetails);
    }

    $scope.createList = function() {
        var url = baseUrl + 'list';
        var song_id_list = [];
        console.log($scope.songList);
        for(var i=0; i<$scope.songList.list.length;i++){
            song_id_list.push($scope.songList.list[i].id);
        }
        $http.post(url, {name: 'aList', songs: song_id_list});
    }

    $scope.getLists = function() {
        $http.get(baseUrl + 'list').success(function(data){
            $scope.lists = data;
        });
    }

    $scope.getList = function(aList) {
        $http.post(baseUrl + 'list/' + aList[0]);
    }

    $scope.getArtists = function() {
        $http.get(baseUrl + 'music').success(function(data) {
            $scope.artists = data;
        });
    }

    $scope.getSongs = function(albumDetails){
        $http.get(baseUrl + 'music/' + albumDetails[2] + '/' + albumDetails[0]).success(function(data){
            $scope.songs = data;
        });
    }

    $scope.getAlbums = function(artistDetails) {
        $http.get(baseUrl + 'music/' + artistDetails[0]).success(function(data) {
            $scope.albums = data;
        });
    }

    $scope.toggleArtists = function(){
        $scope.showArtist = true;
        $scope.getArtists();
    }

    $scope.toggleLists = function(){
        $scope.showArtist = false;
        $scope.getLists();
    }

    $scope.pause_unpause = function() {
        $http.get(baseUrl + 'player/pause');
    }

    $scope.nextSong = function() {
        $http.get(baseUrl + 'player/next');
    }

    $scope.prevSong = function(){
        $http.get(baseUrl + 'player/previous');
    }

    var mplayerParse = function(socketOutput) {
        switch(socketOutput.message)
        {
        case "ANS_PERCENT_POSITION":
            $scope.output = socketOutput.value;
            ngProgress.set(parseInt(socketOutput.value));
            break;
        case "Title":
        case "ANS_META_TITLE":
            $scope.metadata.title = socketOutput.value;
            break;
        case "Artist":
        case "ANS_META_ARTIST":
            $scope.metadata.artist = socketOutput.value;
            break;
        case "Album":
        case "ANS_META_ALBUM":
            $scope.metadata.album = socketOutput.value;
            break;
        case "ANS_pause":
            if (socketOutput.value == "yes") {
                $scope.paused = true;
            } else {
                $scope.paused = false;
            }
            break;
        case "list":
            $scope.songList.list = socketOutput.value;
            break;
        case "index":
            $scope.songList.index = socketOutput.value;
            break;
        case "ANS_volume":
            $scope.autoVolumeChangeInProgress = true;
            $scope.volume = socketOutput.value;
            break;
        default:
            console.log("Unknown: %s", socketOutput.message);
        }
        $scope.$apply();

        $scope.autoVolumeChangeInProgress = false;
    }

    var init = function () {
        $scope.getArtists();
        ws.onmessage = function(msg) {
            console.log("Received message: %s", msg.data);
            mplayerParse(JSON.parse(msg.data));
        }
    }
    init();
}]);
