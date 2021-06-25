WID=`xdotool search --class gwenview`
xdotool windowactivate $WID

watch -n 5 'Rscript plotGeneratorEvl.r; xdotool key F5'
