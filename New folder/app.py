from flask import Flask, render_template, request, redirect, url_for,flash,session
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["heart_disease_db"]
collection = db["heart_disease_data"]
users_collection = db["users"]

# Load data (replace with your data path)
data = pd.read_csv("heart_disease.csv")

# Feature columns and target variable
features = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
target = "target"

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2)

# Train a simple logistic regression model (replace with a more complex model if needed)
model = LogisticRegression()
model.fit(X_train, y_train)


@app.route("/")
def index():
    return render_template("signup.html")


@app.route('/home')
def home():
    if "user" not in session:
        
        return redirect(url_for("login"))

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials.")
            return redirect(url_for("login"))
        session["user"] = username
        flash("Logged in successfully!")
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        phone = request.form.get("phone")

        user = users_collection.find_one({"username": username})

        if user:
            flash("Username already exists.")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password)
        users_collection.insert_one({
            "username": username,
            "password": password_hash,
            "phone": phone
        })

        flash("Account created successfully!")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Extract data from form submission
    age = int(request.form["age"])
    sex = int(request.form["sex"])
    chest_pain_type = 23
    trestbps = int(request.form["trestbps"])
    chol = int(request.form["chol"])
    fbs = int(request.form["fbs"])
    restecg = int(request.form["restecg"])
    thalach = int(request.form["thalach"])
    exang = int(request.form["exang"])
    oldpeak = float(request.form["oldpeak"])
    slope = int(request.form["slope"])
    ca = int(request.form["ca"])
    thal = int(request.form["thal"])

    # Prepare data for prediction
    new_data = pd.DataFrame({
        "age": [age],
        "sex": [sex],
        "cp": [chest_pain_type],
        "trestbps": [trestbps],
        "chol": [chol],
        "fbs": [fbs],
        "restecg": [restecg],
        "thalach": [thalach],
        "exang": [exang],
        "oldpeak": [oldpeak],
        "slope": [slope],
        "ca": [ca],
        "thal": [thal]
    })

    # Make prediction
    prediction = model.predict(new_data)[0]
    result = "Heart Disease" if prediction == 1 else "No Heart Disease"

    # Store prediction data in MongoDB
    prediction_data = {
        "age": age,
        "sex": sex,
        "cp": chest_pain_type,
        "trestbps": trestbps,
        "chol": chol,
        "fbs": fbs,
        "restecg": restecg,
        "thalach": thalach,
        "exang": exang,
        "oldpeak": oldpeak,
        "slope": slope,
        "ca": ca,
        "thal": thal,
        "prediction": result
    }
    collection.insert_one(prediction_data)

    return render_template("result.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
