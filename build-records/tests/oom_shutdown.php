<?php
// A patched hard OOM must terminate before user shutdown/destructor callbacks.
register_shutdown_function(function () {
    echo "UNSAFE_SHUTDOWN_CALLBACK\n";
});
$allocation = str_repeat('x', 32 * 1024 * 1024);
echo "UNEXPECTED_SUCCESS\n";
