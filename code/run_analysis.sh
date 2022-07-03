LOG_DIR=$1

if [[ $# -ne 1 ]]; then
    echo "Please enter: ./run_vid_stab.sh log_dir"
    exit 2
fi

LOG_DIR_ABS="$(cd "$(dirname "$LOG_DIR")"; pwd)/$(basename "$LOG_DIR")"



cd ../../utility/vid_stab_analysis/

./run_analysis.sh $LOG_DIR_ABS

cd -