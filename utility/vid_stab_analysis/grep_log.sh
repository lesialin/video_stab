LOG_DIR=$1

if [[ $# -ne 1 ]]; then
    echo "Please enter: ./grep_log.sh log_dir"
    exit 2
fi

# if [[ -d "$LOG_DIR/result" ]]
# then
#     # do nothing
#     echo "result directory exist! fine!"
# else
#     echo "result directory not exist, make one!"
#     mkdir -p $LOG_DIR/result
# fi

RESULT_LOG_PATH="${LOG_DIR}/vid_stab.log"
V_CAM_ORIEN_PATH="${LOG_DIR}/v_cam_orien.log"
P_CAM_ORIEN_PATH="${LOG_DIR}/p_cam_orien.log"
OOB_PATH="${LOG_DIR}/out_of_boundary.log"
ALPHA_PATH="${LOG_DIR}/alpha.log"
UNCOMP_DIST_PATH="${LOG_DIR}/uncompensated_dist.log"


grep "v_cam_orien" $RESULT_LOG_PATH | cut -d':' -f2 | sed -e 's/,//g' > $V_CAM_ORIEN_PATH
grep "p_cam_orien" $RESULT_LOG_PATH | cut -d':' -f2 | sed -e 's/,//g' > $P_CAM_ORIEN_PATH
grep "out_of_boundary" $RESULT_LOG_PATH | cut -d'=' -f2  > $OOB_PATH
grep "alpha =" $RESULT_LOG_PATH | cut -d'=' -f2  > $ALPHA_PATH
grep "uncompensated_dist =" $RESULT_LOG_PATH | cut -d'=' -f2  > $UNCOMP_DIST_PATH
