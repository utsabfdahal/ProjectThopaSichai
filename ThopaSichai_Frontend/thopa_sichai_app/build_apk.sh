#!/bin/bash
# Build script for Thopa Sichai APK
# Run this script when connected to mobile hotspot

echo "🚀 Building Thopa Sichai APK..."
echo ""

# Check internet connectivity
echo "📡 Checking internet connectivity..."
if ! ping -c 1 google.com &> /dev/null; then
    echo "❌ No internet connection detected!"
    echo "Please connect to mobile hotspot and try again."
    exit 1
fi
echo "✅ Internet connected"
echo ""

# Clean previous build
echo "🧹 Cleaning previous build..."
flutter clean
echo ""

# Get dependencies
echo "📦 Getting dependencies..."
flutter pub get
echo ""

# Build release APK
echo "🔨 Building release APK..."
flutter build apk --release

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📱 APK Location:"
    echo "   build/app/outputs/flutter-apk/app-release.apk"
    echo ""
    echo "📊 APK Size:"
    ls -lh build/app/outputs/flutter-apk/app-release.apk | awk '{print "   " $5}'
    echo ""
    echo "🎉 You can now install this APK on your Android device!"
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the error messages above for details."
    exit 1
fi
