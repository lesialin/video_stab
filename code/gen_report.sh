PPT_TITLE=20200528_experiment.pptx
PPT_SUBTITLE=LesiaLin
DATASETDIR=/home/lesia/sf_vid_stab/dataset/vivo/
EXPERIMENT_PREFIX=20200512_log

cd ../../utility/report_generator/

python3 gen_report.py $DATASETDIR $EXPERIMENT_PREFIX $PPT_TITLE $PPT_SUBTITLE