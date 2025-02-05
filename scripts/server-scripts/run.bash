screen -ls | grep -q "train" || screen -dmS train
screen -S train -X stuff "bash /home/chan/server-scripts/train.bash $1\n"