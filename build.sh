#!/bin/sh
# Generates the Xcode project and compiles everything for the simulator (no signing needed).
# The full output goes to build.log.
cd "$(dirname "$0")"
{
    command -v xcodegen >/dev/null || brew install xcodegen
    xcodegen && xcodebuild -project GymLog.xcodeproj -scheme GymLog \
        -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
} > build.log 2>&1
grep -E "error:|BUILD (SUCCEEDED|FAILED)" build.log | sort -u
