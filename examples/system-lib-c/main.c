#include <stdio.h>
#include <curl/curl.h>

int main() {
    printf("libcurl version: %s\n", curl_version());
    return 0;
}
