<?php
#require_once __DIR__ . "/config.php";


//https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-a-php-string/

function encrypt($text){
    global $CONFIG;

    $ciphering = $CONFIG['cypher']['ciphering'];
    $iv_length = openssl_cipher_iv_length($ciphering);
    $options = 0;
    return openssl_encrypt($text, $ciphering, $CONFIG['cypher']['key'], $options, $CONFIG['cypher']['iv']);
}   

function decrypt($text){
    global $CONFIG;

    $ciphering = $CONFIG['cypher']['ciphering'];
    $iv_length = openssl_cipher_iv_length($ciphering);
    $options = 0;
    return openssl_decrypt ($text, $ciphering, $CONFIG['cypher']['key'], $options, $CONFIG['cypher']['iv']);
}

?>