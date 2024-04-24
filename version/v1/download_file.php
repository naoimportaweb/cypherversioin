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

    $path_file_upload_version = $path_file_upload . "/content/";

    $contentfile_data = "";
    if( $data["version"] == "" ) {
        $versions = scandir($path_file_upload_version, SCANDIR_SORT_DESCENDING);

        $contentfile = fopen( $path_file_upload_version . "/" . $versions[ 0 ] , "rb") or die("Unable to open file!");
        $contentfile_data = fread($contentfile,filesize($path_file_upload_version . "/" . $versions[ 0 ]));
        fclose($contentfile);
    } else {
        $contentfile = fopen( $path_file_upload_version . "/" . $data["version"] , "rb") or die("Unable to open file!");
        $contentfile_data = fread($contentfile,filesize($path_file_upload_version . "/" . $data["version"]));
        fclose($contentfile);
    }

    $infofile = fopen( $path_file_upload . "/description/info.json" , "r") or die("Unable to open file!");
    $infofile_data = fread($infofile,filesize($path_file_upload . "/description/info.json"));
    fclose($infofile);


    return array("status" => 1, "info" => $infofile_data, "content" => $contentfile_data);

}

?>