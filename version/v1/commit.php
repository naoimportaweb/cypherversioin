<?php


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
    
    $now = DateTime::createFromFormat('U.u', microtime(true));
    $now_string = $now->format("ymdHisu");

    $myfile = fopen($path_commits . "/" . $now_string , "w") or die("Unable to open file!");
    fwrite($myfile, json_encode( $data['commit'] ) );
    fclose($myfile);


    return array("status" => 1, "commit" => $now_string);

}

?>