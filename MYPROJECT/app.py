from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
from prediction import predict_result
import yagmail


app = Flask(__name__)
app.secret_key = "cropYield"


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["email"] == str(email) and row["password"] == str(pwd):
                session['email'] = email
                return redirect(url_for('prediction'))
        else:
            msg = 'Invalid Login Try Again'
            return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['Email']
        password = request.form['Password']
        col_list = ["name", "email", "password"]
        r1 = pd.read_excel('user.xlsx', usecols=col_list)
        if str(email).lower() not in r1['email'].values.tolist():
            new_row = {'name': name, 'email': str(email).lower(), 'password': password}
            r1 = r1.append(new_row, ignore_index=True)
            r1.to_excel('user.xlsx', index=False)
            print("Records created successfully")
        else:
            msg="Email already exist. Create Account with New Email."
            return render_template('register.html', msg=msg)
        # msg = 'Entered Mail ID Already Existed'
        msg = 'Registration Successfull !! U Can login Here !!!'
        return render_template('login.html', msg=msg)
    return render_template('register.html')


@app.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'POST':
        try:
            email = request.form['email']
            current_password = request.form['current']
            new_password = request.form['new']
            confirm_password = request.form['verify']

            df = pd.read_excel('user.xlsx')

            user_row = df[(df['email'] == email) & (
                df['password'] == current_password)]

            if not user_row.empty:
                if new_password == confirm_password:
                    df.loc[user_row.index, 'password'] = new_password
                    df.to_excel('user.xlsx', index=False)
                    return render_template('password_change.html', msg='Password changed successfully.')
                else:
                    return render_template('password_change.html', msg='New password and confirmation password do not match.')
            else:
                return render_template('password_change.html', msg='Invalid email or password. Please try again.')

        except KeyError as e:
            return render_template('password_change.html', msg='Required form field is missing: {}'.format(e))

    return render_template('password_change.html')


def sendmail(result, prob, user_mails):  
    try:
        yag = yagmail.SMTP(user='santhoshreddyg2002@gmail.com', password='wursfcwqxewxffgl')
        for user_mail in [user_mails]:
            mail_contents = [f"\n \n {result} is being Detected with {prob} probability score. \n \n"]
            yag.send(to=user_mail, subject="Crop Yield Prediction",
                     contents=mail_contents)  # Use video_path_ here

        print('[SUCCESS]  > Email sent successfully...')
        return "success"
    except Exception as e:
        print('[FAILED]    >', e)
        return "failed"
    

state_dict = {'Andaman and Nicobar': 0, 'Andhra Pradesh': 1, 'Assam': 2, 'Chattisgarh': 3, 'Goa': 4, 'Gujarat': 5, 'Haryana': 6, 'Himachal Pradesh': 7, 'Jammu and Kashmir': 8, 'Karnataka': 9, 'Kerala': 10, 'Madhya Pradesh': 11,
              'Maharashtra': 12, 'Manipur': 13, 'Meghalaya': 14, 'Nagaland': 15, 'Odisha': 16, 'Pondicherry': 17, 'Punjab': 18, 'Rajasthan': 19, 'Tamil Nadu': 20, 'Telangana': 21, 'Tripura': 22, 'Uttar Pradesh': 23, 'Uttrakhand': 24, 'West Bengal': 25}

crop_dict = {'Apple': 0, 'Banana': 1, 'Blackgram': 2, 'ChickPea': 3, 'Coconut': 4, 'Coffee': 5, 'Cotton': 6, 'Grapes': 7, 'Jute': 8, 'KidneyBeans': 9, 'Lentil': 10,
             'Maize': 11, 'Mango': 12, 'MothBeans': 13, 'MungBean': 14, 'Muskmelon': 15, 'Orange': 16, 'Papaya': 17, 'PigeonPeas': 18, 'Pomegranate': 19, 'Rice': 20, 'Watermelon': 21}


@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    return render_template("prediction.html", state_dict=state_dict, crop_dict=crop_dict)


@app.route('/predict', methods=['POST'])
def predict():
    email_id = session['email']

    ui = []

    if request.method == 'POST':
        ui.append(float(request.form['q1']))
        ui.append(float(request.form['q2']))
        ui.append(float(request.form['q3']))
        ui.append(float(request.form['q4']))
        ui.append(float(request.form['q5']))
        ui.append(float(request.form['q6']))
        ui.append(float(request.form['q7']))
        ui.append(int(request.form['q8']))
        ui.append(float(request.form['q9']))
        ui.append(int(request.form['q10']))

        print("ui : ", ui)

        cl, prob = predict_result([ui])

        mail = sendmail(cl, prob, user_mails=email_id)

        if mail == "success":
            msg = "File sent to " + email_id
        else:
            msg = "Oops!! File sending failed to " + email_id

        return render_template('result.html', cl=cl, prob=prob)


@app.route('/graph', methods=['POST', 'GET'])
def graph():
    try:
        if request.method == 'POST':
            graph_name = request.form['text']
            graph = ''
            name = ''

            if graph_name == "k_cr":            
                model_name = "K Neighbors Classifier Model"
                name = "Classification Report"
                graph = "static/graphs/k_cr.png"
            elif graph_name == 'k_cm':
                model_name = "K Neighbors Classifier Model"
                name = "Confusion Matrix"
                graph = "static/graphs/k_cm.png"
            elif graph_name == 'r_cr':
                model_name = "Random Forest Classifier Model"
                name = "Classification Report"
                graph = "static/graphs/r_cr.png"
            elif graph_name == 'r_cm':
                model_name = "Random Forest Classifier Model"
                name = "Confusion Matrix"
                graph = "static/graphs/r_cm.png"
            elif graph_name == 'comp':
                model_name = " K Neighbors Classifier Model vs Random Forest Classifier Model"
                name = "Models Comparision Plot Graph"
                graph = "static/graphs/comp.png"

            return render_template('graphs.html', mn=model_name, name=name, graph=graph)
    except Exception as e:
         msg = "Select the Graph."
         return render_template('graphs.html', msg=msg)
    
    
@app.route('/graphs', methods=['POST', 'GET'])
def graphs():
    return render_template('graphs.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5549, debug=True)
