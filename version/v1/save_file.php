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
    $path_files = $path_project . "/files";
    $path_file_upload = $path_files . "/" . str_replace("/", "", $data["name"]);
    if(!file_exists($path_file_upload)){
        mkdir($path_file_upload);
    }

    if(!file_exists($path_file_upload . "/content")){
        mkdir($path_file_upload . "/content");
    }

    if(!file_exists($path_file_upload . "/versions")){
        mkdir($path_file_upload . "/versions");
    }

    if(!file_exists($path_file_upload . "/description")){
        mkdir($path_file_upload . "/description");
    }

    $now = DateTime::createFromFormat('U.u', microtime(true));
    $now_string = $now->format("ymdHisu");
    $path_file_upload_version = $path_file_upload . "/content/" . $now_string;

    error_log($path_file_upload_version, 0);

    $myfile = fopen($path_file_upload_version , "wb") or die("Unable to open file!");
    fwrite($myfile, $data["content"]);
    fclose($myfile);

    if(!file_exists($path_file_upload . "/description/info.json")){
        $myfile = fopen($path_file_upload . "/description/info.json" , "w") or die("Unable to open file!");
        fwrite($myfile, json_encode( array("name" => $data["name"])  ) );
        fclose($myfile);
    }

    $myfile = fopen($path_file_upload . "/versions/" . $now_string , "w") or die("Unable to open file!");
    fwrite($myfile, json_encode( array("name" => $now_string, "md5" => $data["md5"])  ) );
    fclose($myfile);

    return array("status" => 1, "version" => $now_string );

}

?>