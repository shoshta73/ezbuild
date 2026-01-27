#include <iostream>
#include <string>

#define LIB_INTERNAL_DEBUG 1
#define LIB_PUBLIC_VERSION_MAJOR 2
#define LIB_PUBLIC_VERSION_MINOR 5

std::string getLibVersion() {
#ifdef LIB_PUBLIC_VERSION_MAJOR
#ifdef LIB_PUBLIC_VERSION_MINOR
    std::cout << "Library version: " << LIB_PUBLIC_VERSION_MAJOR << "."
              << LIB_PUBLIC_VERSION_MINOR << std::endl;
#else
    std::cout << "Library version: " << LIB_PUBLIC_VERSION_MAJOR << std::endl;
#endif
#else
    std::cout << "Library version: unknown" << std::endl;
#endif

#ifdef LIB_INTERNAL_DEBUG
    std::cout << "Internal debug mode enabled" << std::endl;
#endif

    return "2.5";
}

int getInternalValue() {
    return 42;
}
