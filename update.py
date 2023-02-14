import schedule, time
import db, main

#weekly db update for progging
def update_prog_log():
    print("updating prog log, in update")
    db.update_prog_log();

#this is 10:01 because it was written in EST to happen 1 minute after weekly maintenance
schedule.every().tuesday.at("10:01").do(update_prog_log)

print("Update loop running. Waiting for reset.")

while True:
    schedule.run_pending()
    time.sleep(30)