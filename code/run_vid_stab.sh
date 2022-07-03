LOG_DIR=$1

if [[ $# -ne 1 ]]; then
    echo "Please enter: ./run_vid_stab.sh log_dir"
    exit 2
fi

RESULT_LOG_PATH="${LOG_DIR}/vid_stab.log"

python3 run_vid_stab.py $LOG_DIR > $RESULT_LOG_PATH

cd ../../utility/vid_stab_analysis/

./run_analysis.sh $LOG_DIR

cd -

cd ../../utility/filter_evaluation

python3 run_evaluation.py $LOG_DIR


cd -