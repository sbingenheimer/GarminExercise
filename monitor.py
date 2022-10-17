import sys
import requests
import time
import smtplib


def monitor (email):
    healthLog = {"Failure": 0, "Recovery": 0}
    lastResCode = 200

    downtime = 0
    
    #indicator that there has been a failure
    failureCheck = 0

    #getting the support email
    for index, elem in enumerate(email):
        if (email[index] == "--support"):
            emailTo = email[index+1]

    #test email I created to send out the alerts
    emailFrom = "tmonitorapp@gmail.com"
    password = "ktpmxuszltyvpnqx" #should be a secret, but for sake of excersize its hardcoded.


    while(1):
       
        #api call and getting data
        x = requests.get(url = "https://api.qa.fitpay.ninja/health")
        resCode = 0
        data = x.json()
        status = data['status']

        #calculate downtime of the api
        if (resCode != 200):
            start = time.time()
        if (resCode == 200 and failureCheck == 1):
            end = time.time()
            downtime = end - start
            end = 0
            start = 0
        
        #msgs to send when needed
        fEmailMsg = f"There has been two failures in a row to reach the Garmin Pay health API.\nThe return results were a code of {resCode} with a status of {status}.\nA new email will be sent when a successful connection to the API is collected."
        rEmailMsg = f"There has been two successful connections to the Garmin Pay health API since it has been down.\nThe APIs are now healthy again.\nThe downtime was approximatley {downtime}"

        #failure case
        if (lastResCode != 200 and resCode != 200):
            #update log
            healthLog['Failure'] = healthLog['Failure'] + 1
            #set the failure
            failureCheck = 1
            #send the email
            subject = 'Failure to connect to Germin Pay health API'
            body = fEmailMsg

            email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (emailFrom, ", ".join(emailTo), subject, body)
            try:
                smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                smtp_server.starttls()
                smtp_server.login(emailFrom, password)
                smtp_server.sendmail(emailFrom, emailTo, email_text)
                smtp_server.quit()
                print("Email sent successfully")
            except Exception as ex:
                print ("Error while sending the email: ",ex)

        #recovery case
        if (failureCheck == 1 and resCode == 200 and lastResCode == 200):
            #update the log 
            healthLog['Recovery'] = healthLog['Recovery'] + 1
            #set the fail check back to 0
            failureCheck = 0

            #send email
            subject = 'Connection has been restored to the Garmin Pay health API'
            body = rEmailMsg

            email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (emailFrom, ", ".join(emailTo), subject, body)
            try:
                smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                smtp_server.starttls()
                smtp_server.login(emailFrom, password)
                smtp_server.sendmail(emailFrom, emailTo, email_text)
                smtp_server.quit()
                print("Email sent successfully")
            except Exception as ex:
                print ("Error while sending the email: ",ex)
            
            
        #keep track of last return code from api 
        lastResCode = resCode
        
        #wait 10 min before running again
        time.sleep(600)



if __name__ == "__main__":
    monitor(sys.argv)