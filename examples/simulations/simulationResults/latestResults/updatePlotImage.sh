WID=`xdotool search --name .png`
xdotool windowactivate $WID

watch -n 2 'Rscript plotGeneratorEvl.r; xdotool key F5'
