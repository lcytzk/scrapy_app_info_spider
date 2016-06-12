task=$1
echo "task='$task'" > localSetting.py
scrapy crawl $task
