for directory in ../../networks/*; do
python3 IO.py -i "$directory" -o ../../output/networks_results -cl 5 -si 3
done
