@echo off
REM Test script for City Insights API using curl (Windows)
REM Makes it easy to test the API endpoint

set API_BASE=http://localhost:8012

echo ======================================================================
echo Testing City Insights API
echo ======================================================================

REM Test 1: Health check
echo.
echo Test 1: Health Check
echo ----------------------------------------------------------------------
curl -s "%API_BASE%/health"
echo.

REM Test 2: API info
echo.
echo Test 2: API Info
echo ----------------------------------------------------------------------
curl -s "%API_BASE%/"
echo.

REM Test 3: City Insights Analysis - Bristol with criteria
echo.
echo Test 3: Analyze Bristol with success criteria
echo ----------------------------------------------------------------------
curl -X POST "%API_BASE%/api/analyze/city-insights" ^
    -H "Content-Type: application/json" ^
    -d "{\"city\": \"Bristol\", \"country_code\": \"GB\", \"success_criteria\": \"Achieve net zero by 2030 through renewable energy\"}"
echo.

REM Test 4: City Insights Analysis - Bristol without criteria
echo.
echo Test 4: Analyze Bristol without explicit success criteria
echo ----------------------------------------------------------------------
curl -X POST "%API_BASE%/api/analyze/city-insights" ^
    -H "Content-Type: application/json" ^
    -d "{\"city\": \"Bristol\", \"country_code\": \"GB\"}"
echo.

echo.
echo ======================================================================
echo Tests Complete
echo ======================================================================
pause
