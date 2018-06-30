all:
	#This script will create a new tmux session named 'turtle', start the
	#device code and detach the session to allow it to continue to run
	#after the remote session has ended.
	tmux new-session -d -s turtle
	tmux send-keys 'python main.py' C-m
	tmux detach -s turtle
	#To reattach the session enter 'tmux attach -t turtle'
	#To re-detach the session after attaching it enter
	#CTR-B then "d" while in tmux
