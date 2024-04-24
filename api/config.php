<?php

$ROOT = dirname(__DIR__);
$CONFIG = json_decode(file_get_contents( $ROOT . "/data/config.json"  ), true); 

if ($CONFIG['src_foler'] == "") {
    $CONFIG['src_foler'] = dirname(__DIR__) . "/projects";
}

if(!file_exists($CONFIG['src_foler'])){
    mkdir($CONFIG['src_foler']);
}

$CONFIG['cypher'] = $CONFIG["cypher_v1"];

?>