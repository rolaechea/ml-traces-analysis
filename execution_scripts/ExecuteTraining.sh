python LearnWithCrossValidation.py $1 $2train_conf_rep_1.pkl $2sampled_rep_1.pkl > $3results_rep_1.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_2.pkl $2sampled_rep_2.pkl > $3results_rep_2.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_3.pkl $2sampled_rep_3.pkl > $3results_rep_3.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_4.pkl $2sampled_rep_4.pkl > $3results_rep_4.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_5.pkl $2sampled_rep_5.pkl > $3results_rep_5.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_6.pkl $2sampled_rep_6.pkl > $3results_rep_6.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_7.pkl $2sampled_rep_7.pkl > $3results_rep_7.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_8.pkl $2sampled_rep_8.pkl > $3results_rep_8.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_9.pkl $2sampled_rep_9.pkl > $3results_rep_9.csv
python LearnWithCrossValidation.py $1 $2train_conf_rep_10.pkl $2sampled_rep_10.pkl >  $3results_rep_10.csv
cat $3results_rep_1.csv | cut -d, -f1,91,92 > $3best_method_rep_1.csv
cat $3results_rep_2.csv | cut -d, -f1,91,92 > $3best_method_rep_2.csv
cat $3results_rep_3.csv | cut -d, -f1,91,92 >  $3best_method_rep_3.csv
cat $3results_rep_4.csv | cut -d, -f1,91,92 > $3best_method_rep_4.csv
cat $3results_rep_5.csv | cut -d, -f1,91,92 > $3best_method_rep_5.csv
cat $3results_rep_6.csv | cut -d, -f1,91,92 > $3best_method_rep_6.csv
cat $3results_rep_7.csv | cut -d, -f1,91,92 > $3best_method_rep_7.csv
cat $3results_rep_8.csv | cut -d, -f1,91,92 > $3best_method_rep_8.csv
cat $3results_rep_9.csv | cut -d, -f1,91,92 > $3best_method_rep_9.csv
cat $3results_rep_10.csv | cut -d, -f1,91,92 > $3best_method_rep_10.csv