#include <iostream>
#include <string>

int main() {
#ifdef DEBUG
    std::cout << "Debug mode is ON" << std::endl;
#else
    std::cout << "Debug mode is OFF" << std::endl;
#endif

#ifdef VERSION_MAJOR
#ifdef VERSION_MINOR
    std::cout << "Version: " << VERSION_MAJOR << "." << VERSION_MINOR << std::endl;
#else
    std::cout << "Version: " << VERSION_MAJOR << std::endl;
#endif
#else
    std::cout << "Version not defined" << std::endl;
#endif

#if defined(FEATURE_ENABLED) && defined(DEBUG)
    std::cout << "Feature is enabled in debug mode" << std::endl;
#elif defined(FEATURE_ENABLED)
    std::cout << "Feature is enabled in release mode" << std::endl;
#else
    std::cout << "Feature is disabled" << std::endl;
#endif

    return 0;
}
