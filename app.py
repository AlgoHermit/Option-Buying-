from flask import Flask, render_template, redirect, url_for, request
from time import sleep
import threading
import requests as re
import datetime
import pytz
import strategy


app = Flask(__name__)
thread = False

def keep_alive():
    global thread
    while True:
        if thread == True:          
            thread = False
            break
        r = re.get('https://optbuy.glitch.me') 
        dt_today = datetime.datetime.today()
        dt_India = dt_today.astimezone(pytz.timezone('Asia/Kolkata')) 
        India = (dt_India.strftime('%m/%d/%Y %H:%M'))
        print(India, r)
        sleep(120)


# Login page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user = request.form['nm']
        password = request.form['pwd']

        if user == 'ayham' and password == '1234':
            return redirect(url_for("setup"))
        else:
            return "Invalid credential, <a href='/login'>Try again</a>"
    else:
        return render_template("index.html")
    
# Gathering trade details
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global entry
    if request.method == 'POST':
        typ = request.form['type']
        strategy.ty = typ
        strike = int(request.form['strike'])
        strategy.stk = strike
        entry = float(request.form['entry'])
        strategy.ep = entry
        expiry = request.form['expiry']
        strategy.exp = expiry
        return redirect(url_for("running"))
    else:
        return render_template("setup.html")

# Starting the execution
@app.route('/running')
def running():
    t1 = threading.Thread(target=strategy.begin)
    t2 = threading.Thread(target=keep_alive)
    t1.start()
    t2.start()
    return render_template('stop.html')

@app.route('/stop')
def stop():
    global thread
    strategy.close_thread = True
    thread = True
    return redirect(url_for('setup'))

if __name__  == '__main__':
    app.run(debug = True)