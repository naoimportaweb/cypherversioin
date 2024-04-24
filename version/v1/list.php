<?php

function arquivojson($path){
    $commitfile = fopen( $path , "r") or die("Unable to open file!");
    $commit_data = fread($commitfile,filesize( $path ));
    fclose($commitfile);
    return json_decode($commit_data, true);
}

function execute($data){
    global $CONFIG;

    if(!file_exists($CONFIG["src_foler"])){
        mkdir($CONFIG["src_foler"]);
    }

    $path_project = $CONFIG["src_foler"] . "/" . str_replace("/", "", $data["project"] ) ;
    if(!file_exists($path_project)){
        mkdir($path_project);
        mkdir($path_project . "/files");
    
    }
    
    $path_project = $CONFIG["src_foler"] . "/" . str_replace("/", "", $data["project"] ) ;
    $path_commits = $path_project . "/commits";
    if(!file_exists($path_commits)){
        mkdir($path_commits);
    }

    $commits = scandir($path_commits , SCANDIR_SORT_DESCENDING);

    $commitfile = fopen($path_commits . '/' . $commits[0] , "r") or die("Unable to open file!");
    $commit_data = fread($commitfile,filesize($path_commits . '/' . $commits[0] ));
    fclose($commitfile);

    $commits_json = json_decode($commit_data, true);
    for($i = 0; $i < count($commits_json['files']); $i++){
        if( ! array_key_exists("md5", $commits_json['files'][$i]) ){
            $commits_json['files'][$i]['md5'] =  arquivojson(   $path_project . '/files/' . str_replace("/", "", $commits_json['files'][$i]['name']) . "/versions/" .  $commits_json['files'][$i]['version']  )['md5'];
        }
    }

    //message
    $commits = scandir($path_commits);
    $commits_return = [];
    for($i = 0; $i < count($commits); $i++){
        $commitfile = fopen($path_commits . '/' . $commits[$i] , "r") or die("Unable to open file!");
        $commit_data = fread($commitfile,filesize($path_commits . '/' . $commits[$i] ));
        fclose($commitfile);

        if( json_decode($commit_data, true)['message'] != "" ){
            array_push($commits_return, array("name" => $commits[$i], "comment" => json_decode($commit_data, true)['message'], "files" => json_decode($commit_data, true)['files'] ));
        }
    }




    return array("status" => 1, "files" => $commits_json['files'], "commits" => $commits_return);
}

?>