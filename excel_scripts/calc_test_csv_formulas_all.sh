transitions='4 5 6 7 8 9 10 11 12 13 14 15 18 19 20 21 23 24 25 28 33 34'
index=0
for value in $transitions 
do
   valFormula=$((2+$index*10))
   valEnd=$(($valFormula+9))
   echo '='A$valFormula,'=Average(B'$valFormula':B'$valEnd')','=Average(C'$valFormula':C'$valEnd')','=Average(D'$valFormula':D'$valEnd')','=Average(E'$valFormula':E'$valEnd')'
index=$(($index+1))
done