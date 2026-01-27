#include <stdio.h>

#define LIB_INTERNAL_DEBUG 1
#define LIB_PUBLIC_VERSION_MAJOR 2
#define LIB_PUBLIC_VERSION_MINOR 5

int get_lib_version(void) {
#ifdef LIB_PUBLIC_VERSION_MAJOR
#ifdef LIB_PUBLIC_VERSION_MINOR
    printf("Library version: %d.%d\n", LIB_PUBLIC_VERSION_MAJOR, LIB_PUBLIC_VERSION_MINOR);
#else
    printf("Library version: %d\n", LIB_PUBLIC_VERSION_MAJOR);
#endif
#else
    printf("Library version: unknown\n");
#endif

#ifdef LIB_INTERNAL_DEBUG
    printf("Internal debug mode enabled\n");
#endif

    return 100;
}

int get_internal_value(void) {
    return 42;
}
