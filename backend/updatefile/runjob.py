import schedule
import time
import subprocess,shutil
def job():
	commandjob = "python generate_final_data_report_qmpkp.py"
	subprocess.Popen(commandjob, shell=True).wait()


schedule.every().day.at("04:00").do(job)

while 1:
	schedule.run_pending()
	time.sleep(1)
