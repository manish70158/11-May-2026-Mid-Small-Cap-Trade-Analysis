#!/bin/bash
# Monitor progress of India stock screening

echo "📊 Monitoring India Midcap & Smallcap Stock Screening Progress"
echo "=============================================================="
echo ""

OUTPUT_FILE="comprehensive_screening_output.txt"

while true; do
    clear
    echo "📊 Monitoring India Midcap & Smallcap Stock Screening Progress"
    echo "=============================================================="
    echo ""
    echo "⏰ Started: $(date)"
    echo ""

    if [ -f "$OUTPUT_FILE" ]; then
        echo "📈 Recent Activity:"
        echo "──────────────────────────────────────────────────────────"
        tail -25 "$OUTPUT_FILE" | head -20
        echo ""
        echo "Press Ctrl+C to stop monitoring"
    else
        echo "⏳ Waiting for analysis to start..."
    fi

    sleep 5
done
