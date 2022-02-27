#define HACK_LENGTH(data) \
    []() -> long { \
        constexpr auto n = sizeof(data)/sizeof(data[0]); \
        return n; \
    }()
