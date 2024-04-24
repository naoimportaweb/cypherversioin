<?php
require_once dirname(__DIR__) . "/api/config.php";
require_once dirname(__DIR__) . "/api/functions.php";

$data = json_decode( decrypt( file_get_contents('php://input') ), true);

// {"cypher_version" : "1", "action_version" : "1", "project" : "aaaabbbbbcccccddddd"}
require_once __DIR__ . "/v". $data['action_version'] ."/commit_list.php";

echo encrypt(  json_encode( execute( $data ) ) );


?>