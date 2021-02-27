# slackapp

slack app for testing bolt framework and getting started with stack responses 

pre-requisites:
* https://ngrok.com/download

```
# venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# credentials
export =*****
export =*****

# start ngrok
./ngrok authtoken <your_auth_token>
./ngrok http 3000

    ngrok by @inconshreveable                                                                                                                                                                          (Ctrl+C to quit)
                                                                                                                                                                                                                       
    Session Status                online                                                                                                                                                                               
    Account                       eduardomcerqueira@gmail.com (Plan: Free)                                                                                                                                             
    Version                       2.3.35                                                                                                                                                                               
    Region                        United States (us)                                                                                                                                                                   
    Web Interface                 http://127.0.0.1:4040                                                                                                                                                                
    Forwarding                    http://ebe0e3965fcf.ngrok.io -> http://localhost:3000                                                                                                                                
    Forwarding                    https://ebe0e3965fcf.ngrok.io -> http://localhost:3000                                                                                                                               
                                                                                                                                                                                                                       
    Connections                   ttl     opn     rt1     rt5     p50     p90                                                                                                                                          

                                  0       0       0.00    0.00    0.00    0.00          
```
update REQUEST_URL https://api.slack.com/apps/A01PHET4R1B/event-subscriptions? with ngrok forwarding https URL 



### TODO

#### basic app
1. integrate ngrok as part of the app https://pypi.org/project/pyngrok/ and https://pyngrok.readthedocs.io/en/latest/
1. 

#### refactoring
1. re-build with OO
1. providers must be extendable
1. authentication 
1. database ( analytical, history, reports )
1. containerized

#### providers
1. Openstack
    1. keystone authentication with API TOKEN
1. Openshift
1. AWS EC2