set -euo pipefail
IFS=$'\n\t'
rm -rf CovidWeekEndScorePlots
rm -rf CovidHotSpotPlots
rm -rf CovidSlipScorePlots
rm -rf CovidHotStopMap
rm -rf CovidWeekendMap
rm -rf CovidSlipMap
rm -rf CovidHotSpotScoreCombo
rm -rf CovidSlipScoreCombo
rm -rf CovidWeekEndScoreCombo

mkdir -p CovidWeekEndScorePlots
mkdir -p CovidHotSpotPlots
mkdir -p CovidSlipScorePlots
mkdir -p CovidHotSpotMap
mkdir -p CovidWeekendMap
mkdir -p CovidSlipMap
mkdir -p CovidHotSpotScoreCombo
mkdir -p CovidSlipScoreCombo
mkdir -p CovidWeekEndScoreCombo

python weekend_score.py -i co_covid_animation.pickle -s 2020-03-28 -e 2020-08-30 -o CovidWeekEndScorePlots --figname covid_week_end_score.png --export_data covid_weekend.csv --yrange -1 2 --xrange -1 2
python hot_spot_score.py -i co_covid_animation.pickle -s 2020-03-28 -e 2020-04-03 -b 2020-04-04 -f 2020-08-30 -o CovidHotSpotPlots --figname covid_hotspot.png --export_data covid_hotspot.csv --xrange 0 100
python slip_score.py -i co_covid_animation.pickle -s 2020-03-28 -e 2020-08-30 -o CovidSlipScorePlots --figname covid_slip_score.png --export_data covid_slip.csv

python plot_precomputed_map.py -i covid_hotspot.csv --country Boulder --outdir CovidHotSpotMap --colorscale -10 10 --cities cities.txt --roads boulder_roads.geojson
python plot_precomputed_map.py -i covid_weekend.csv --country Boulder --outdir CovidWeekendMap --colorscale -2 2 --cities cities.txt --roads boulder_roads.geojson
python plot_precomputed_map.py -i covid_slip.csv --country Boulder --outdir CovidSlipMap --colorscale -.3 0.3 --cities cities.txt --roads boulder_roads.geojson --colormap bwr

python combine_plots.py -a CovidHotSpotMap -b CovidHotSpotPlots -o CovidHotSpotScoreCombo -n 3
python combine_plots.py -a CovidSuperHotSpotMap -b CovidHotSpotPlots -o CovidSuperHotSpotScoreCombo -n 3
python combine_plots.py -a CovidSlipMap -b CovidSlipScorePlots -o CovidSlipScoreCombo -n 3
python combine_plots.py -a CovidSlipMap -b CovidSlipScorePlots -o CovidSlipSingleCombo -n 1
python combine_plots.py -a CovidWeekendMap -b CovidWeekEndScorePlots -o CovidWeekEndScoreCombo -n 3

python trend_plotter.py -i covid_slip.csv --out covid_slip_trends.png --title "COVID Slip Score" --na_ok
python trend_plotter.py -i covid_hotspot.csv --out covid_hotspot_trends.png --title "COVID Hotspot Score" --na_ok
python trend_plotter.py -i covid_weekend.csv --out covid_weekend_trends.png --title "COVID Weekend Score" --na_ok

python covid_cases_plot.py --cases boulder_covid_cases.tsv --hotspot covid_hotspot.csv --slip covid_slip.csv --weekend covid_weekend.csv --output four_panel_covid.png --start 2020-03-28 --end 2020-08-11
