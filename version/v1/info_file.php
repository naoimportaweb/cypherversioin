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

    
    if(!file_exists($path_file_upload . "/description/info.json")){
        return array("status" => 1, "info" => array("name" => $data["name"], "versions" => array()));
    
    }
    
    $infofile = fopen( $path_file_upload . "/description/info.json" , "r") or die("Unable to open file!");
    $infofile_data = json_decode( fread($infofile,filesize($path_file_upload . "/description/info.json")), true);
    fclose($infofile);

    $infofile_data['versions'] = [];

    $list_versons = scandir($path_file_upload . "/versions/");
    for($i = 0; $i < count($list_versons); $i++){
        if(is_dir(  $path_file_upload . "/versions/" .  $list_versons[$i]  )){
            continue;
        }
        $buffer_version = fopen( $path_file_upload . "/versions/" .  $list_versons[$i], "r") or die("Unable to open file!");
        $buffer_version_data = json_decode( fread($buffer_version,filesize(  $path_file_upload . "/versions/" .  $list_versons[$i]   )), true);
        fclose($buffer_version);
        array_push( $infofile_data['versions'] , $buffer_version_data);
    }
    

    return array("status" => 1, "info" => $infofile_data);

}

?>