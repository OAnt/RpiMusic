'use strict'

//controllers

function SongSelectionCtrl($scope, $http){
    $scope.artists = [];
    $scope.albums = [];
    $scope.songs = [];
    
    $scope.playSong = function(songDetails) {
        var url = '/music/' + songDetails[3] + '/' + songDetails[2] + '/' + songDetails[0]
        $http.post(url, songDetails)
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

    var init = function () {
        $http.get('/music').success(function(data) {
            $scope.artists = data;
        });
    }
    init();
}
