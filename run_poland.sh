set -euo pipefail
IFS=$'\n\t'
rm -rf PolandWeekEndPlots
#rm -rf PolandHotSpotPlots
rm -rf PolandSlipPlots
#rm -rf PolandHotSpotMap
rm -rf PolandWeekendMap
rm -rf PolandSlipMap
rm -rf PolandHotSpotCombo
rm -rf PolandWeekEndCombo
rm -rf PolandSlipCombo

mkdir -p PolandWeekEndPlots
#mkdir -p PolandHotSpotPlots
mkdir -p PolandSlipPlots
#mkdir -p PolandHotSpotMap
mkdir -p PolandWeekendMap
mkdir -p PolandSlipMap
mkdir -p PolandHotSpotCombo
mkdir -p PolandWeekEndCombo
mkdir -p PolandSlipCombo

python weekend_score.py -i poland_animation.pickle -s 2022-02-17 -e 2022-03-28 -o PolandWeekEndPlots --figname poland_week_end_score.png --export_data poland_weekend.csv
#python hot_spot_score.py -i poland_animation.pickle -s 2022-02-14 -e 2022-02-20 -b 2022-02-21 -f 2022-03-10 -o PolandHotSpotPlots --figname poland_hotspot.png --export_data poland_hotspot.csv
python slip_score.py -i poland_animation.pickle -s 2022-02-10 -e 2022-03-10 -o PolandSlipPlots --figname poland_slip_score.png --export_data poland_slip.csv

python add_baseline_to_hotspot.py poland_slip.csv poland_hotspot.csv poland_hotspot_baseline.csv

python plot_precomputed_map.py -i poland_hotspot_baseline.csv --country Poland --outdir PolandHotSpotMap --colorscale -2 2 --cities cities.txt --borders border_crossings.tsv --baseline_cut_off 20
python plot_precomputed_map.py -i poland_weekend.csv --country Poland --outdir PolandWeekendMap --colorscale -2 2 --cities cities.txt --borders border_crossings.tsv --baseline_cut_off 20
python plot_precomputed_map.py -i poland_slip.csv --country Poland --outdir PolandSlipMap --colorscale -.3 .3 --cities cities.txt --borders border_crossings.tsv --colormap bwr --baseline_cut_off 20

python combine_plots.py -a PolandHotSpotMap -b PolandHotSpotPlots -o PolandHotSpotCombo -n 3
python combine_plots.py -a PolandWeekendMap -b PolandWeekEndPlots -o PolandWeekEndCombo -n 3
python combine_plots.py -a PolandSlipMap -b PolandSlipPlots -o PolandSlipCombo -n 3

python trend_plotter.py -i poland_slip.csv --out poland_slip_trends.png --title "Poland Slip Score"
python trend_plotter.py -i poland_hotspot.csv --out poland_hotspot_trends.png --title "Poland Hot Spot Score"
python trend_plotter.py -i poland_weekend.csv --out poland_weekend_trends.png --title "Poland Weekend Score"

python spacially_aware_trends.py -i poland_hotspot_baseline.csv --out poland_hotspot_borders_trends.png --title "Poland Hotspot Score within 5km of Border Crossing" --locs poland_locs.tsv --distance 5 --baseline_cut_off 20
python spacially_aware_trends.py -i poland_hotspot_baseline.csv --out poland_hotspot_Cities_trends.png --title "Poland Hotspot Score within 5km of Major City" --locs cities.txt --distance 5 --pmin -5 --baseline_cut_off 20
python spacially_aware_trends.py -i poland_hotspot_baseline.csv --out poland_hotspot_trends.png --title "Poland Hotspot Score" --locs cities.txt --distance -1 --baseline_cut_off 20

python spacially_aware_trends.py -i poland_slip.csv --out poland_slip_borders_trends.png --title "Poland Slip Score within 5km of Border Crossing" --locs poland_locs.tsv --distance 5 --baseline_cut_off 20
python spacially_aware_trends.py -i poland_slip.csv --out poland_slip_Cities_trends.png --title "Poland Slip Score within 5km of Major City" --locs cities.txt --distance 5 --pmin -5 --baseline_cut_off 20
python spacially_aware_trends.py -i poland_slip.csv --out poland_slip_trends.png --title "Poland Slip Score" --locs cities.txt --distance -1 --baseline_cut_off 20
