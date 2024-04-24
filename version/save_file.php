<?php
ini_set('upload_max_filesize', '100M');
ini_set('post_max_size', '100M');

require_once dirname(__DIR__) . "/api/config.php";
require_once dirname(__DIR__) . "/api/functions.php";

$data = json_decode( decrypt( file_get_contents('php://input') ), true);

// {"cypher_version" : "1", "action_version" : "1", "project" : "cifrado", "name" : "cifrado", "content" : "cifrado"}
require_once __DIR__ . "/v". $data['action_version'] ."/save_file.php";

echo encrypt(  json_encode( execute( $data ) ) );


?>