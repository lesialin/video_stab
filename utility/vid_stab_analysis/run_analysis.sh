LOG_DIR=$1

if [[ $# -ne 1 ]]; then
    echo "Please enter: ./run_vid_stab.sh log_dir"
    exit 2
fi

./grep_log.sh $LOG_DIR
python3 run_analysis.py $LOG_DIR