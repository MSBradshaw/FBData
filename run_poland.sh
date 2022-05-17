
echo "weekend"
python weekend_score.py -i poland_animation.pickle -s 2022-02-14 -e 2022-03-28 -o WeekEndScorePlots --figname poland_week_end_score.png --export_data poland_weekend.csv
echo "hotspot"
python hot_spot_score.py -i poland_animation.pickle -s 2022-02-14 -e 2022-02-20 -b 2022-02-21 -f 2022-03-10 -o HotSpotPlots --figname poland_hotspot.png --export_data poland_hotspot.csv
echo "slip"
python slip_score.py -i poland_animation.pickle -s 2022-01-14 -e 2022-03-10 -o SlipScorePlots --figname poland_slip_score.png --export_data poland_slip.csv
# mapping
echo "mapping hotspot"
python plot_precomputed_map.py -i poland_hotspot.csv --country Poland --outdir PolandZScoreFigsHotStop --colorscale -10 10 --cities cities.txt --roads europe-road.geojson --borders border_crossings.tsv
echo "mapping weekend"
python plot_precomputed_map.py -i poland_weekend.csv --country Poland --outdir PolandZScoreFigsWeekend --colorscale -10 10 --cities cities.txt --roads europe-road.geojson --borders border_crossings.tsv
echo "mapping slip"
python plot_precomputed_map.py -i poland_slip.csv --country Poland --outdir PolandZScoreFigsSlip --colorscale -10 10 --cities cities.txt --roads europe-road.geojson --borders border_crossings.tsv


