#include <stdio.h>

#ifdef HAVE_LIBCURL
#include <curl/curl.h>
#include <string.h>
#endif

size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    return size * nmemb;
}

void fetch_example() {
#ifdef HAVE_LIBCURL
    CURL *curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "https://example.com");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_NOBODY, 1L);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        
        CURLcode res = curl_easy_perform(curl);
        
        if (res == CURLE_OK) {
            long http_code = 0;
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
            printf("Successfully fetched example.com (HTTP %ld)\n", http_code);
        } else {
            printf("curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }
        
        curl_easy_cleanup(curl);
    }
#else
    printf("Cannot fetch example.com - libcurl not available\n");
#endif
}
