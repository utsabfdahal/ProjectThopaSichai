#!/bin/bash
# Comprehensive endpoint testing script

BASE_URL="http://localhost:8000/api"
PASS="\033[0;32m✓ PASS\033[0m"
FAIL="\033[0;31m✗ FAIL\033[0m"
INFO="\033[0;34mℹ INFO\033[0m"

echo "======================================================================"
echo "TESTING ALL API ENDPOINTS"
echo "======================================================================"

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_code="$5"
    
    echo ""
    echo "----------------------------------------------------------------------"
    echo "TEST: $name"
    echo "----------------------------------------------------------------------"
    echo "URL: $method $url"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$url")
    else
        echo "Data: $data"
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d':' -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')
    
    echo "Status: $http_code (expected: $expected_code)"
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "$PASS"
    else
        echo -e "$FAIL"
    fi
    
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
}

# 1. HEALTH CHECK
test_endpoint "Health Check" "GET" "$BASE_URL/health/" "" "200"

# 2. GET MOTORS (with nodeid)
test_endpoint "List All Motors" "GET" "$BASE_URL/motors/" "" "200"

# 3. SIMPLE MOTORS INFO
test_endpoint "Simple Motors Info (for motor controller)" "GET" "$BASE_URL/motorsinfo/" "" "200"

# 4. GET SYSTEM MODE
test_endpoint "Get Current System Mode" "GET" "$BASE_URL/mode/" "" "200"

# 5. SET TO AUTOMATIC MODE
test_endpoint "Set System to AUTOMATIC Mode" "POST" "$BASE_URL/mode/set/" '{"mode":"AUTOMATIC"}' "200"

# 6. SEND SENSOR DATA (sensor_zone1 - LOW moisture)
test_endpoint "Send LOW Moisture Data (sensor_zone1)" "POST" "$BASE_URL/data/receive/" \
    '{"nodeid":"sensor_zone1","value":25.0}' "201"

# 7. CHECK MOTORS INFO AFTER AUTOMATIC CONTROL
test_endpoint "Check Motors Info After Automatic Control" "GET" "$BASE_URL/motorsinfo/" "" "200"

# 8. SEND HIGH MOISTURE DATA
test_endpoint "Send HIGH Moisture Data (sensor_zone1)" "POST" "$BASE_URL/data/receive/" \
    '{"nodeid":"sensor_zone1","value":75.0}' "201"

# 9. CHECK MOTORS INFO AGAIN
test_endpoint "Check Motors Info After High Moisture" "GET" "$BASE_URL/motorsinfo/" "" "200"

# 10. SEND DATA FOR SENSOR_ZONE2
test_endpoint "Send Data for sensor_zone2" "POST" "$BASE_URL/data/receive/" \
    '{"nodeid":"sensor_zone2","value":20.0}' "201"

# 11. LIST SOIL MOISTURE DATA
test_endpoint "List Recent Sensor Readings" "GET" "$BASE_URL/data/?page=1&page_size=5" "" "200"

# 12. GET LATEST SENSOR DATA
test_endpoint "Get Latest Sensor Data" "GET" "$BASE_URL/data/latest/" "" "200"

# 13. GET THRESHOLDS
test_endpoint "Get Threshold Configuration" "GET" "$BASE_URL/config/thresholds/" "" "200"

# 14. GET SYSTEM STATUS
test_endpoint "Get System Status" "GET" "$BASE_URL/status/" "" "200"

# 15. GET DASHBOARD STATS
test_endpoint "Get Dashboard Statistics" "GET" "$BASE_URL/stats/dashboard/" "" "200"

# 16. MANUAL MOTOR CONTROL (Set to MANUAL first)
test_endpoint "Set System to MANUAL Mode" "POST" "$BASE_URL/mode/set/" '{"mode":"MANUAL"}' "200"

# 17. CONTROL SPECIFIC MOTOR
test_endpoint "Turn Motor ON Manually (Motor ID 1)" "POST" "$BASE_URL/motors/1/control/" \
    '{"state":"ON"}' "200"

# 18. CREATE NEW MOTOR
test_endpoint "Create New Motor with nodeid" "POST" "$BASE_URL/motors/" \
    '{"name":"Test Motor","nodeid":"test_sensor_01","state":"OFF"}' "201"

# 19. GET SPECIFIC MOTOR DETAILS
test_endpoint "Get Specific Motor Details (ID 1)" "GET" "$BASE_URL/motors/1/" "" "200"

# 20. FILTERED SENSOR DATA
test_endpoint "Get Filtered Sensor Data" "GET" "$BASE_URL/data/filtered/?nodeid=sensor_zone1&limit=3" "" "200"

# Summary
echo ""
echo "======================================================================"
echo "TEST SUMMARY"
echo "======================================================================"
echo "All endpoint tests completed!"
echo ""
echo "Key Endpoints for ESP32:"
echo "  - POST $BASE_URL/data/receive/       (Sensor data submission)"
echo "  - GET  $BASE_URL/motorsinfo/         (Motor controller polling)"
echo ""
echo "Management Endpoints:"
echo "  - GET/POST $BASE_URL/motors/         (Motor management)"
echo "  - POST $BASE_URL/mode/set/           (AUTOMATIC/MANUAL mode)"
echo "  - GET  $BASE_URL/status/             (System status)"
echo "======================================================================"
