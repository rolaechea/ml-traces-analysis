transitions='4 5 6 7 8 9 10 11 12 13 14 15 18 19 20 21 23 24 25 28 33 34'

for value in $transitions 

do
    bash excel_scripts/preComputeForTransitionTraining.sh $value $1
done