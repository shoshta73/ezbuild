#include <stdio.h>

#define LIB1_INTERNAL_DEBUG 1

int lib1_get_version(void) {
#ifdef LIB1_PUBLIC_VERSION_MAJOR
#ifdef LIB1_PUBLIC_VERSION_MINOR
    printf("Lib1 version: %d.%d\n", LIB1_PUBLIC_VERSION_MAJOR, LIB1_PUBLIC_VERSION_MINOR);
#else
    printf("Lib1 version: %d\n", LIB1_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Lib1 version: unknown\n");
#endif

#ifdef LIB1_INTERNAL_DEBUG
    printf("Lib1 internal debug enabled\n");
#endif

    return 100;
}

int lib1_internal_value(void) {
    return 1;
}
