#!/bin/bash
# ============================================================================
# PPIPilot - Batch Execution Test Script
# ============================================================================
# This script demonstrates how to run batch analysis from command line
#
# Usage:
#   1. Copy config_batch_template.json to config_batch.json
#   2. Edit config_batch.json with your settings
#   3. Make this script executable: chmod +x run_batch_test.sh
#   4. Run this script: ./run_batch_test.sh
# ============================================================================

echo ""
echo "================================================================================"
echo "PPIPilot - Batch Execution CLI"
echo "================================================================================"
echo ""

# Check if config file exists
if [ ! -f "config_batch.json" ]; then
    echo "[ERROR] Configuration file not found: config_batch.json"
    echo ""
    echo "Please create config_batch.json from the template:"
    echo "  cp config_batch_template.json config_batch.json"
    echo ""
    echo "Then edit config_batch.json with your settings."
    echo ""
    exit 1
fi

echo "[INFO] Configuration file found: config_batch.json"
echo ""

# Display configuration (first 20 lines)
echo "[INFO] Configuration preview:"
echo "--------------------------------------------------------------------------------"
head -n 20 config_batch.json
echo "--------------------------------------------------------------------------------"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with this configuration? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo ""
    echo "[INFO] Execution cancelled by user."
    exit 0
fi

echo ""
echo "[INFO] Starting batch execution..."
echo ""

# Run the batch analysis
python interface_batch_cli.py config_batch.json

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "[SUCCESS] Batch execution completed successfully!"
    echo "================================================================================"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "[ERROR] Batch execution failed with error code: $?"
    echo "================================================================================"
    echo ""
    echo "Please check the execution log for details."
    echo ""
    exit 1
fi
