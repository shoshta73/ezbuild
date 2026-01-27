#include <stdio.h>

#define LIB2_INTERNAL_DEBUG 1

int lib2_get_version(void) {
#ifdef LIB2_PUBLIC_VERSION_MAJOR
#ifdef LIB2_PUBLIC_VERSION_MINOR
    printf("Lib2 version: %d.%d\n", LIB2_PUBLIC_VERSION_MAJOR, LIB2_PUBLIC_VERSION_MINOR);
#else
    printf("Lib2 version: %d\n", LIB2_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Lib2 version: unknown\n");
#endif

#ifdef LIB2_INTERNAL_DEBUG
    printf("Lib2 internal debug enabled\n");
#endif

    return 200;
}

int lib2_internal_value(void) {
    return 2;
}
