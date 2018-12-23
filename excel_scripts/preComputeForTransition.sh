cat $2/results/test_results_rep_*.csv | grep ^$1 | cut -d ',' -f1,6,7,8,9
