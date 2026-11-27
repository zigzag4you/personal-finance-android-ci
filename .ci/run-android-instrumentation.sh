#!/usr/bin/env bash
set -euo pipefail
set +x

adb devices
adb -s "$ANDROID_SERIAL" shell getprop ro.build.version.sdk

echo "Pre-install PackageManager readiness check:"
package_manager_ready=0
for attempt in 1 2 3 4 5 6; do
  if adb -s "$ANDROID_SERIAL" shell cmd package list packages >/dev/null 2>&1; then
    package_manager_ready=1
    echo "PackageManager is responsive (attempt $attempt)."
    break
  fi
  echo "PackageManager not responsive yet (attempt $attempt/6)."
  sleep 5
done

echo "Pre-test service and resource snapshot:"
adb -s "$ANDROID_SERIAL" shell service list 2>&1 | grep -Ei 'package|activity' | head -n 40 || true
adb -s "$ANDROID_SERIAL" shell dumpsys meminfo 2>&1 | sed -n '1,70p' || true
adb -s "$ANDROID_SERIAL" shell df -h /data 2>&1 || true

if [[ "$package_manager_ready" -ne 1 ]]; then
  echo "::error::Android PackageManager did not become responsive after emulator boot; instrumentation will not be reported as an app test failure."
  adb -s "$ANDROID_SERIAL" logcat -d -b crash -b system -t 2500 2>&1 | grep -Ei 'FATAL EXCEPTION|system_server|PackageManager|OutOfMemory|low memory|lmkd|watchdog|service.*package' | tail -n 200 || true
  exit 86
fi

set +e
bash ./gradlew :app:connectedDebugAndroidTest --no-daemon --no-build-cache --stacktrace --info
gradle_status=$?
set -e

echo "Android instrumentation Gradle exit code: $gradle_status"
echo "Bounded emulator system diagnostics before emulator shutdown:"
adb devices -l || true
adb -s "$ANDROID_SERIAL" logcat -d -b crash -b system -t 2500 2>&1 | grep -Ei 'FATAL EXCEPTION|system_server|PackageManager|Broken pipe|OutOfMemory|low memory|lmkd|watchdog|INSTALL_FAILED|install.*failed|dex2oat' | tail -n 160 || true
adb -s "$ANDROID_SERIAL" shell dumpsys meminfo 2>&1 | sed -n '1,80p' || true
adb -s "$ANDROID_SERIAL" shell df -h /data 2>&1 || true
exit "$gradle_status"
