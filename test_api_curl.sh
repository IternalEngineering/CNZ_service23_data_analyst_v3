#!/bin/bash
# Test script for City Insights API using curl
# Makes it easy to test the API endpoint

API_BASE="http://localhost:8012"

echo "======================================================================"
echo "Testing City Insights API"
echo "======================================================================"

# Test 1: Health check
echo ""
echo "Test 1: Health Check"
echo "----------------------------------------------------------------------"
curl -s "${API_BASE}/health" | python -m json.tool

# Test 2: API info
echo ""
echo "Test 2: API Info"
echo "----------------------------------------------------------------------"
curl -s "${API_BASE}/" | python -m json.tool

# Test 3: City Insights Analysis - Bristol
echo ""
echo "Test 3: Analyze Bristol with success criteria"
echo "----------------------------------------------------------------------"
curl -X POST "${API_BASE}/api/analyze/city-insights" \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB",
      "success_criteria": "Achieve net zero by 2030 through renewable energy"
    }' | python -m json.tool

# Test 4: City Insights Analysis - Bristol without criteria
echo ""
echo "Test 4: Analyze Bristol without explicit success criteria"
echo "----------------------------------------------------------------------"
curl -X POST "${API_BASE}/api/analyze/city-insights" \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB"
    }' | python -m json.tool

echo ""
echo "======================================================================"
echo "Tests Complete"
echo "======================================================================"
