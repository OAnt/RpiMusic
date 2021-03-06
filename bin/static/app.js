var myApp = angular.module('myApp', ["ngProgress"]);

myApp.controller("SongSelectionCtrl", function ($scope, $http, ngProgress) {
    $scope.artists = [];
    $scope.albums = [];
    $scope.songs = [];
    $scope.output = null; 
    $scope.metadata = new Object(null);

    $scope.playSong = function(songDetails) {
        var url = '/music/' + songDetails[3] + '/' + songDetails[2] + '/' + songDetails[0]
        $http.post(url, songDetails);
    }

    $scope.getSongs = function(albumDetails){
        $http.get('/music/' + albumDetails[2] + '/' + albumDetails[0]).success(function(data){
            $scope.songs = data;
        });
    }

    $scope.getAlbums = function(artistDetails) {
        $http.get('/music/' + artistDetails[0]).success(function(data) {
            $scope.albums = data;
        });
    }

    $scope.pause_unpause = function() {
        $http.get('/player/pause');
    }

    $scope.nextSong = function() {
        $http.get('/player/next');
    }

    $scope.prevSong = function(){
        $http.get('/player/previous');
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
        default:
            console.log("Unknown: %s", socketOutput.message);
        }
        $scope.$apply();
    }

    var init = function () {
        $http.get('/music').success(function(data) {
            $scope.artists = data;
        });
        var ws = new WebSocket("ws://" + document.domain + ":5000/api");
        ws.onmessage = function(msg) {
            console.log("Received message: %s", msg.data);
            mplayerParse(JSON.parse(msg.data));
        }
    }
    init();
});
