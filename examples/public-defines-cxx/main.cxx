#include <iostream>

#include "lib.hxx"

int main() {
#ifdef LIB_PUBLIC_VERSION_MAJOR
#ifdef LIB_PUBLIC_VERSION_MINOR
    std::cout << "Application sees library version: " << LIB_PUBLIC_VERSION_MAJOR
              << "." << LIB_PUBLIC_VERSION_MINOR << std::endl;
#else
    std::cout << "Application sees library version: " << LIB_PUBLIC_VERSION_MAJOR
              << std::endl;
#endif
#else
    std::cout << "Application cannot see library version" << std::endl;
#endif

#ifdef LIB_PUBLIC_FEATURE_ENABLED
    std::cout << "Public feature is enabled" << std::endl;
#else
    std::cout << "Public feature is disabled" << std::endl;
#endif

#ifdef LIB_INTERNAL_DEBUG
    std::cout << "ERROR: Application should not see internal defines!" << std::endl;
#else
    std::cout << "Correct: Application does not see internal defines" << std::endl;
#endif

    std::string version = getLibVersion();
    int value = getInternalValue();

    std::cout << "Library returned version: " << version << ", value: " << value
              << std::endl;

    return 0;
}
