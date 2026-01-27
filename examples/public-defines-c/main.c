#include <stdio.h>

#include "lib.h"

int main(void) {
#ifdef LIB_PUBLIC_VERSION_MAJOR
#ifdef LIB_PUBLIC_VERSION_MINOR
    printf("Application sees library version: %d.%d\n", LIB_PUBLIC_VERSION_MAJOR, LIB_PUBLIC_VERSION_MINOR);
#else
    printf("Application sees library version: %d\n", LIB_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Application cannot see library version\n");
#endif

#ifdef LIB_PUBLIC_FEATURE_ENABLED
    printf("Public feature is enabled\n");
#else
    printf("Public feature is disabled\n");
#endif

#ifdef LIB_INTERNAL_DEBUG
    printf("ERROR: Application should not see internal defines!\n");
#else
    printf("Correct: Application does not see internal defines\n");
#endif

    int version = get_lib_version();
    int value = get_internal_value();

    printf("Library returned version: %d, value: %d\n", version, value);

    return 0;
}
