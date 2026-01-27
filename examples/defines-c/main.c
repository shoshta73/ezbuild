#include <stdio.h>

int main(void) {
#ifdef DEBUG
    printf("Debug mode is ON\n");
#else
    printf("Debug mode is OFF\n");
#endif

#ifdef VERSION_MAJOR
#ifdef VERSION_MINOR
    printf("Version: %d.%d\n", VERSION_MAJOR, VERSION_MINOR);
#else
    printf("Version: %d\n", VERSION_MAJOR);
#endif
#else
    printf("Version not defined\n");
#endif

#ifdef FEATURE_ENABLED
    printf("Feature is enabled\n");
#else
    printf("Feature is disabled\n");
#endif

    return 0;
}
