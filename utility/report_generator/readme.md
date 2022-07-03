# Report Generator

This repo is to generate power point report of _vid_stab_ result.

**usage**
`python gen_report.py dataset_dir experiment_prefix ppt_title ppt_subtitle`

you may have _dataset_dir_ like,

```
/home/lesia/sf_vid_stab/dataset/vivo/

├── 20200414_log01
├── 20200414_log02
├── 20200414_log04
├── 20200414_log05
├── 20200417_log03
├── 20200417_log04
├── 20200417_log05
├── 20200512_log01
├── 20200512_log02
├── 20200512_log03
├── 20200512_log04
├── 20200512_log05
├── 20200512_log07
├── 20200512_log08
├── 20200512_log09
├── 20200512_log10
├── 20200512_log11
├── 20200512_log12
├── 20200512_log13
├── 20200526_log01
├── 20200526_log02
├── 20200526_log03
├── 20200526_log04
├── 20200526_log05


```

for example I would like to generate a report of 20200512_xxx

so the _experiment_prefix_ is `20200512`

_ppt_title_ is the title  in the first page of the report

and also the report name is _ppt_title_

_ppt_subtile is the subtitle in the first page of the report

ex. 

`python gen_report.py /home/lesia/sf_vid_stab/dataset/vivo/ 20200512 20200528_experiment_result  lesialin`

then you will have a 20200528_experiment_result.pptx in `/home/lesia/sf_vid_stab/dataset/vivo/`
