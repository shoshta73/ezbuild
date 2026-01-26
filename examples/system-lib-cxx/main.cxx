#include <iostream>
#include <curl/curl.h>

int main() {
    std::cout << "libcurl version: " << curl_version() << std::endl;
    return 0;
}
