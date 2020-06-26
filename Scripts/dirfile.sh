function move_n_mkdir(){
    for file in /home/nabil/results/Alter-cluster-timestamp-sorted/*; do
        local basefile=$(basename $file)
        dir=${basefile:0:1}
        mkdir -p "$dir" || continue
        mv "$file" "$dir/$basefile"
    done
}

move_n_mkdir

function rename (){
    for file in /home/nabil/results/results/*;
    do
        mv $file "${file#*_}"
    done
}

