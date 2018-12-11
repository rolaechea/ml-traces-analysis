python LearnWithCrossValidation.py train_conf_460_rep_1.pkl sampled_460_rep_1.pkl > results_460_rep_1.csv
python LearnWithCrossValidation.py train_conf_460_rep_2.pkl sampled_460_rep_2.pkl > results_460_rep_2.csv
python LearnWithCrossValidation.py train_conf_460_rep_3.pkl sampled_460_rep_3.pkl > results_460_rep_3.csv
python LearnWithCrossValidation.py train_conf_460_rep_4.pkl sampled_460_rep_4.pkl > results_460_rep_4.csv
python LearnWithCrossValidation.py train_conf_460_rep_5.pkl sampled_460_rep_5.pkl > results_460_rep_5.csv
python LearnWithCrossValidation.py train_conf_460_rep_6.pkl sampled_460_rep_6.pkl > results_460_rep_6.csv
python LearnWithCrossValidation.py train_conf_460_rep_7.pkl sampled_460_rep_7.pkl > results_460_rep_7.csv
python LearnWithCrossValidation.py train_conf_460_rep_8.pkl sampled_460_rep_8.pkl > results_460_rep_8.csv
python LearnWithCrossValidation.py train_conf_460_rep_9.pkl sampled_460_rep_9.pkl > results_460_rep_9.csv
python LearnWithCrossValidation.py train_conf_460_rep_10.pkl sampled_460_rep_10.pkl > results_460_rep_10.csv
cat results_460_rep_1.csv | cut -d, -f1,91,92 > best_method_460_rep_1.csv
cat results_460_rep_2.csv | cut -d, -f1,91,92 > best_method_460_rep_2.csv
cat results_460_rep_3.csv | cut -d, -f1,91,92 >  best_method_460_rep_3.csv
cat results_460_rep_4.csv | cut -d, -f1,91,92 > best_method_460_rep_4.csv
cat results_460_rep_5.csv | cut -d, -f1,91,92 > best_method_460_rep_5.csv
cat results_460_rep_6.csv | cut -d, -f1,91,92 > best_method_460_rep_6.csv
cat results_460_rep_7.csv | cut -d, -f1,91,92 > best_method_460_rep_7.csv
cat results_460_rep_8.csv | cut -d, -f1,91,92 > best_method_460_rep_8.csv
cat results_460_rep_9.csv | cut -d, -f1,91,92 > best_method_460_rep_9.csv
cat results_460_rep_10.csv | cut -d, -f1,91,92 > best_method_460_rep_10.csv
