from flask import Flask, request, jsonify, render_template
import random
import joblib
import os

# Creating an instance of the flask microframework
app = Flask(__name__)

# Loading the pre-trained model
predModel = os.path.join(os.path.dirname(__file__),"model", "processing_model.pkl")
model = joblib.load(predModel)

# Setting all 6 tonality labels
emotions = ["joy", "sadness", "anger", "fear", "love", "surprise"]

# Meme templates object used for extracting images from the memegenAPI
memeTemplates = {
    "joy": [
        "feelsgood", "pigeon", "firsttry", "sohappy",
        "oprah", "money", "success", "agnes", "atis"
    ],
    "anger": [
        "spongebob", "bad", "joker", "imsorry", "stop-it", "trump",
        "patrick", "sparta", "captain", "slap", "because"
    ],
    "sadness": [
        "sad-biden", "sadfrog", "sad-obama", "cryingfloor", "regret",
        "gone", "grumpycat", "hagrid", "noidea", "fwp"
    ],
    "fear": [
        "afraid", "panik-kalm-panik", "cryingfloor", "awkward", "drowning",
        "right", "disastergirl", "noidea", "jetpack", "ackbar"
    ],
    "love": [
        "jim", "pooh", "keanu", "agnes", "dwight",
        "michael-scott", "cmm", "captain-america", "say", "ggg"
    ],
    "surprise": [
        "ams", "bs", "disastergirl", "sarcasticbear",
        "cat", "sk", "scc","hagrid", "gru", "ackbar"
    ]
}

# Meme texts object used for adding funny texts to the images with memegenAPI
memeTexts = {
    "joy": [
        ("How life feels", "When you get that 30L for your project"),
        ("Pure happiness", "Nothing can ruin this"),
        ("Unexpected good vibes", "I'll take it"),
        ("That feeling", "When life finally makes sense"),
        ("Best day ever", "And it's not even noon"),
        ("Smiling for no reason", "Or maybe every reason"),
        ("My happiness level", "Off the charts"),
        ("Just good vibes", "All around"),
        ("Feeling unstoppable", "For once"), 
        
    ],
    "sadness": [
        ("Trying to smile", "But the world said no"),
        ("It's fine", "I'm used to disappointment"),
        ("Crying inside", "Smiling outside"),
        ("Some days just hit different", "In the worst way"),
        ("Fell apart", "But still showed up"),
        ("Mood:", "Blue"),
        ("This too shall pass", "But it's taking forever"),
        ("Me at 3 AM", "Overthinking everything")
    ],
    "anger": [
        ("I'm not mad", "Just disappointed"),
        ("Ughhhhh", "That's the point Giorgina"),
        ("It's not just rage", "It's a lifestyle"),
        ("When they said that", "I lost it"),
        ("I can't even", "With this nonsense"),
        ("When you try to be chill", "But they keep pushing"),
        ("Why does this keep happening?", "WHYYYYYY"),
        ("Holding it in", "Barely"),
        ("The audacity", "Of everything today"),
        ("That's it", "I'm SO done"),
        ("Deep breaths", "Still angry"),
        ("They really said that", "And walked away") 
        
    ],
    "fear": [
        ("Something feels off", "And I'm not okay with it"),
        ("The anxiety is real", "And it brought snacks"),
        ("I'm fine", "This is fine"),
        ("What was that noise?", "I live alone"),
        ("My brain at night", "Let's panic"),
        ("Overthinking everything", "Since always"),
        ("No thoughts", "Just dread"),
        ("Can't sleep", "Monsters under the bed")
    ],
    "love": [
        ("Butterflies again?", "Yeah, it's real"),
        ("This feels right", "But also terrifying"),
        ("It's the little things", "That hit the hardest"),
        ("Smiling at my phone", "Like a fool"),
        ("My heart", "Can't handle this"),
        ("Why am I like this", "In love again"),
        ("Soft hours", "Activated"),
        ("They texted first", "I'm blushing")
    ],
    "surprise": [
        ("Wait, what?", "Did I just get 30L for my project?"),
        ("I didn't see that coming", "At all"),
        ("Plot twist!", "Was not ready for that"),
        ("That moment", "When reality hits weird"),
        ("Well that escalated", "Very quickly"),
        ("Me opening emails", "Shocked and confused"),
        ("Did that just happen?", "Yes, yes it did"),
        ("Suddenly", "Everything changed"),
        ("What a twist", "M. Night would be proud"),
        ("Oh no", "I think it's a trap!")
    ]
}

# A function used to format the texts from the templates to fit the notation 
# suitable for memegenAPI
def formatText(text):
    return text.replace(" ", "_").replace("?", "~q").replace("&", "~a").replace("%", "~p")


# Given an emotion category, randomly pick a meme template and meme text pair from the
# pre-defined objects. Afterwards format the texts and construct the URL for api.memegen.link/images/....
# If something goes wrong along the way, instead of crashing out, the program will use "Buzzlightyear"
# Pixar cartoon character as the default meme image and ("Feeling things", "Emotionally") pair as a 
# default text on that image.
# The function returns a URL link with the meme generated on the website.
def generateMemes(emotion):
    template = random.choice(memeTemplates.get(emotion, ["buzz"]))
    top, bottom = random.choice(memeTexts.get(emotion,  [("Feeling things", "Emotionally")]))
    topUrl = formatText(top)
    bottomUrl = formatText(bottom)
    memeUrl = f"https://api.memegen.link/images/{template}/{topUrl}/{bottomUrl}.png"
    return memeUrl

# The purpose of this routing is to render the structure of the website, i.e. "index.html", including
# its "style.css".
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint to receive JSON payloads containing user text, run the ML model,
# and return the predicted emotion, confidence score, and 5 unique meme URLs.
@app.route("/predict", methods = ["POST"])
def predict():
    # Parsing the JSON body from the request and cleaning the whitespace
    data = request.get_json()
    userInput = data.get("text", "").strip()

    # Error if no input is received
    if not userInput:
        return jsonify({"error" : "No input"}), 400
    
    # Running the model to predict the emotion label as well as getting the confidence estimates
    predEmotion = model.predict([userInput])[0]
    probs = model.predict_proba([userInput])[0]
    confidence = round(100*max(probs), 2)
    
    # A simple error prevention measure in case the model returns a label not defined in our categories
    if predEmotion not in emotions:
        return jsonify({
            "emotion" : predEmotion,
            "message" : "Unknown emotion category"
        }), 400
    
    # Generating 5 unique memes for the predicted emotion
    uniqueMemes = set()
    while len(uniqueMemes) < 5:
        url = generateMemes(predEmotion)
        uniqueMemes.add(url)
    memes = list(uniqueMemes)

    # Returning a JSON file containing usefull information for the UI/UX part of the project
    return jsonify({
        "emotion" : predEmotion,
        "confidence" : confidence,
        "memes" : memes
    })


if __name__ == "__main__":
    app.run(debug=False)