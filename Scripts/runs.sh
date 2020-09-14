#Will sort alter-ego interaction by timestamps
function Sort-timestamps(){
  sh ../Alter_Cluster_Sort.sh
}

function reverse-sort-timestamps(){
  sh ../Reverse_Alter_Cluster_Sort.sh
}

#Will Compute new alters from sorted timestamps-data
function New-Alters(){
  nohup python3 alters_count.py -d /home/nabil/results/Alter-cluster-timestamp-sorted/ -o /home/nabil/results/New-Alters/ &
}

#Will Compute leaving alters from sorted timestamps-data
function Leaving-Alters(){
   nohup python3 leaving_count.py -d /home/nabil/results/Alter-cluster-timestamp-reverse-sorted/ -o /home/nabil/results/Leaving-Alters/ &
}

#Will compute peaks depending on duration, thresold, and smoothing
function Age_Peak(){
  nohup python3 ActivityPeriodsAnalysis/activity_periods_analysis.py -d ../../results/Mirror/New-alters/Egos/ --output ../../results/Age-peak/ -du 2 -th 20 -s 1 &
}

