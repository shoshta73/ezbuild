#include <stdio.h>

#include "lib1.h"
#include "lib2.h"

int main(void) {
#ifdef LIB1_PUBLIC_VERSION_MAJOR
#ifdef LIB1_PUBLIC_VERSION_MINOR
    printf("Application sees lib1 version: %d.%d\n", LIB1_PUBLIC_VERSION_MAJOR, LIB1_PUBLIC_VERSION_MINOR);
#else
    printf("Application sees lib1 version: %d\n", LIB1_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Application cannot see lib1 version\n");
#endif

#ifdef LIB2_PUBLIC_VERSION_MAJOR
#ifdef LIB2_PUBLIC_VERSION_MINOR
    printf("Application sees lib2 version: %d.%d\n", LIB2_PUBLIC_VERSION_MAJOR, LIB2_PUBLIC_VERSION_MINOR);
#else
    printf("Application sees lib2 version: %d\n", LIB2_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Application cannot see lib2 version\n");
#endif

#ifdef LIB1_PUBLIC_FEATURE_ENABLED
    printf("Lib1 public feature enabled\n");
#else
    printf("Lib1 public feature disabled\n");
#endif

#ifdef LIB2_PUBLIC_FEATURE_ENABLED
    printf("Lib2 public feature enabled\n");
#else
    printf("Lib2 public feature disabled\n");
#endif

#ifdef LIB1_INTERNAL_DEBUG
    printf("ERROR: Application sees lib1 internal define!\n");
#else
    printf("Correct: Application does not see lib1 internal defines\n");
#endif

#ifdef LIB2_INTERNAL_DEBUG
    printf("ERROR: Application sees lib2 internal define!\n");
#else
    printf("Correct: Application does not see lib2 internal defines\n");
#endif

    int version1 = lib1_get_version();
    int version2 = lib2_get_version();
    int value1 = lib1_internal_value();
    int value2 = lib2_internal_value();

    printf("Total: %d\n", version1 + version2 + value1 + value2);

    return 0;
}
