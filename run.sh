cd scripts/invokers || exit
python startup.py 65444:65444 --rebuild
cd ../.. || exit
python -m botts.bot.main